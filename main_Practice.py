from fastapi import FastAPI, Request, Form, UploadFile, File, Body, status
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import pymysql
from datetime import datetime, timedelta
import os
from tempfile import NamedTemporaryFile
import pandas as pd
from menu_generator import IndianMenuGenerator
from pydantic import BaseModel
import json
import joblib
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Optional, Dict, Any
from fastapi import Depends
from fastapi import APIRouter
import httpx

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="super_secret_key")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Database connection helper (sync for now)
def get_mysql_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='Ravindra@140',
        db='rafeedo',
        cursorclass=pymysql.cursors.Cursor
    )

generator = IndianMenuGenerator()

# Load the Pax ML model at startup
PAX_MODEL_PATH = os.path.join('Pax ML', 'backend', 'pax_predictor.pkl')
try:
    pax_ml_bundle = joblib.load(PAX_MODEL_PATH)
    pax_ml_model = pax_ml_bundle['model']
    pax_ml_columns = pax_ml_bundle['columns']
    # If you need unique_dish_df or pax_long, you can get them from pax_ml_bundle
except Exception as e:
    pax_ml_model = None
    pax_ml_columns = []
    print(f"[ERROR] Could not load Pax ML model: {e}")

# --- Pax ML Settings DB (SQLite) ---
PAX_DB_PATH = os.path.join(os.path.dirname(__file__), 'pax_settings.db')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{PAX_DB_PATH}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BatchSetting(Base):
    __tablename__ = 'batch_settings'
    id = Column(Integer, primary_key=True, index=True)
    batch_name = Column(String, unique=True, index=True)
    total_count = Column(Integer)
    weekend_stay_percent = Column(Float)

class ExamRule(Base):
    __tablename__ = 'exam_rules'
    id = Column(Integer, primary_key=True, index=True)
    exam_time = Column(String)
    meal = Column(String)
    reduction_percent = Column(Float)

class ExamDate(Base):
    __tablename__ = 'exam_dates'
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    exam_time = Column(String)

# Create tables if not exist
Base.metadata.create_all(bind=engine)

def get_pax_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UpdateMenuItemRequest(BaseModel):
    category: str
    subcat: str
    oldValue: str
    newValue: str
    date: str

class DeleteMenuItemRequest(BaseModel):
    category: str
    subcat: str
    value: str
    date: str

class AddMenuItemRequest(BaseModel):
    category: str
    subcat: str
    value: str
    date: str

class IngredientData(BaseModel):
    name: str
    quantity: float
    unit: str

class AddDishRequest(BaseModel):
    dish_name: str
    category: str
    ingredients: list[IngredientData]

class UpdateDishRequest(BaseModel):
    original_dish_name: str
    updated_dish_name: str
    updated_category: str
    ingredients: list[IngredientData]

class DeleteDishRequest(BaseModel):
    dish_name_to_delete: str

# Helper for BOM DB connection

def get_bom_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='Ravindra@140',
        db='bom',
        cursorclass=pymysql.cursors.Cursor
    )

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/login")
async def login_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "message": None})

@app.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = get_mysql_connection()
    cur = conn.cursor()
    try:
        # Log the login attempt (before verification)
        cur.execute(
            "INSERT INTO user_logins (username, password, login_time, success) VALUES (%s, %s, %s, %s)",
            (username, password, datetime.now(), False)
        )
        conn.commit()
        # Verify credentials
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        if user:
            # Update the login attempt to successful
            cur.execute("UPDATE user_logins SET success = TRUE WHERE id = LAST_INSERT_ID()")
            conn.commit()
            # Store user info in session
            request.session['user_id'] = user[0]
            request.session['username'] = user[1]
            return RedirectResponse(url="/menu", status_code=303)
        else:
            message = 'Invalid credentials'
            return templates.TemplateResponse("form.html", {"request": request, "message": message})
    except Exception as e:
        conn.rollback()
        message = 'Database error occurred'
        return templates.TemplateResponse("form.html", {"request": request, "message": message})
    finally:
        cur.close()
        conn.close()

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/dashboard")
async def dashboard(request: Request):
    if not request.session.get('user_id'):
        message = 'Please log in to access the dashboard.'
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("dashboard.html", {"request": request, "active_page": "dashboard"})

@app.get("/form")
async def form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.get("/menu")
async def menu_get(request: Request):
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("menu.html", {"request": request, "active_page": "menu"})

@app.post("/menu")
async def menu_post(request: Request):
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    # Call the generate_menu logic here (to be implemented)
    # For now, just render the menu page
    return templates.TemplateResponse("menu.html", {"request": request, "active_page": "menu"})

@app.get("/studentstaff")
async def studentstaff(request: Request):
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("studentstaff.html", {"request": request, "active_page": "studentstaff"})

@app.get("/supplier")
async def supplier(request: Request):
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("supplier.html", {"request": request, "active_page": "supplier"})

@app.get("/analytics")
async def analytics(request: Request):
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("analytics.html", {"request": request, "active_page": "analytics"})

@app.get("/index")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/pax")
async def pax(request: Request):
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("pax.html", {"request": request, "active_page": "pax"})

@app.get("/pax_settings")
async def pax_settings(request: Request):
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("pax_settings.html", {"request": request, "active_page": "pax_settings"})

@app.get("/settings")
async def settings(request: Request):
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    dishes = []
    conn = None
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='Ravindra@140',
            db='bom',
            cursorclass=pymysql.cursors.Cursor
        )
        cur = conn.cursor()
        cur.execute("SELECT dish_id, Name FROM dishes ORDER BY Name")
        dish_tuples = cur.fetchall()
        dishes = [{
            'dish_id': dish_tuple[0],
            'dish_name': dish_tuple[1]
        } for dish_tuple in dish_tuples]
        cur.close()
    except Exception as e:
        # Optionally log error
        pass
    finally:
        if conn:
            conn.close()
    return templates.TemplateResponse("settings.html", {"request": request, "active_page": "settings", "dishes": dishes})

# Example root endpoint (to be replaced with routers)
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Food Management Website!"}

@app.post("/generate")
async def generate_menu(request: Request):
    form = await request.form()
    start_date = form.get('start_date', '')
    end_date = form.get('end_date', '')
    error = None
    menu = None
    try:
        # Validate and format start and end dates
        if not start_date or not end_date:
            error = 'Both start and end dates are required'
            return templates.TemplateResponse("menu.html", {"request": request, "error": error})
        try:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                start_dt = datetime.strptime(start_date, '%d-%m-%Y')
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                end_dt = datetime.strptime(end_date, '%d-%m-%Y')
        except ValueError:
            error = 'Invalid date format. Use YYYY-MM-DD or DD-MM-YYYY'
            return templates.TemplateResponse("menu.html", {"request": request, "error": error})
        days = (end_dt - start_dt).days + 1
        if days <= 0:
            error = 'End date must be after or equal to start date'
            return templates.TemplateResponse("menu.html", {"request": request, "error": error})
        df = generator.menu_data.copy()
        df['Day'] = df['Day'].astype(str).str.strip().str.capitalize()
        df['Meal Type'] = df['Meal Type'].astype(str).str.strip().str.capitalize()
        df['Date'] = df['Date'].astype(str).str.strip()
        meal_types = ['Breakfast', 'Lunch', 'Snacks', 'Dinner', 'Brunch']
        menu = {}
        current_date = start_dt
        for _ in range(days):
            day_name = current_date.strftime('%A')
            day_menu = {}
            if day_name == 'Sunday':
                meal_categories = ['Brunch', 'Snacks', 'Dinner']
            else:
                meal_categories = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
            for meal_type in meal_categories:
                candidates = df[(df['Day'] == day_name) & (df['Meal Type'] == meal_type)]
                if not candidates.empty:
                    row = candidates.sample(1).iloc[0]
                    item_cols = [col for col in candidates.columns if col.lower().replace(' ', '').startswith('item')]
                    meal_items = []
                    for col in item_cols:
                        dish = str(row[col]).strip()
                        if dish and dish.lower() != 'nan':
                            meal_items.append(dish)
                    day_menu[meal_type] = meal_items
                else:
                    day_menu[meal_type] = []
            date_str = current_date.strftime('%Y-%m-%d')
            menu[date_str] = {
                'Date': date_str,
                'Day': day_name,
                'Items': day_menu
            }
            current_date += timedelta(days=1)
        # Save menu to database
        if save_menu_to_database(menu):
            pass # Optionally add a success message
        else:
            error = 'Menu generated but failed to save to database!'
        generator.current_menu = menu
        return templates.TemplateResponse("menu.html", {"request": request, "menu": menu, "start_date": start_date, "end_date": end_date, "error": error})
    except Exception as e:
        import traceback
        traceback.print_exc()
        error = 'An unexpected error occurred'
        return templates.TemplateResponse("menu.html", {"request": request, "error": error})

@app.get("/bom")
async def bom(request: Request):
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("bom.html", {"request": request, "active_page": "bom"})

@app.get("/bom_database")
async def bom_database(request: Request):
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    dishes_data = []
    conn = None
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='Ravindra@140',
            db='bom',
            cursorclass=pymysql.cursors.Cursor
        )
        cur = conn.cursor()
        cur.execute("SELECT dish_id, Name, Meal_Category FROM dishes ORDER BY Name;")
        dishes = cur.fetchall()
        for dish_id, dish_name, meal_category in dishes:
            cur.execute("""
                SELECT i.ingredient_id, i.Name, di.Serving_per_person, di.Unit_of_measure 
                FROM dish_ingredients di 
                JOIN ingredients i ON di.Ingredient_id = i.Ingredient_id 
                WHERE di.dish_id=%s
            """, (dish_id,))
            ingredients = cur.fetchall()
            ingredients_list = []
            for ing_id, ing_name, serving, unit in ingredients:
                ingredients_list.append({
                    'id': ing_id,
                    'name': ing_name,
                    'serving': serving,
                    'unit': unit
                })
            dishes_data.append({
                'dish_id': dish_id,
                'dish_name': dish_name,
                'meal_category': meal_category,
                'ingredients': ingredients_list
            })
        cur.close()
    except Exception as e:
        pass
    finally:
        if conn:
            conn.close()
    return templates.TemplateResponse("bom_database.html", {"request": request, "active_page": "bom", "dishes_data": dishes_data})

@app.get("/debug_db_schema")
async def debug_db_schema():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='Ravindra@140',
            db='bom',
            cursorclass=pymysql.cursors.Cursor
        )
        cur = conn.cursor()
        cur.execute("DESCRIBE dishes;")
        schema = cur.fetchall()
        cur.close()
        conn.close()
        return {"schema": schema}
    except Exception as e:
        return {"error": str(e)}

def get_menu_from_database(start_date, end_date):
    """Retrieve menu data from MySQL database for given date range"""
    try:
        conn = get_mysql_connection()
        cur = conn.cursor()
        # Convert date strings to MySQL DATE format
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            try:
                start_dt = datetime.strptime(start_date, '%d-%m-%Y').date()
                end_dt = datetime.strptime(end_date, '%d-%m-%Y').date()
            except ValueError:
                return {}
        cur.execute('''
            SELECT id, menu_date, day_name 
            FROM menu_days 
            WHERE menu_date BETWEEN %s AND %s 
            ORDER BY menu_date
        ''', (start_dt, end_dt))
        menu_days = cur.fetchall()
        menu_data = {}
        for menu_day in menu_days:
            menu_day_id, menu_date, day_name = menu_day
            cur.execute('''
                SELECT meal_category, item_category, item_name, item_order
                FROM menu_items 
                WHERE menu_day_id = %s 
                ORDER BY meal_category, item_order
            ''', (menu_day_id,))
            menu_items = cur.fetchall()
            day_menu = {}
            for meal_category, item_category, item_name, item_order in menu_items:
                if meal_category not in day_menu:
                    day_menu[meal_category] = {}
                if item_category not in day_menu[meal_category]:
                    day_menu[meal_category][item_category] = []
                day_menu[meal_category][item_category].append(item_name)
            date_str = menu_date.strftime('%Y-%m-%d')
            menu_data[date_str] = {
                'Date': date_str,
                'Day': day_name,
                'Items': day_menu
            }
        cur.close()
        conn.close()
        return menu_data
    except Exception as e:
        return {}

@app.api_route("/generate_bom", methods=["GET", "POST"])
async def generate_bom(request: Request):
    if request.method == "POST":
        form = await request.form()
        dish = form.get('dish', 'all')
        period = form.get('period', 'week')
        num_students = int(form.get('num_students', 0))
        custom_date = form.get('custom_date')
        today = datetime.today().date()
        if period == 'week':
            start_date = today
            end_date = today + timedelta(days=6)
        elif period == 'month':
            start_date = today.replace(day=1)
            next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
            end_date = next_month - timedelta(days=1)
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        elif period == 'customdate' and custom_date:
            start_date = end_date = datetime.strptime(custom_date, '%Y-%m-%d').date()
        else:
            start_date = today
            end_date = today
        menu_data = get_menu_from_database(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        if not menu_data:
            return templates.TemplateResponse("bom.html", {"request": request, "bom_results": None, "error": "No menu data found for the selected period."})
        flat_menu = flatten_menu_data(menu_data)
        # Dish filter logic (optional, not implemented in original detailed BOM)
        if dish and dish != 'all':
            # Only keep rows where any Dish X matches the selected dish
            flat_menu = [row for row in flat_menu if dish in [row.get(f'Dish {i+1}', '') for i in range(4)]]
        bom_results = calculate_detailed_bom(flat_menu, num_students)
        return templates.TemplateResponse("bom.html", {
            "request": request,
            "bom_results": bom_results['total'],
            "detailed_bom": bom_results['detailed'],
            "num_students": num_students,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "error": None
        })
    return templates.TemplateResponse("bom.html", {"request": request, "bom_results": None, "error": None})

@app.post("/generate_bom_from_menu")
async def generate_bom_from_menu(request: Request):
    form = await request.form()
    num_students = int(form.get('num_students', 0))
    error = None
    menu_data = getattr(generator, 'current_menu', None)
    if not menu_data:
        # Fallback: try to get menu from DB for the last 7 days
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=6)
        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')
        # Use the same DB logic as in save_menu_to_database
        try:
            conn = get_mysql_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT id, menu_date, day_name 
                FROM menu_days 
                WHERE menu_date BETWEEN %s AND %s 
                ORDER BY menu_date
            ''', (from_date, to_date))
            menu_days = cur.fetchall()
            menu_data = {}
            for menu_day in menu_days:
                menu_day_id, menu_date, day_name = menu_day
                cur.execute('''
                    SELECT meal_category, item_category, item_name, item_order
                    FROM menu_items 
                    WHERE menu_day_id = %s 
                    ORDER BY meal_category, item_order
                ''', (menu_day_id,))
                menu_items = cur.fetchall()
                day_menu = {}
                for meal_category, item_category, item_name, item_order in menu_items:
                    if meal_category not in day_menu:
                        day_menu[meal_category] = {}
                    if item_category not in day_menu[meal_category]:
                        day_menu[meal_category][item_category] = []
                    day_menu[meal_category][item_category].append(item_name)
                date_str = menu_date.strftime('%Y-%m-%d')
                menu_data[date_str] = {
                    'Date': date_str,
                    'Day': day_name,
                    'Items': day_menu
                }
            cur.close()
            conn.close()
        except Exception as e:
            error = 'No menu data found. Please generate a menu first.'
            menu_data = None
    if not menu_data:
        return templates.TemplateResponse("bom_results.html", {
            "request": request,
            "bom_results": None,
            "detailed_bom": None,
            "num_students": num_students,
            "menu_data": None,
            "error": error or 'No menu data found.'
        })
    flat_menu = flatten_menu_data(menu_data)
    bom_results = calculate_detailed_bom(flat_menu, num_students)
    return templates.TemplateResponse("bom_results.html", {
        "request": request,
        "bom_results": bom_results['total'],
        "detailed_bom": bom_results['detailed'],
        "num_students": num_students,
        "menu_data": menu_data,
        "error": error
    })

@app.post("/upload_and_calculate_bom")
async def upload_and_calculate_bom(request: Request, excel_file: UploadFile = File(...), num_students: int = Form(...)):
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    if not excel_file:
        return RedirectResponse(url="/dashboard", status_code=303)
    if not (excel_file.filename.endswith('.xlsx') or excel_file.filename.endswith('.xls')):
        return RedirectResponse(url="/dashboard", status_code=303)
    if num_students <= 0:
        return RedirectResponse(url="/dashboard", status_code=303)
    # Save uploaded file to a temp file
    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(excel_file.filename)[1]) as tmp:
        content = await excel_file.read()
        tmp.write(content)
        tmp_path = tmp.name
    df = pd.read_excel(tmp_path)
    os.remove(tmp_path)
    # Prepare data in a format suitable for calculate_detailed_bom
    required_cols = ['Day', 'Meal Type']
    if not all(col in df.columns for col in required_cols):
        return RedirectResponse(url="/dashboard", status_code=303)
    excel_item_cols = [col for col in df.columns if col.startswith('Item') and len(col) == 5 and col[4].isdigit()]
    excel_item_cols.sort()
    flat_menu_from_upload = []
    for index, row in df.iterrows():
        row_dict = {
            'Day': row['Day'],
            'Meal Type': row['Meal Type']
        }
        for i in range(4):
            dish_col_name = f'Dish {i+1}'
            item_col_in_excel = excel_item_cols[i] if i < len(excel_item_cols) else None
            if item_col_in_excel and pd.notna(row[item_col_in_excel]):
                row_dict[dish_col_name] = str(row[item_col_in_excel])
            else:
                row_dict[dish_col_name] = ''
        flat_menu_from_upload.append(row_dict)
    bom_results = calculate_detailed_bom(flat_menu_from_upload, num_students)
    # For menu_data to pass to bom_results.html, create a summary from the uploaded excel
    uploaded_menu_summary = {}
    for _, row in df.iterrows():
        day = row['Day']
        meal_type = row['Meal Type']
        if day not in uploaded_menu_summary:
            uploaded_menu_summary[day] = {'Day': day, 'Items': {}}
        if meal_type not in uploaded_menu_summary[day]['Items']:
            uploaded_menu_summary[day]['Items'][meal_type] = {}
        category_key = 'Dishes'
        if category_key not in uploaded_menu_summary[day]['Items'][meal_type]:
            uploaded_menu_summary[day]['Items'][meal_type][category_key] = []
        for col in excel_item_cols:
            if pd.notna(row[col]):
                uploaded_menu_summary[day]['Items'][meal_type][category_key].append(row[col])
    return templates.TemplateResponse("bom_results.html", {
        "request": request,
        "bom_results": bom_results['total'],
        "detailed_bom": bom_results['detailed'],
        "num_students": num_students,
        "menu_data": uploaded_menu_summary
    })

@app.get("/get_dish_details/{dish_name}")
async def get_dish_details(dish_name: str):
    conn = None
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='Ravindra@140',
            db='bom',
            cursorclass=pymysql.cursors.Cursor
        )
        cur = conn.cursor()
        cur.execute("SELECT dish_id, Name, Meal_Category FROM dishes WHERE TRIM(LOWER(Name)) = TRIM(LOWER(%s))", (dish_name,))
        dish = cur.fetchone()
        if not dish:
            return {"error": "Dish not found"}
        dish_id, fetched_dish_name, category = dish
        cur.execute("SELECT i.ingredient_id, i.Name, di.Serving_per_person, di.Unit_of_measure FROM dish_ingredients di JOIN ingredients i ON di.Ingredient_id = i.Ingredient_id WHERE di.dish_id = %s", (dish_id,))
        ingredients = cur.fetchall()
        ingredients_list = []
        for ing_id, ing_name, serving, unit in ingredients:
            ingredients_list.append({
                'id': ing_id,
                'name': ing_name,
                'serving': serving,
                'unit': unit
            })
        return {
            'dish_id': dish_id,
            'dish_name': fetched_dish_name,
            'category': category,
            'ingredients': ingredients_list
        }
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}
    finally:
        if conn:
            conn.close()

def create_tables():
    # Main DB
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Ravindra@140',
        db='rafeedo',
        cursorclass=pymysql.cursors.Cursor
    )
    try:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user_logins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(255) NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT FALSE
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS dishes (
                dish_id VARCHAR(10) PRIMARY KEY,
                dish_name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS menu_variations (
                variation_id INT AUTO_INCREMENT PRIMARY KEY,
                variation_name VARCHAR(100) NOT NULL,
                week_number INT NOT NULL,
                year INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('Draft', 'Active', 'Archived') DEFAULT 'Draft',
                UNIQUE KEY unique_week_year (week_number, year)
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS menu_days (
                id INT AUTO_INCREMENT PRIMARY KEY,
                menu_date DATE NOT NULL,
                day_name VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_menu_date (menu_date)
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                menu_day_id INT NOT NULL,
                meal_category VARCHAR(50) NOT NULL,
                item_category VARCHAR(100) NOT NULL,
                item_name VARCHAR(255) NOT NULL,
                item_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (menu_day_id) REFERENCES menu_days(id) ON DELETE CASCADE,
                INDEX idx_menu_day_meal (menu_day_id, meal_category)
            )
        ''')
        cur.execute('''
            INSERT INTO users (username, password)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE password = VALUES(password)
        ''', ('admin', 'admin123'))
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cur.close()
        conn.close()

    # BOM DB
    conn_bom = pymysql.connect(
        host='localhost',
        user='root',
        password='Ravindra@140',
        db='bom',
        cursorclass=pymysql.cursors.Cursor
    )
    try:
        cur_bom = conn_bom.cursor()
        cur_bom.execute("SHOW TABLES LIKE 'dishes'")
        dishes_table_exists = cur_bom.fetchone()
        if dishes_table_exists:
            cur_bom.execute("DESCRIBE dishes")
            columns = cur_bom.fetchall()
            expected_columns = ['dish_id', 'Name', 'Meal_Category']
            actual_columns = [col[0] for col in columns]
            # Optionally check schema
        cur_bom.execute("SHOW TABLES LIKE 'ingredients'")
        if cur_bom.fetchone():
            cur_bom.execute("DESCRIBE ingredients")
        cur_bom.execute("SHOW TABLES LIKE 'dish_ingredients'")
        if cur_bom.fetchone():
            cur_bom.execute("DESCRIBE dish_ingredients")
        conn_bom.commit()
    except Exception as e:
        conn_bom.rollback()
    finally:
        cur_bom.close()
        conn_bom.close()

def save_menu_to_database(menu_data):
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='Ravindra@140',
            db='rafeedo',
            cursorclass=pymysql.cursors.Cursor
        )
        cur = conn.cursor()
        for date_str, day_data in menu_data.items():
            try:
                menu_date = datetime.strptime(date_str, '%d-%b-%Y').date()
            except ValueError:
                continue
            day_name = day_data['Day']
            cur.execute('''
                INSERT INTO menu_days (menu_date, day_name) 
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE day_name = VALUES(day_name)
            ''', (menu_date, day_name))
            menu_day_id = cur.lastrowid if cur.lastrowid else None
            if not menu_day_id:
                cur.execute('SELECT id FROM menu_days WHERE menu_date = %s', (menu_date,))
                menu_day_id = cur.fetchone()[0]
            cur.execute('DELETE FROM menu_items WHERE menu_day_id = %s', (menu_day_id,))
            item_order = 0
            for meal_category, meal_data in day_data['Items'].items():
                if isinstance(meal_data, dict):
                    for item_category, items in meal_data.items():
                        if isinstance(items, list):
                            for item in items:
                                item_order += 1
                                cur.execute('''
                                    INSERT INTO menu_items 
                                    (menu_day_id, meal_category, item_category, item_name, item_order)
                                    VALUES (%s, %s, %s, %s, %s)
                                ''', (menu_day_id, meal_category, item_category, item, item_order))
                elif isinstance(meal_data, list):
                    for item in meal_data:
                        item_order += 1
                        cur.execute('''
                            INSERT INTO menu_items 
                            (menu_day_id, meal_category, item_category, item_name, item_order)
                            VALUES (%s, %s, %s, %s, %s)
                        ''', (menu_day_id, meal_category, meal_category, item, item_order))
        conn.commit()
        return True
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.on_event("startup")
def startup_event():
    create_tables()
    global generator
    generator.prepare_data('Final Menu Modified.xlsx')

@app.post("/update_menu_item")
async def update_menu_item(request: UpdateMenuItemRequest):
    try:
        category = request.category
        subcat = request.subcat
        old_value = request.oldValue
        new_value = request.newValue
        date = request.date
        try:
            menu_date = datetime.strptime(date, '%d-%b-%Y').date()
        except ValueError:
            return JSONResponse({'error': 'Invalid date format'}, status_code=400)
        conn = get_mysql_connection()
        cur = conn.cursor()
        try:
            cur.execute('SELECT id FROM menu_days WHERE menu_date = %s', (menu_date,))
            result = cur.fetchone()
            if not result:
                return JSONResponse({'error': 'Date not found in menu'}, status_code=404)
            menu_day_id = result[0]
            cur.execute('''
                UPDATE menu_items 
                SET item_name = %s 
                WHERE menu_day_id = %s AND meal_category = %s AND item_category = %s AND item_name = %s
            ''', (new_value, menu_day_id, category, subcat, old_value))
            if cur.rowcount > 0:
                conn.commit()
                menu = getattr(generator, 'current_menu', None)
                if menu and date in menu:
                    day_menu = menu[date]
                    if (category in day_menu['Items'] and 
                        subcat in day_menu['Items'][category] and 
                        old_value in day_menu['Items'][category][subcat]):
                        index = day_menu['Items'][category][subcat].index(old_value)
                        day_menu['Items'][category][subcat][index] = new_value
                return JSONResponse({'success': True, 'message': 'Item updated successfully in database'})
            else:
                return JSONResponse({'error': 'Item not found in database'}, status_code=404)
        except Exception as e:
            conn.rollback()
            return JSONResponse({'error': f'Database error: {str(e)}'}, status_code=500)
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)

@app.post("/delete_menu_item")
async def delete_menu_item(request: DeleteMenuItemRequest):
    try:
        category = request.category
        subcat = request.subcat
        value = request.value
        date = request.date
        try:
            menu_date = datetime.strptime(date, '%d-%b-%Y').date()
        except ValueError:
            return JSONResponse({'error': 'Invalid date format'}, status_code=400)
        conn = get_mysql_connection()
        cur = conn.cursor()
        try:
            cur.execute('SELECT id FROM menu_days WHERE menu_date = %s', (menu_date,))
            result = cur.fetchone()
            if not result:
                return JSONResponse({'error': 'Date not found in menu'}, status_code=404)
            menu_day_id = result[0]
            cur.execute('''
                DELETE FROM menu_items 
                WHERE menu_day_id = %s AND meal_category = %s AND item_category = %s AND item_name = %s
            ''', (menu_day_id, category, subcat, value))
            if cur.rowcount > 0:
                conn.commit()
                menu = getattr(generator, 'current_menu', None)
                if menu and date in menu:
                    day_menu = menu[date]
                    if (category in day_menu['Items'] and 
                        subcat in day_menu['Items'][category] and 
                        value in day_menu['Items'][category][subcat]):
                        day_menu['Items'][category][subcat].remove(value)
                return JSONResponse({'success': True, 'message': 'Item deleted successfully from database'})
            else:
                return JSONResponse({'error': 'Item not found in database'}, status_code=404)
        except Exception as e:
            conn.rollback()
            return JSONResponse({'error': f'Database error: {str(e)}'}, status_code=500)
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)

@app.post("/add_menu_item")
async def add_menu_item(request: AddMenuItemRequest):
    try:
        category = request.category
        subcat = request.subcat
        value = request.value
        date = request.date
        try:
            menu_date = datetime.strptime(date, '%d-%b-%Y').date()
        except ValueError:
            return JSONResponse({'error': 'Invalid date format'}, status_code=400)
        conn = get_mysql_connection()
        cur = conn.cursor()
        try:
            cur.execute('''
                INSERT INTO menu_days (menu_date, day_name) 
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE day_name = VALUES(day_name)
            ''', (menu_date, menu_date.strftime('%A')))
            menu_day_id = cur.lastrowid if cur.lastrowid else None
            if not menu_day_id:
                cur.execute('SELECT id FROM menu_days WHERE menu_date = %s', (menu_date,))
                menu_day_id = cur.fetchone()[0]
            cur.execute('''
                SELECT COALESCE(MAX(item_order), 0) + 1
                FROM menu_items 
                WHERE menu_day_id = %s
            ''', (menu_day_id,))
            item_order = cur.fetchone()[0]
            cur.execute('''
                INSERT INTO menu_items 
                (menu_day_id, meal_category, item_category, item_name, item_order)
                VALUES (%s, %s, %s, %s, %s)
            ''', (menu_day_id, category, subcat, value, item_order))
            conn.commit()
            menu = getattr(generator, 'current_menu', None)
            if menu and date in menu:
                day_menu = menu[date]
                if 'Items' not in day_menu:
                    day_menu['Items'] = {}
                if category not in day_menu['Items']:
                    day_menu['Items'][category] = {}
                if subcat not in day_menu['Items'][category]:
                    day_menu['Items'][category][subcat] = []
                day_menu['Items'][category][subcat].append(value)
            return JSONResponse({'success': True, 'message': 'Item added successfully to database'})
        except Exception as e:
            conn.rollback()
            return JSONResponse({'error': f'Database error: {str(e)}'}, status_code=500)
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({'error': str(e)}, status_code=500)

@app.post("/add_dish")
async def add_dish(request: AddDishRequest):
    conn = None
    cur = None
    try:
        dish_name = request.dish_name.strip()
        category = request.category.strip()
        ingredients = request.ingredients
        if not dish_name:
            return JSONResponse({'error': 'Dish name is required'}, status_code=400)
        if not category:
            return JSONResponse({'error': 'Category is required'}, status_code=400)
        if not ingredients:
            return JSONResponse({'error': 'At least one ingredient is required'}, status_code=400)
        valid_ingredients = []
        for ing in ingredients:
            if ing.name.strip() and ing.unit.strip():
                try:
                    qty = float(ing.quantity)
                    if qty <= 0:
                        return JSONResponse({'error': f'Quantity for {ing.name} must be greater than 0'}, status_code=400)
                    valid_ingredients.append({'name': ing.name.strip(), 'quantity': qty, 'unit': ing.unit.strip()})
                except ValueError:
                    return JSONResponse({'error': f'Invalid quantity for {ing.name}'}, status_code=400)
        if not valid_ingredients:
            return JSONResponse({'error': 'At least one valid ingredient is required'}, status_code=400)
        conn = get_bom_connection()
        cur = conn.cursor()
        # Check if dish already exists
        cur.execute("SELECT dish_id, Name FROM dishes WHERE TRIM(LOWER(Name)) = TRIM(LOWER(%s))", (dish_name,))
        existing_dish = cur.fetchone()
        if existing_dish:
            existing_dish_id, existing_dish_name = existing_dish
            return JSONResponse({'error': f'Dish "{existing_dish_name}" already exists with ID: {existing_dish_id}'}, status_code=400)
        # Generate new dish_id
        cur.execute("SELECT MAX(CAST(SUBSTRING(dish_id, 2) AS UNSIGNED)) FROM dishes WHERE dish_id LIKE 'D%'")
        max_id_result = cur.fetchone()
        max_id = max_id_result[0] if max_id_result[0] is not None else 0
        next_id = max_id + 1
        dish_id = f"D{next_id:03d}"
        # Insert new dish
        cur.execute("INSERT INTO dishes (dish_id, Name, Meal_Category) VALUES (%s, %s, %s)", (dish_id, dish_name, category))
        # Process each ingredient
        for ingredient in valid_ingredients:
            ing_name = ingredient['name']
            qty = ingredient['quantity']
            unit = ingredient['unit']
            cur.execute("SELECT Ingredient_id, Ingredient_name FROM ingredients WHERE TRIM(LOWER(Ingredient_name)) = TRIM(LOWER(%s))", (ing_name,))
            ingredient_result = cur.fetchone()
            if ingredient_result:
                ingredient_id, _ = ingredient_result
            else:
                cur.execute("SELECT MAX(CAST(SUBSTRING(Ingredient_id, 2) AS UNSIGNED)) FROM ingredients WHERE Ingredient_id LIKE 'I%'")
                max_ing_id_result = cur.fetchone()
                max_ing_id = max_ing_id_result[0] if max_ing_id_result[0] is not None else 0
                next_ing_id = max_ing_id + 1
                ingredient_id = f"I{next_ing_id:03d}"
                cur.execute("INSERT INTO ingredients (Ingredient_id, Ingredient_name) VALUES (%s, %s)", (ingredient_id, ing_name))
            cur.execute("INSERT INTO dish_ingredients (dish_id, Ingredient_id, Serving_per_person, Unit_of_measure) VALUES (%s, %s, %s, %s)", (dish_id, ingredient_id, qty, unit))
        conn.commit()
        return JSONResponse({'success': True, 'message': f'Dish "{dish_name}" added successfully with ID: {dish_id}'})
    except Exception as e:
        if conn:
            conn.rollback()
        import traceback
        traceback.print_exc()
        return JSONResponse({'error': f'Error adding dish: {str(e)}'}, status_code=500)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.post("/update_dish")
async def update_dish(request: UpdateDishRequest):
    conn = None
    cur = None
    try:
        original_dish_name = request.original_dish_name
        updated_dish_name = request.updated_dish_name
        updated_category = request.updated_category
        ingredients = request.ingredients
        conn = get_bom_connection()
        cur = conn.cursor()
        cur.execute("SELECT dish_id FROM dishes WHERE TRIM(LOWER(Name)) = TRIM(LOWER(%s))", (original_dish_name,))
        dish = cur.fetchone()
        if not dish:
            return JSONResponse({'error': 'Original dish not found in database.'}, status_code=404)
        dish_id = dish[0]
        cur.execute("UPDATE dishes SET Name = %s, Meal_Category = %s WHERE dish_id = %s", (updated_dish_name, updated_category, dish_id))
        cur.execute("DELETE FROM dish_ingredients WHERE dish_id = %s", (dish_id,))
        for ing in ingredients:
            ing_name = ing.name
            qty = ing.quantity
            unit = ing.unit
            cur.execute("SELECT Ingredient_id FROM ingredients WHERE TRIM(LOWER(Ingredient_name)) = TRIM(LOWER(%s))", (ing_name,))
            ingredient_result = cur.fetchone()
            if ingredient_result:
                ingredient_id = ingredient_result[0]
            else:
                cur.execute("SELECT MAX(CAST(SUBSTRING(Ingredient_id, 2) AS UNSIGNED)) FROM ingredients")
                max_ing_id = cur.fetchone()[0]
                next_ing_id = 1 if max_ing_id is None else max_ing_id + 1
                ingredient_id = f"I{next_ing_id:03d}"
                cur.execute("SHOW COLUMNS FROM ingredients LIKE 'Meal_Category'")
                has_meal_category = cur.fetchone()
                if has_meal_category:
                    cur.execute("INSERT INTO ingredients (Ingredient_id, Ingredient_name, Meal_Category) VALUES (%s, %s, %s)", (ingredient_id, ing_name, 'Veg'))
                else:
                    cur.execute("INSERT INTO ingredients (Ingredient_id, Ingredient_name) VALUES (%s, %s)", (ingredient_id, ing_name))
            cur.execute("INSERT INTO dish_ingredients (dish_id, Ingredient_id, Serving_per_person, Unit_of_measure) VALUES (%s, %s, %s, %s)", (dish_id, ingredient_id, qty, unit))
        conn.commit()
        return JSONResponse({'success': True, 'message': 'Dish updated successfully!'})
    except Exception as e:
        if conn:
            conn.rollback()
        return JSONResponse({'error': f'Error updating dish: {str(e)}'}, status_code=500)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.post("/delete_dish")
async def delete_dish(request: DeleteDishRequest):
    conn = None
    cur = None
    try:
        dish_name_to_delete = request.dish_name_to_delete
        conn = get_bom_connection()
        cur = conn.cursor()
        cur.execute("SELECT dish_id FROM dishes WHERE TRIM(LOWER(Name)) = TRIM(LOWER(%s))", (dish_name_to_delete,))
        dish_result = cur.fetchone()
        if not dish_result:
            return JSONResponse({'error': 'Dish not found.'}, status_code=404)
        dish_id = dish_result[0]
        cur.execute("DELETE FROM dish_ingredients WHERE dish_id = %s", (dish_id,))
        cur.execute("DELETE FROM dishes WHERE dish_id = %s", (dish_id,))
        conn.commit()
        return JSONResponse({'success': True, 'message': 'Dish deleted successfully!'})
    except Exception as e:
        if conn:
            conn.rollback()
        return JSONResponse({'error': f'Error deleting dish: {str(e)}'}, status_code=500)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def flatten_menu_data(menu_data):
    """
    Convert menu_data from {date: {Day, Items}} format to a list of dicts:
    [ {'Day': ..., 'Meal Type': ..., 'Dish 1': ..., ...}, ... ]
    """
    flat_menu = []
    seen_dishes = set()  # (date, meal_type, dish_name)
    for date, day_data in menu_data.items():
        day = day_data['Day']
        items = day_data['Items']
        for meal_type, meal_packet in items.items():
            if isinstance(meal_packet, list):
                dishes = meal_packet
            else:
                dishes = []
                for cat_items in meal_packet.values():
                    dishes.extend(cat_items)
            # Deduplicate dishes for this meal and across subcategories
            unique_dishes = []
            seen = set()
            for dish in dishes:
                d = dish.strip().lower()
                if d and d not in seen and (date, meal_type, d) not in seen_dishes:
                    unique_dishes.append(dish)
                    seen.add(d)
                    seen_dishes.add((date, meal_type, d))
            row = {'Day': day, 'Meal Type': meal_type}
            for i, dish in enumerate(unique_dishes[:4]):
                row[f'Dish {i+1}'] = dish
            for i in range(len(unique_dishes), 4):
                row[f'Dish {i+1}'] = ''
            row['Date'] = date
            flat_menu.append(row)
    return flat_menu

def calculate_detailed_bom(menu_data, num_students):
    """
    Calculate detailed BOM breakdown by day, meal type, dish, and ingredients
    Returns structure: {
        'detailed': { ... },
        'total': [ ... ]
    }
    """
    conn = get_bom_connection()
    cur = conn.cursor()
    ATTENDANCE = {
        "breakfast": 0.5,
        "snacks": 0.5,
        "lunch": 0.85,
        "dinner": 0.85,
        "brunch": 0.85
    }
    detailed_bom = {}
    ingredient_totals = {}
    for row in menu_data:
        day = row['Day']
        meal_type = row['Meal Type']
        meal_type_lower = meal_type.lower()
        percent = ATTENDANCE.get(meal_type_lower, 1)
        if day not in detailed_bom:
            detailed_bom[day] = {}
        if meal_type not in detailed_bom[day]:
            detailed_bom[day][meal_type] = {}
        for dish_col in ['Dish 1', 'Dish 2', 'Dish 3', 'Dish 4']:
            dish_name = row[dish_col]
            if not dish_name or dish_name.strip() == '':
                continue
            cur.execute("SELECT dish_id FROM dishes WHERE TRIM(LOWER(Name)) = TRIM(LOWER(%s))", (dish_name,))
            dish = cur.fetchone()
            if not dish:
                detailed_bom[day][meal_type][dish_name] = []
                continue
            dish_id = dish[0]
            try:
                cur.execute(
                    "SELECT Dish_Ingredients.Ingredient_id, Ingredients.Name, Dish_Ingredients.Serving_per_person, Dish_Ingredients.Unit_of_measure "
                    "FROM Dish_Ingredients "
                    "JOIN Ingredients ON Dish_Ingredients.Ingredient_id = Ingredients.ingredient_id "
                    "WHERE Dish_Ingredients.dish_id = %s",
                    (dish_id,)
                )
            except Exception as sql_e:
                detailed_bom[day][meal_type][dish_name] = []
                continue
            dish_ingredients = []
            for ing_id, ing_name, serving, unit in cur.fetchall():
                qty = float(serving) * num_students * percent
                display_qty = round(qty, 2)
                display_unit = unit
                if unit in ['gm', 'g'] and qty >= 1000:
                    display_qty = round(qty / 1000, 2)
                    display_unit = 'kg'
                elif unit in ['ml', 'mL'] and qty >= 1000:
                    display_qty = round(qty / 1000, 2)
                    display_unit = 'L'
                dish_ingredients.append({
                    'id': ing_id,
                    'name': ing_name,
                    'quantity': display_qty,
                    'unit': display_unit
                })
                key = (ing_name, display_unit)
                ingredient_totals[key] = ingredient_totals.get(key, 0) + display_qty
            detailed_bom[day][meal_type][dish_name] = dish_ingredients
    total_results = []
    for (ing_name, unit), total_qty in ingredient_totals.items():
        total_results.append({
            'ingredient': ing_name,
            'quantity': round(total_qty, 2),
            'unit': unit
        })
    cur.close()
    conn.close()
    return {
        'detailed': detailed_bom,
        'total': total_results
    }

def get_dish_bom(dish_name, num_students, attendance_percent):
    conn = get_bom_connection()
    cur = conn.cursor()
    cur.execute("SELECT dish_id FROM dishes WHERE TRIM(LOWER(Name)) = TRIM(LOWER(%s))", (dish_name,))
    dish = cur.fetchone()
    if not dish:
        cur.close()
        conn.close()
        return []
    dish_id = dish[0]
    cur.execute("""
        SELECT i.Name, di.Serving_per_person, di.Unit_of_measure 
        FROM dish_ingredients di 
        JOIN ingredients i ON di.Ingredient_id = i.Ingredient_id 
        WHERE di.dish_id=%s
    """, (dish_id,))
    ingredients = []
    for ing_name, serving, unit in cur.fetchall():
        qty = float(serving) * num_students * attendance_percent
        display_qty = round(qty, 2)
        display_unit = unit
        if unit in ['gm', 'g'] and qty >= 1000:
            display_qty = round(qty / 1000, 2)
            display_unit = 'kg'
        elif unit in ['ml', 'mL'] and qty >= 1000:
            display_qty = round(qty / 1000, 2)
            display_unit = 'L'
        ingredients.append({
            'name': ing_name,
            'quantity': display_qty,
            'unit': display_unit
        })
    cur.close()
    conn.close()
    return ingredients

def calculate_dish_wise_bom(menu_data, num_students):
    ATTENDANCE = {
        "breakfast": 0.5,
        "snacks": 0.5,
        "lunch": 0.85,
        "dinner": 0.85,
        "brunch": 0.85
    }
    dish_wise_bom = {}
    for row in menu_data:
        day = row['Day']
        meal_type = row['Meal Type'].lower()
        percent = ATTENDANCE.get(meal_type, 1)
        if day not in dish_wise_bom:
            dish_wise_bom[day] = {}
        for dish_col in ['Dish 1', 'Dish 2', 'Dish 3', 'Dish 4']:
            dish_name = row[dish_col]
            if not dish_name or dish_name.strip() == '':
                continue
            if dish_name not in dish_wise_bom[day]:
                dish_wise_bom[day][dish_name] = get_dish_bom(dish_name, num_students, percent)
    return dish_wise_bom

@app.get("/dish_wise_bom")
async def dish_wise_bom(request: Request):
    # Use the current menu from the generator and last used num_students from session or default
    menu_data = getattr(generator, 'current_menu', None)
    num_students = request.session.get('num_students', 100)  # Default to 100 if not set
    if not menu_data:
        return templates.TemplateResponse("dish_wise_bom.html", {"request": request, "dish_wise_bom": {}, "error": "No menu data found. Please generate a menu first."})
    flat_menu = flatten_menu_data(menu_data)
    dish_bom = calculate_dish_wise_bom(flat_menu, num_students)
    return templates.TemplateResponse("dish_wise_bom.html", {"request": request, "dish_wise_bom": dish_bom, "error": None})

@app.get("/debug_menu_mismatches")
async def debug_menu_mismatches():
    menu = getattr(generator, 'current_menu', None)
    if not menu:
        return {"error": "No menu generated yet."}
    # Collect all unique dish names from the menu
    menu_dishes = set()
    for day_data in menu.values():
        for meal_data in day_data['Items'].values():
            if isinstance(meal_data, list):
                menu_dishes.update([str(dish).strip() for dish in meal_data if dish and str(dish).strip()])
            elif isinstance(meal_data, dict):
                for subcat_items in meal_data.values():
                    menu_dishes.update([str(dish).strip() for dish in subcat_items if dish and str(dish).strip()])
    # Get all valid dish names from the BOM database
    conn = get_bom_connection()
    cur = conn.cursor()
    cur.execute("SELECT Name FROM dishes")
    db_dishes = set(str(row[0]).strip().lower() for row in cur.fetchall())
    cur.close()
    conn.close()
    # Find mismatches (case-insensitive, trimmed)
    mismatches = [dish for dish in menu_dishes if dish.strip().lower() not in db_dishes]
    return {"mismatched_dishes": sorted(mismatches)}

def calculate_custom_bom_individual(menu_data, attendance_map):
    """
    For each (date, meal_type), multiply Serving_per_person by the exact number entered for that meal.
    Each unique dish is only counted once per meal per day, regardless of how many times it appears.
    Returns: (ingredient_totals, detailed_bom)
    - ingredient_totals: {ingredient_name: {qty, unit}}
    - detailed_bom: {date: {meal_type: {dish_name: [ {ingredient, quantity, unit}, ... ] } } }
    """
    conn = get_bom_connection()
    cur = conn.cursor()
    ingredient_totals = {}
    detailed_bom = {}
    # Group dishes by (date, meal_type)
    dishes_by_meal = {}
    for row in menu_data:
        date = row.get('Date')
        meal_type = row['Meal Type']
        key = (date, meal_type)
        if key not in dishes_by_meal:
            dishes_by_meal[key] = set()
        for dish_col in ['Dish 1', 'Dish 2', 'Dish 3', 'Dish 4']:
            dish_name = row.get(dish_col)
            if dish_name:
                dishes_by_meal[key].add(dish_name.strip())
    for (date, meal_type), unique_dishes in dishes_by_meal.items():
        num_people = attendance_map.get((date, meal_type), 0)
        if num_people is None or num_people == 0:
            continue
        # Prepare detailed_bom structure
        if date not in detailed_bom:
            detailed_bom[date] = {}
        if meal_type not in detailed_bom[date]:
            detailed_bom[date][meal_type] = {}
        for dish_name in unique_dishes:
            cur.execute("SELECT dish_id FROM Dishes WHERE LOWER(TRIM(Name)) = %s", (dish_name.strip().lower(),))
            dish_row = cur.fetchone()
            if not dish_row:
                continue
            dish_id = dish_row[0]
            cur.execute(
                "SELECT Dish_Ingredients.Ingredient_id, Ingredients.Name, Dish_Ingredients.Serving_per_person, Dish_Ingredients.Unit_of_measure "
                "FROM Dish_Ingredients "
                "JOIN Ingredients ON Dish_Ingredients.Ingredient_id = Ingredients.ingredient_id "
                "WHERE Dish_Ingredients.dish_id = %s",
                (dish_id,)
            )
            dish_ingredients = []
            for ing_id, ing_name, serving, unit in cur.fetchall():
                qty = float(serving) * num_people
                display_qty = round(qty, 2)
                display_unit = unit
                if unit in ['gm', 'g'] and qty >= 1000:
                    display_qty = round(qty / 1000, 2)
                    display_unit = 'kg'
                elif unit in ['ml', 'mL'] and qty >= 1000:
                    display_qty = round(qty / 1000, 2)
                    display_unit = 'L'
                dish_ingredients.append({
                    'ingredient': ing_name,
                    'quantity': display_qty,
                    'unit': display_unit
                })
                # Add to ingredient_totals
                if ing_name not in ingredient_totals:
                    ingredient_totals[ing_name] = {'qty': 0, 'unit': display_unit}
                ingredient_totals[ing_name]['qty'] += display_qty
                ingredient_totals[ing_name]['unit'] = display_unit
            detailed_bom[date][meal_type][dish_name] = dish_ingredients
    conn.close()
    return ingredient_totals, detailed_bom

@app.post("/generate_custom_bom")
async def generate_custom_bom(request: Request):
    data = await request.json()
    attendance = data.get('attendance', [])
    menu_data = getattr(generator, 'current_menu', None)
    if not menu_data:
        return HTMLResponse("<h2>No menu data found. Please generate a menu first.</h2>")
    flat_menu = flatten_menu_data(menu_data)
    # Build attendance_map
    attendance_map = {}
    for row in attendance:
        date = row['date']
        for meal, num in row['meals'].items():
            attendance_map[(date, meal)] = num
    ingredient_totals, detailed_bom = calculate_custom_bom_individual(flat_menu, attendance_map)
    bom_results_list = [
        {"ingredient": name, "quantity": data["qty"], "unit": data["unit"]}
        for name, data in ingredient_totals.items()
    ]
    return templates.TemplateResponse("bom_results.html", {
        "request": request,
        "bom_results": bom_results_list,
        "detailed_bom": detailed_bom,
        "num_students": None,
        "menu_data": menu_data,
        "error": None
    })

@app.post("/update_dish_ingredient")
async def update_dish_ingredient(
    dish_id: str = Form(...),
    ingredient_id: str = Form(...),
    name: str = Form(...),
    serving: float = Form(...),
    unit: str = Form(...)
):
    conn = get_bom_connection()
    cur = conn.cursor()
    # Update the ingredient name in Ingredients table
    cur.execute("UPDATE Ingredients SET Name=%s WHERE ingredient_id=%s", (name, ingredient_id))
    # Update the serving and unit in Dish_Ingredients table
    cur.execute(
        "UPDATE Dish_Ingredients SET Serving_per_person=%s, Unit_of_measure=%s WHERE dish_id=%s AND Ingredient_id=%s",
        (serving, unit, dish_id, ingredient_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"success": True}

@app.get("/get_dish_recommendations")
async def get_dish_recommendations(query: str):
    """Get dish recommendations based on user input for autocomplete"""
    if not query or len(query.strip()) < 1:
        return JSONResponse({"recommendations": []})
    
    conn = None
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='Ravindra@140',
            db='bom',
            cursorclass=pymysql.cursors.Cursor
        )
        cur = conn.cursor()
        
        # Search for dishes that start with the query (case-insensitive)
        search_query = f"{query.strip()}%"
        cur.execute("""
            SELECT dish_id, Name, Meal_Category 
            FROM dishes 
            WHERE LOWER(Name) LIKE LOWER(%s) 
            ORDER BY Name 
            LIMIT 10
        """, (search_query,))
        
        dishes = cur.fetchall()
        recommendations = []
        for dish_id, dish_name, meal_category in dishes:
            recommendations.append({
                'dish_id': dish_id,
                'name': dish_name,
                'category': meal_category
            })
        
        cur.close()
        return JSONResponse({"recommendations": recommendations})
    except Exception as e:
        return JSONResponse({"error": f"Database error: {str(e)}"}, status_code=500)
    finally:
        if conn:
            conn.close()

class PaxPredictRequest(BaseModel):
    date: str  # YYYY-MM-DD
    total_present: int
    is_exam: bool = False
    exam_time: Optional[str] = None

class PaxPredictResponse(BaseModel):
    breakfast: int
    brunch: int
    lunch: int
    snacks: int
    dinner: int
    notes: list[str] = []

@app.post("/pax_predict", response_model=PaxPredictResponse)
async def pax_predict(request: PaxPredictRequest):
    if pax_ml_model is None:
        return {"breakfast": 0, "brunch": 0, "lunch": 0, "snacks": 0, "dinner": 0, "notes": ["Model not loaded."]}
    try:
        date_obj = datetime.strptime(request.date, "%Y-%m-%d")
        day_name = date_obj.strftime("%A")
        meal_types = ["Breakfast", "Brunch", "Lunch", "Snacks", "Dinner"]
        results = []
        for meal in meal_types:
            if meal == "Brunch" and day_name != "Sunday":
                results.append(0)
                continue
            features = {col: 0 for col in pax_ml_columns}
            if 'DateOrdinal' in pax_ml_columns:
                features['DateOrdinal'] = date_obj.toordinal()
            meal_col = f"Meal Type_{meal}"
            if meal_col in features:
                features[meal_col] = 1
            day_col = f"Day_{day_name}"
            if day_col in features:
                features[day_col] = 1
            X = pd.DataFrame([features])[pax_ml_columns]
            pred = pax_ml_model.predict(X)
            results.append(int(round(pred[0])) if hasattr(pred, '__iter__') else int(round(pred)))
        return PaxPredictResponse(
            breakfast=results[0],
            brunch=results[1],
            lunch=results[2],
            snacks=results[3],
            dinner=results[4],
            notes=["Brunch is only available on Sundays."] if day_name != "Sunday" else []
        )
    except Exception as e:
        return PaxPredictResponse(breakfast=0, brunch=0, lunch=0, snacks=0, dinner=0, notes=[f"Prediction error: {e}"])

# --- Pax ML Settings Endpoints ---

class BatchSettingIn(BaseModel):
    batch_name: str
    total_count: int
    weekend_stay_percent: float

class BatchSettingOut(BaseModel):
    id: int
    batch_name: str
    total_count: int
    weekend_stay_percent: float
    class Config:
        orm_mode = True

@app.get("/pax_settings/batches", response_model=List[BatchSettingOut])
async def get_batches(db=Depends(get_pax_db)):
    return db.query(BatchSetting).all()

@app.post("/pax_settings/batches", response_model=BatchSettingOut)
async def set_batch(batch: BatchSettingIn, db=Depends(get_pax_db)):
    obj = db.query(BatchSetting).filter(BatchSetting.batch_name == batch.batch_name).first()
    if obj:
        obj.total_count = batch.total_count
        obj.weekend_stay_percent = batch.weekend_stay_percent
    else:
        obj = BatchSetting(**batch.dict())
        db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

class ExamRuleIn(BaseModel):
    exam_time: str
    meal: str
    reduction_percent: float

class ExamRuleOut(BaseModel):
    id: int
    exam_time: str
    meal: str
    reduction_percent: float
    class Config:
        orm_mode = True

@app.get("/pax_settings/exam_rules", response_model=List[ExamRuleOut])
async def get_exam_rules(db=Depends(get_pax_db)):
    return db.query(ExamRule).all()

@app.post("/pax_settings/exam_rules", response_model=ExamRuleOut)
async def set_exam_rule(rule: ExamRuleIn, db=Depends(get_pax_db)):
    obj = ExamRule(**rule.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

class ExamDateIn(BaseModel):
    date: str
    exam_time: str

class ExamDateOut(BaseModel):
    id: int
    date: str
    exam_time: str
    class Config:
        orm_mode = True

@app.get("/pax_settings/exam_dates", response_model=List[ExamDateOut])
async def get_exam_dates(db=Depends(get_pax_db)):
    return db.query(ExamDate).all()

@app.post("/pax_settings/exam_dates", response_model=ExamDateOut)
async def add_exam_date(exam: ExamDateIn, db=Depends(get_pax_db)):
    obj = ExamDate(**exam.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/pax_settings/exam_dates/{date}")
async def delete_exam_date(date: str, db=Depends(get_pax_db)):
    obj = db.query(ExamDate).filter(ExamDate.date == date).first()
    if obj:
        db.delete(obj)
        db.commit()
        return {"success": True}
    return {"success": False, "error": "Not found"}

class MealPaxRequest(BaseModel):
    menu: List[Dict[str, Any]]  # Each dict: {date, day, meal_type, unique_dish}

class MealPaxResponse(BaseModel):
    predictions: List[Dict[str, Any]]  # Each dict: {date, day, meal_type, unique_dish, predicted_pax, method}

@app.post("/predict_meal_pax", response_model=MealPaxResponse)
async def predict_meal_pax(request: Request):
    import pandas as pd
    data = await request.json()
    menu = data.get('menu', [])
    results = []
    # Load Unique Dish.csv (no header)
    try:
        unique_dish_df = pd.read_csv('Pax ML/Unique Dish.csv', header=None, names=['Date', 'Day', 'Meal Type', 'UniqueDish'])
        # Normalize date format for matching
        unique_dish_df['Date'] = pd.to_datetime(unique_dish_df['Date'], errors='coerce').dt.date
        unique_dish_df['Day'] = unique_dish_df['Day'].str.strip()
        unique_dish_df['Meal Type'] = unique_dish_df['Meal Type'].str.strip()
        unique_dish_df['UniqueDish'] = unique_dish_df['UniqueDish'].str.strip()
    except Exception:
        unique_dish_df = None
    # Load Pax ML (1).csv (header, meal columns may have spaces)
    try:
        pax_df = pd.read_csv('Pax ML/Pax ML (1).csv')
        pax_df = pax_df.rename(columns=lambda x: x.strip())
        pax_df['Date'] = pd.to_datetime(pax_df['Date'], errors='coerce').dt.date
        pax_df['Day'] = pax_df['Day'].str.strip()
    except Exception:
        pax_df = None
    for entry in menu:
        try:
            date = pd.to_datetime(entry.get('date'), errors='coerce').date() if entry.get('date') else None
            day = entry.get('day', None)
            meal_type = entry.get('meal_type', None)
            unique_dish = entry.get('unique_dish', None)
            method = None
            predicted_pax = None
            if not (date and day and meal_type and unique_dish):
                results.append({
                    'date': str(date) if date else None,
                    'day': day,
                    'meal_type': meal_type,
                    'unique_dish': unique_dish,
                    'predicted_pax': 'no_data',
                    'method': 'no_data'
                })
                continue
            found_csv = False
            # Special branch for Sunday Brunch: ignore unique_dish, use meal-level lookup
            if (
                str(day).lower().strip() == 'sunday' and str(meal_type).lower().strip() == 'brunch' and pax_df is not None
            ):
                meal_col = 'Brunch'
                print(f"[DEBUG] Sunday Brunch lookup: date={date}, day={day}, meal_col={meal_col}")
                print(f"[DEBUG] Available dates in CSV: {pax_df['Date'].unique()}")
                print(f"[DEBUG] Available days in CSV: {pax_df['Day'].unique()}")
                # Try exact match first
                pax_mask = (
                    (pax_df['Date'] == date) &
                    (pax_df['Day'].str.lower().str.strip() == str(day).lower().strip())
                )
                pax_val = pax_df.loc[pax_mask, meal_col]
                print(f"[DEBUG] Sunday Brunch pax_mask: {pax_mask}")
                print(f"[DEBUG] Sunday Brunch pax_val: {pax_val}")
                if not pax_val.empty and pd.notnull(pax_val.iloc[0]):
                    predicted_pax = pax_val.iloc[0]
                    method = 'csv_lookup_sunday_brunch_exact'
                    found_csv = True
                else:
                    # No exact match, use closest previous Sunday
                    sundays = pax_df[(pax_df['Day'].str.lower().str.strip() == 'sunday') & pd.notnull(pax_df[meal_col])]
                    sundays = sundays[sundays['Date'] < date]
                    if not sundays.empty:
                        closest_idx = sundays['Date'].idxmax()
                        predicted_pax = sundays.loc[closest_idx, meal_col]
                        method = 'csv_lookup_sunday_brunch_closest_previous'
                        print(f"[DEBUG] Used closest previous Sunday: {sundays.loc[closest_idx, 'Date']}")
                        found_csv = True
                    else:
                        print(f"[DEBUG] No previous Sunday Brunch value found in CSV for date < {date}")
            # General CSV lookup for other meals (including Brunch on other days, if any)
            if not found_csv and unique_dish_df is not None and pax_df is not None:
                mask = (
                    (unique_dish_df['Date'] == date) &
                    (unique_dish_df['Day'].str.lower().str.strip() == str(day).lower().strip()) &
                    (unique_dish_df['Meal Type'].str.lower().str.strip() == str(meal_type).lower().strip()) &
                    (unique_dish_df['UniqueDish'].str.lower().str.strip() == str(unique_dish).lower().strip())
                )
                if unique_dish_df[mask].shape[0] > 0:
                    meal_col = meal_type.strip()
                    pax_mask = (
                        (pax_df['Date'] == date) &
                        (pax_df['Day'].str.lower().str.strip() == str(day).lower().strip())
                    )
                    pax_val = pax_df.loc[pax_mask, meal_col]
                    if not pax_val.empty and pd.notnull(pax_val.values[0]):
                        try:
                            predicted_pax = int(round(float(pax_val.values[0])))
                            method = 'csv_lookup'
                            found_csv = True
                        except Exception:
                            predicted_pax = None
            if not found_csv and pax_ml_model is not None:
                features = {col: 0 for col in pax_ml_columns}
                if 'DateOrdinal' in features and date:
                    features['DateOrdinal'] = pd.to_datetime(date).toordinal()
                dish_col = None
                if unique_dish:
                    norm_dish = unique_dish.strip().lower()
                    for col in pax_ml_columns:
                        if col.strip().lower() == norm_dish:
                            dish_col = col
                            break
                    if dish_col:
                        features[dish_col] = 1
                if f"Meal Type_{meal_type}" in features:
                    features[f"Meal Type_{meal_type}"] = 1
                if f"Day_{day}" in features:
                    features[f"Day_{day}"] = 1
                try:
                    X = pd.DataFrame([features])
                    predicted_pax = int(pax_ml_model.predict(X)[0])
                    method = 'ml'
                except Exception:
                    predicted_pax = None
            if predicted_pax is None:
                predicted_pax = 'no_data'
                method = 'no_data'
            results.append({
                'date': str(date) if date else None,
                'day': day,
                'meal_type': meal_type,
                'unique_dish': unique_dish,
                'predicted_pax': predicted_pax,
                'method': method
            })
        except Exception:
            results.append({
                'date': entry.get('date', None),
                'day': entry.get('day', None),
                'meal_type': entry.get('meal_type', None),
                'unique_dish': entry.get('unique_dish', None),
                'predicted_pax': 'error',
                'method': 'error'
            })
    return {'predictions': results} 

# --- Inventory and BOM Endpoints ---
from fastapi import Body

class InventoryUpdateRequest(BaseModel):
    ingredient_id: str
    new_quantity: float

class BOMItem(BaseModel):
    ingredient_id: str
    quantity: float

@app.get("/inventory")
async def inventory(request: Request):
    if not request.session.get('user_id'):
        return RedirectResponse(url="/login", status_code=303)
    # Fetch inventory from DB
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="Ravindra@140",
        db="bom",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingredient_inventory")
    inventory = cursor.fetchall()
    cursor.close()
    conn.close()
    return templates.TemplateResponse(
        "inventory.html",
        {"request": request, "active_page": "inventory", "inventory": inventory}
    )

@app.post("/inventory/update")
async def update_inventory_form(request: Request, ingredient_id: str = Form(...), new_quantity: float = Form(...)):
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="Ravindra@140",
        db="bom",
        cursorclass=pymysql.cursors.Cursor
    )
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM ingredient_inventory WHERE ingredient_id = %s", (ingredient_id,))
    old_qty = cursor.fetchone()
    old_qty = old_qty[0] if old_qty else None
    cursor.execute(
        "UPDATE ingredient_inventory SET quantity = %s WHERE ingredient_id = %s",
        (new_quantity, ingredient_id)
    )
    change_amount = new_quantity - (old_qty if old_qty is not None else 0)
    cursor.execute(
        "INSERT INTO inventory_activity (ingredient_id, change_amount, action, note) VALUES (%s, %s, %s, %s)",
        (ingredient_id, change_amount, 'manual edit', 'Manual inventory update')
    )
    conn.commit()
    cursor.close()
    conn.close()
    return RedirectResponse(url="/inventory", status_code=303)

@app.post("/bom/finalize")
def finalize_bom_api(bom: list[BOMItem] = Body(...)):
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="Ravindra@140",
        db="bom",
        cursorclass=pymysql.cursors.Cursor
    )
    cursor = conn.cursor()
    for item in bom:
        # Subtract from inventory
        cursor.execute(
            "UPDATE ingredient_inventory SET quantity = quantity - %s WHERE ingredient_id = %s",
            (item.quantity, item.ingredient_id)
        )
        # Log the subtraction
        cursor.execute(
            "INSERT INTO inventory_activity (ingredient_id, change_amount, action, note) VALUES (%s, %s, %s, %s)",
            (item.ingredient_id, -item.quantity, 'subtracted', 'BOM finalized')
        )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "success"}

@app.get("/inventory/activity")
def get_inventory_activity_api():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="Ravindra@140",
        db="bom",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory_activity ORDER BY timestamp DESC")
    activity = cursor.fetchall()
    cursor.close()
    conn.close()
    return activity