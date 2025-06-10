from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from menu_generator import IndianMenuGenerator
from datetime import datetime, timedelta
from flask_mysqldb import MySQL
import random
import json
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
generator = IndianMenuGenerator()

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '16042006'
app.config['MYSQL_DB'] = 'rafeedo'
app.secret_key = 'super_secret_key'

mysql = MySQL(app)

# Add a second Flask app and MySQL connection for bom1
from flask import Flask as FlaskBOM
app_bom = FlaskBOM(__name__)
app_bom.config['MYSQL_HOST'] = 'localhost'
app_bom.config['MYSQL_USER'] = 'root'
app_bom.config['MYSQL_PASSWORD'] = '16042006'
app_bom.config['MYSQL_DB'] = 'bom1'
mysql_bom = MySQL(app_bom)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize the model when starting the app
print("Initializing menu generator...")
generator.prepare_data('Weekly_Menu_Categorized.xlsx')

# Helper for BOM calculation
ATTENDANCE = {
    "breakfast": 0.5,
    "snacks": 0.5,
    "lunch": 0.85,
    "dinner": 0.85,
    "brunch": 0.85
}

def calculate_bom(menu_data, num_students, dish_filter=None):
    # menu_data: dict of {date: {Day, Items}}
    # dish_filter: None or dish name (if only one dish is selected)
    ingredient_totals = {}
    try:
        # Get MySQL connection properly
        cur = mysql.connection.cursor()
        
        # Check if dish_ingredients table exists
        cur.execute("SHOW TABLES LIKE 'dish_ingredients'")
        if not cur.fetchone():
            print("dish_ingredients table does not exist. Creating sample BOM data.")
            # Return sample BOM data for now
            sample_ingredients = [
                {'ingredient': 'Rice', 'quantity': round(num_students * 0.1, 2), 'unit': 'kg'},
                {'ingredient': 'Dal', 'quantity': round(num_students * 0.05, 2), 'unit': 'kg'},
                {'ingredient': 'Vegetables', 'quantity': round(num_students * 0.2, 2), 'unit': 'kg'},
                {'ingredient': 'Oil', 'quantity': round(num_students * 0.02, 2), 'unit': 'L'},
                {'ingredient': 'Spices', 'quantity': round(num_students * 0.01, 2), 'unit': 'kg'},
                {'ingredient': 'Tea', 'quantity': round(num_students * 0.005, 2), 'unit': 'kg'},
                {'ingredient': 'Milk', 'quantity': round(num_students * 0.1, 2), 'unit': 'L'},
                {'ingredient': 'Bread', 'quantity': round(num_students * 0.1, 2), 'unit': 'pieces'},
            ]
            cur.close()
            return sample_ingredients
        
        # Process menu data to calculate BOM
        for day, day_data in menu_data.items():
            items = day_data['Items']
            for meal_type, meal_data in items.items():
                percent = ATTENDANCE.get(meal_type.lower(), 1)
                for category, dishes in meal_data.items():
                    for dish in dishes:
                        if dish_filter and dish_filter != 'all' and dish != dish_filter:
                            continue
                        # For now, use sample calculations since dish_ingredients table doesn't exist
                        # In a real implementation, you would look up ingredients for each dish
                        pass
        
        cur.close()
        
        # Return sample BOM data based on menu items and attendance
        total_meals = 0
        for day, day_data in menu_data.items():
            for meal_type in day_data['Items']:
                total_meals += 1
        
        # Calculate sample ingredients based on number of students and meals
        sample_ingredients = [
            {'ingredient': 'Rice', 'quantity': round(num_students * 0.1 * total_meals * 0.3, 2), 'unit': 'kg'},
            {'ingredient': 'Dal', 'quantity': round(num_students * 0.05 * total_meals * 0.3, 2), 'unit': 'kg'},
            {'ingredient': 'Vegetables', 'quantity': round(num_students * 0.2 * total_meals * 0.3, 2), 'unit': 'kg'},
            {'ingredient': 'Oil', 'quantity': round(num_students * 0.02 * total_meals * 0.3, 2), 'unit': 'L'},
            {'ingredient': 'Spices', 'quantity': round(num_students * 0.01 * total_meals * 0.3, 2), 'unit': 'kg'},
            {'ingredient': 'Tea', 'quantity': round(num_students * 0.005 * total_meals * 0.3, 2), 'unit': 'kg'},
            {'ingredient': 'Milk', 'quantity': round(num_students * 0.1 * total_meals * 0.3, 2), 'unit': 'L'},
            {'ingredient': 'Bread', 'quantity': round(num_students * 0.1 * total_meals * 0.3, 2), 'unit': 'pieces'},
        ]
        return sample_ingredients
        
    except Exception as e:
        print(f"Error in BOM calculation: {e}")
        # Return sample BOM data as fallback
        sample_ingredients = [
            {'ingredient': 'Rice', 'quantity': round(num_students * 0.1, 2), 'unit': 'kg'},
            {'ingredient': 'Dal', 'quantity': round(num_students * 0.05, 2), 'unit': 'kg'},
            {'ingredient': 'Vegetables', 'quantity': round(num_students * 0.2, 2), 'unit': 'kg'},
            {'ingredient': 'Oil', 'quantity': round(num_students * 0.02, 2), 'unit': 'L'},
            {'ingredient': 'Spices', 'quantity': round(num_students * 0.01, 2), 'unit': 'kg'},
            {'ingredient': 'Tea', 'quantity': round(num_students * 0.005, 2), 'unit': 'kg'},
            {'ingredient': 'Milk', 'quantity': round(num_students * 0.1, 2), 'unit': 'L'},
            {'ingredient': 'Bread', 'quantity': round(num_students * 0.1, 2), 'unit': 'pieces'},
        ]
        return sample_ingredients

def create_tables():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # Create users table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create user_logins table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS user_logins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Create dishes table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS dishes (
                    dish_id VARCHAR(10) PRIMARY KEY,
                    dish_name VARCHAR(100) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create menu_variations table
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
            
            # Create menu_days table
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
            
            # Create menu_items table
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
            
            # Insert a test user
            cur.execute('''
                INSERT INTO users (username, password)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE password = VALUES(password)
            ''', ('admin', 'admin123'))
            
            # Insert sample dishes if they don't exist
            sample_dishes = [
                ('D001', 'Tea', 'Beverages'),
                ('D002', 'Coffee', 'Beverages'),
                ('D003', 'Bread', 'Main Course'),
                ('D004', 'Poha', 'Main Course'),
                ('D005', 'Chapati', 'Main Course'),
                ('D006', 'Rice', 'Main Course'),
                ('D007', 'Dal', 'Side Dish'),
                ('D008', 'Vegetable Curry', 'Main Course'),
                ('D009', 'Salad', 'Side Dish'),
                ('D010', 'Snacks', 'Snacks'),
                ('D011', 'Aloo Paratha', 'Main Course'),
                ('D012', 'Paneer Butter Masala', 'Main Course'),
                ('D013', 'Naan', 'Bread')
            ]
            
            for dish_id, dish_name, category in sample_dishes:
                cur.execute('''
                    INSERT INTO dishes (dish_id, dish_name, category)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    dish_name = VALUES(dish_name),
                    category = VALUES(category)
                ''', (dish_id, dish_name, category))
            
            mysql.connection.commit()
            print("Tables created successfully!")
            
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
            mysql.connection.rollback()
        finally:
            if 'cur' in locals():
                cur.close()

    # Ensure BOM-related tables are created in bom1 database
    with app_bom.app_context():
        try:
            cur_bom = mysql_bom.connection.cursor()

            # Check if dishes table exists and what its schema looks like
            cur_bom.execute("SHOW TABLES LIKE 'dishes'")
            dishes_table_exists = cur_bom.fetchone()
            
            if dishes_table_exists:
                print("dishes table exists, checking schema...")
                cur_bom.execute("DESCRIBE dishes")
                columns = cur_bom.fetchall()
                print("Current dishes table schema:")
                for col in columns:
                    print(f"  {col}")
                
                # Verify the expected schema
                expected_columns = ['dish_id', 'Name', 'Meal_Category']
                actual_columns = [col[0] for col in columns]
                if all(col in actual_columns for col in expected_columns):
                    print("✓ dishes table has correct schema")
                else:
                    print("⚠ dishes table schema may not match expected format")
            else:
                print("No dishes table exists")

            # Check ingredients table schema
            cur_bom.execute("SHOW TABLES LIKE 'ingredients'")
            ingredients_table_exists = cur_bom.fetchone()
            if ingredients_table_exists:
                print("ingredients table exists, checking schema...")
                cur_bom.execute("DESCRIBE ingredients")
                columns = cur_bom.fetchall()
                print("Current ingredients table schema:")
                for col in columns:
                    print(f"  {col}")

            # Check dish_ingredients table schema
            cur_bom.execute("SHOW TABLES LIKE 'dish_ingredients'")
            dish_ingredients_table_exists = cur_bom.fetchone()
            if dish_ingredients_table_exists:
                print("dish_ingredients table exists, checking schema...")
                cur_bom.execute("DESCRIBE dish_ingredients")
                columns = cur_bom.fetchall()
                print("Current dish_ingredients table schema:")
                for col in columns:
                    print(f"  {col}")

            mysql_bom.connection.commit()
            print("BOM database schema checked successfully!")

        except Exception as e:
            print(f"Error checking BOM database schema: {str(e)}")
            mysql_bom.connection.rollback()
        finally:
            if 'cur_bom' in locals():
                cur_bom.close()

def save_menu_to_database(menu_data):
    """Save generated menu data to MySQL database"""
    try:
        cur = mysql.connection.cursor()
        
        for date_str, day_data in menu_data.items():
            # Parse date string to MySQL DATE format
            try:
                menu_date = datetime.strptime(date_str, '%d-%b-%Y').date()
            except ValueError:
                print(f"Invalid date format: {date_str}")
                continue
            
            day_name = day_data['Day']
            
            # Insert or update menu_day record
            cur.execute('''
                INSERT INTO menu_days (menu_date, day_name) 
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE day_name = VALUES(day_name)
            ''', (menu_date, day_name))
            
            # Get the menu_day_id
            menu_day_id = cur.lastrowid if cur.lastrowid else None
            if not menu_day_id:
                cur.execute('SELECT id FROM menu_days WHERE menu_date = %s', (menu_date,))
                menu_day_id = cur.fetchone()[0]
            
            # Clear existing menu items for this day
            cur.execute('DELETE FROM menu_items WHERE menu_day_id = %s', (menu_day_id,))
            
            # Insert menu items
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
        
        mysql.connection.commit()
        print("Menu data saved to database successfully!")
        return True
        
    except Exception as e:
        print(f"Error saving menu to database: {str(e)}")
        mysql.connection.rollback()
        return False
    finally:
        if 'cur' in locals():
            cur.close()

def get_menu_from_database(start_date, end_date):
    """Retrieve menu data from MySQL database for given date range"""
    try:
        cur = mysql.connection.cursor()
        
        # Convert date strings to MySQL DATE format
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            try:
                start_dt = datetime.strptime(start_date, '%d-%m-%Y').date()
                end_dt = datetime.strptime(end_date, '%d-%m-%Y').date()
            except ValueError:
                print(f"Invalid date format: {start_date} or {end_date}")
                return {}
        
        # Get menu days in date range
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
            
            # Get menu items for this day
            cur.execute('''
                SELECT meal_category, item_category, item_name, item_order
                FROM menu_items 
                WHERE menu_day_id = %s 
                ORDER BY meal_category, item_order
            ''', (menu_day_id,))
            
            menu_items = cur.fetchall()
            
            # Organize items by meal category and item category
            day_menu = {}
            for meal_category, item_category, item_name, item_order in menu_items:
                if meal_category not in day_menu:
                    day_menu[meal_category] = {}
                if item_category not in day_menu[meal_category]:
                    day_menu[meal_category][item_category] = []
                day_menu[meal_category][item_category].append(item_name)
            
            # Format date string
            date_str = menu_date.strftime('%d-%b-%Y')
            menu_data[date_str] = {
                'Date': date_str,
                'Day': day_name,
                'Items': day_menu
            }
        
        return menu_data
        
    except Exception as e:
        print(f"Error retrieving menu from database: {str(e)}")
        return {}
    finally:
        if 'cur' in locals():
            cur.close()

def delete_menu_from_database(start_date, end_date):
    """Delete menu data from MySQL database for given date range"""
    try:
        cur = mysql.connection.cursor()
        
        # Convert date strings to MySQL DATE format
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            try:
                start_dt = datetime.strptime(start_date, '%d-%m-%Y').date()
                end_dt = datetime.strptime(end_date, '%d-%m-%Y').date()
            except ValueError:
                print(f"Invalid date format: {start_date} or {end_date}")
                return False
        
        # Delete menu items and days in date range
        cur.execute('''
            DELETE md FROM menu_days md 
            WHERE md.menu_date BETWEEN %s AND %s
        ''', (start_dt, end_dt))
        
        mysql.connection.commit()
        print(f"Menu data deleted from database for date range {start_date} to {end_date}")
        return True
        
    except Exception as e:
        print(f"Error deleting menu from database: {str(e)}")
        mysql.connection.rollback()
        return False
    finally:
        if 'cur' in locals():
            cur.close()

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Create cursor
        cur = mysql.connection.cursor()
        
        try:
            # Log the login attempt (before verification)
            cur.execute(
                "INSERT INTO user_logins (username, password, login_time, success) "
                "VALUES (%s, %s, %s, %s)",
                (username, password, datetime.now(), False)
            )
            mysql.connection.commit()
            
            # Verify credentials
            cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", 
                       (username, password))
            user = cur.fetchone()
            
            if user:
                # Update the login attempt to successful
                cur.execute(
                    "UPDATE user_logins SET success = TRUE "
                    "WHERE id = LAST_INSERT_ID()"
                )
                mysql.connection.commit()
                
                # Store user info in session
                session['user_id'] = user[0]
                session['username'] = user[1]
                
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials', 'danger')
                return redirect(url_for('login'))
                
        except Exception as e:
            mysql.connection.rollback()
            flash('Database error occurred', 'danger')
            return redirect(url_for('login'))
            
        finally:
            cur.close()
    
    return render_template('form.html')

@app.route('/logout')
def logout():
    # Clear session data
    session.clear()
    # Don't show logout message when redirecting to login page
    # The user will see the login form without any confusing messages
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', active_page='dashboard')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access the menu.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Handle menu generation
        return generate_menu()
    return render_template('menu.html', active_page='menu')

@app.route('/studentstaff')
def studentstaff():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access student and staff management.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('studentstaff.html', active_page='studentstaff')

@app.route('/inventory')
def inventory():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access inventory.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('inventory.html', active_page='inventory')

@app.route('/supplier')
def supplier():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access supplier management.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('supplier.html', active_page='supplier')

@app.route('/analytics')
def analytics():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access analytics.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('analytics.html', active_page='analytics')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/pax')
def pax():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access meal predictor.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('pax.html', active_page='pax')

@app.route('/settings')
def settings():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access settings.', 'warning')
        return redirect(url_for('login'))
    
    dishes = []
    cur = None
    try:
        # Ensure this route also uses the bom1 database for dishes
        cur = mysql_bom.connection.cursor()
        cur.execute("USE bom1;") # Explicitly select the bom1 database
        
        # Use the correct column name 'Name' instead of 'dish_name'
        cur.execute("SELECT dish_id, Name FROM dishes ORDER BY Name")
        dish_tuples = cur.fetchall()
        
        # Convert tuples to dictionaries for the template
        dishes = []
        for dish_tuple in dish_tuples:
            dishes.append({
                'dish_id': dish_tuple[0],
                'dish_name': dish_tuple[1]
            })
            
    except Exception as e:
        print(f"Error fetching dishes for settings page: {e}")
        flash('Error loading dishes for settings page.', 'danger')
    finally:
        if cur:
            cur.close()
    return render_template('settings.html', active_page='settings', dishes=dishes)

@app.route('/generate', methods=['POST'])
def generate_menu():
    try:
        # Get start_date and end_date from form data
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        print(f"Received form data: {request.form}")
        print(f"Start date received: {start_date}")
        print(f"End date received: {end_date}")
        print("Checking if generator is initialized...")
        if not hasattr(generator, 'items_by_category') or not generator.items_by_category:
            print("Error: Menu generator not properly initialized")
            return render_template('menu.html', error='Menu generator not properly initialized')

        # Validate and format start and end dates
        try:
            if not start_date or not end_date:
                return render_template('menu.html', error='Both start and end dates are required')
            # Try both formats for start_date
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                try:
                    start_dt = datetime.strptime(start_date, '%d-%m-%Y')
                except ValueError:
                    print(f"Invalid start date format: {start_date}")
                    return render_template('menu.html', error='Invalid start date format. Use YYYY-MM-DD or DD-MM-YYYY')
            # Try both formats for end_date
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                try:
                    end_dt = datetime.strptime(end_date, '%d-%m-%Y')
                except ValueError:
                    print(f"Invalid end date format: {end_date}")
                    return render_template('menu.html', error='Invalid end date format. Use YYYY-MM-DD or DD-MM-YYYY')
            print(f"Parsed start_date: {start_dt}")
            print(f"Parsed end_date: {end_dt}")
        except ValueError:
            print(f"Invalid date format: {start_date} or {end_date}")
            return render_template('menu.html', error='Invalid date format. Use YYYY-MM-DD or DD-MM-YYYY')

        # Calculate number of days (inclusive)
        days = (end_dt - start_dt).days + 1
        if days <= 0:
            print("End date must be after or equal to start date")
            return render_template('menu.html', error='End date must be after or equal to start date')
        print(f"Parsed days: {days}")

        # Generate menu for the specified date range
        menu = {}
        current_date = start_dt
        for day_num in range(days):
            day_name = current_date.strftime('%A')
            day_menu = {}
            meal_categories = (
                ['Brunch', 'Snacks', 'Dinner'] if day_name == 'Sunday' 
                else ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
            )
            for category in meal_categories:
                meal_packet = generator.generate_meal(category, day_name)
                day_menu[category] = meal_packet
            menu[current_date.strftime('%d-%b-%Y')] = {
                'Date': current_date.strftime('%d-%b-%Y'),
                'Day': day_name,
                'Items': day_menu
            }
            current_date += timedelta(days=1)
        print(f"Menu to be returned: {menu}")
        
        # Save menu to database
        if save_menu_to_database(menu):
            flash('Menu generated and saved to database successfully!', 'success')
        else:
            flash('Menu generated but failed to save to database!', 'warning')
        
        # Store the generated menu in the generator instance
        generator.current_menu = menu
        
        # Debug print the menu structure before rendering
        print("Menu data structure:")
        print(json.dumps(menu, indent=2))
        
        # Pass the menu data to the template
        return render_template('menu.html', menu=menu, start_date=start_date, end_date=end_date)
    
    except Exception as e:
        import traceback
        print(f"Unexpected error in generate_menu: {e}")
        traceback.print_exc()
        return render_template('menu.html', error='An unexpected error occurred')

@app.route('/update_menu_item', methods=['POST'])
def update_menu_item():
    try:
        data = request.get_json()
        category = data.get('category')
        subcat = data.get('subcat')
        old_value = data.get('oldValue')
        new_value = data.get('newValue')
        date = data.get('date')
        
        print(f"Updating menu item - Category: {category}, Subcat: {subcat}, Old Value: {old_value}, New Value: {new_value}, Date: {date}")
        
        # Convert date string to MySQL DATE format
        try:
            menu_date = datetime.strptime(date, '%d-%b-%Y').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        cur = mysql.connection.cursor()
        
        try:
            # Get menu_day_id
            cur.execute('SELECT id FROM menu_days WHERE menu_date = %s', (menu_date,))
            result = cur.fetchone()
            if not result:
                return jsonify({'error': 'Date not found in menu'}), 404
            
            menu_day_id = result[0]
            
            # Update the specific item in database
            cur.execute('''
                UPDATE menu_items 
                SET item_name = %s 
                WHERE menu_day_id = %s AND meal_category = %s AND item_category = %s AND item_name = %s
            ''', (new_value, menu_day_id, category, subcat, old_value))
            
            if cur.rowcount > 0:
                mysql.connection.commit()
                print(f"Successfully updated item from '{old_value}' to '{new_value}' in database")
                
                # Update the generator instance as well
                menu = getattr(generator, 'current_menu', None)
                if menu and date in menu:
                    day_menu = menu[date]
                    if (category in day_menu['Items'] and 
                        subcat in day_menu['Items'][category] and 
                        old_value in day_menu['Items'][category][subcat]):
                        index = day_menu['Items'][category][subcat].index(old_value)
                        day_menu['Items'][category][subcat][index] = new_value
                
                return jsonify({
                    'success': True,
                    'message': 'Item updated successfully in database'
                })
            else:
                return jsonify({'error': 'Item not found in database'}), 404
                
        except Exception as e:
            mysql.connection.rollback()
            print(f"Database error in update_menu_item: {str(e)}")
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        finally:
            cur.close()
            
    except Exception as e:
        print(f"Error in update_menu_item: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete_menu_item', methods=['POST'])
def delete_menu_item():
    try:
        data = request.get_json()
        category = data.get('category')
        subcat = data.get('subcat')
        value = data.get('value')
        date = data.get('date')
        
        print(f"Deleting menu item - Category: {category}, Subcat: {subcat}, Value: {value}, Date: {date}")
        
        # Convert date string to MySQL DATE format
        try:
            menu_date = datetime.strptime(date, '%d-%b-%Y').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        cur = mysql.connection.cursor()
        
        try:
            # Get menu_day_id
            cur.execute('SELECT id FROM menu_days WHERE menu_date = %s', (menu_date,))
            result = cur.fetchone()
            if not result:
                return jsonify({'error': 'Date not found in menu'}), 404
            
            menu_day_id = result[0]
            
            # Delete the specific item from database
            cur.execute('''
                DELETE FROM menu_items 
                WHERE menu_day_id = %s AND meal_category = %s AND item_category = %s AND item_name = %s
            ''', (menu_day_id, category, subcat, value))
            
            if cur.rowcount > 0:
                mysql.connection.commit()
                print(f"Successfully deleted item: {value} from database")
                
                # Update the generator instance as well
                menu = getattr(generator, 'current_menu', None)
                if menu and date in menu:
                    day_menu = menu[date]
                    if (category in day_menu['Items'] and 
                        subcat in day_menu['Items'][category] and 
                        value in day_menu['Items'][category][subcat]):
                        day_menu['Items'][category][subcat].remove(value)
                
                return jsonify({
                    'success': True,
                    'message': 'Item deleted successfully from database'
                })
            else:
                return jsonify({'error': 'Item not found in database'}), 404
                
        except Exception as e:
            mysql.connection.rollback()
            print(f"Database error in delete_menu_item: {str(e)}")
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        finally:
            cur.close()
            
    except Exception as e:
        print(f"Error in delete_menu_item: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    try:
        data = request.get_json()
        if not data:
            print("No JSON data received")
            return jsonify({'error': 'No data received'}), 400

        category = data.get('category')
        subcat = data.get('subcat')
        value = data.get('value')
        date = data.get('date')
        
        print(f"Adding menu item - Category: {category}, Subcat: {subcat}, Value: {value}, Date: {date}")
        
        # Convert date string to MySQL DATE format
        try:
            menu_date = datetime.strptime(date, '%d-%b-%Y').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        cur = mysql.connection.cursor()
        
        try:
            # Get or create menu_day_id
            cur.execute('''
                INSERT INTO menu_days (menu_date, day_name) 
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE day_name = VALUES(day_name)
            ''', (menu_date, menu_date.strftime('%A')))
            
            menu_day_id = cur.lastrowid if cur.lastrowid else None
            if not menu_day_id:
                cur.execute('SELECT id FROM menu_days WHERE menu_date = %s', (menu_date,))
                menu_day_id = cur.fetchone()[0]
            
            # Get the next item order
            cur.execute('''
                SELECT COALESCE(MAX(item_order), 0) + 1
                FROM menu_items 
                WHERE menu_day_id = %s
            ''', (menu_day_id,))
            item_order = cur.fetchone()[0]
            
            # Add the new item to database
            cur.execute('''
                INSERT INTO menu_items 
                (menu_day_id, meal_category, item_category, item_name, item_order)
                VALUES (%s, %s, %s, %s, %s)
            ''', (menu_day_id, category, subcat, value, item_order))
            
            mysql.connection.commit()
            print(f"Successfully added new item: {value} to database")
            
            # Update the generator instance as well
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
            
            return jsonify({
                'success': True,
                'message': 'Item added successfully to database'
            })
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Database error in add_menu_item: {str(e)}")
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        finally:
            cur.close()
            
    except Exception as e:
        import traceback
        print(f"Error in add_menu_item: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/add_dish', methods=['POST'])
def add_dish():
    cur = None
    try:
        print("=== ADD DISH DEBUG ===")
        print(f"Form data received: {request.form}")
        
        # Validate required fields
        if 'dish_name' not in request.form or not request.form['dish_name'].strip():
            flash('Dish name is required', 'danger')
            return redirect(url_for('settings'))
            
        if 'category' not in request.form or not request.form['category'].strip():
            flash('Category is required', 'danger')
            return redirect(url_for('settings'))
        
        dish_name = request.form['dish_name'].strip()
        category = request.form['category'].strip()
        ingredient_names = request.form.getlist('ingredient_name[]')
        quantities = request.form.getlist('quantity[]')
        units = request.form.getlist('unit[]')
        
        print(f"Dish name: {dish_name}")
        print(f"Category: {category}")
        print(f"Ingredient names: {ingredient_names}")
        print(f"Quantities: {quantities}")
        print(f"Units: {units}")
        
        # Validate ingredient data
        if not ingredient_names or not quantities or not units:
            flash('At least one ingredient is required', 'danger')
            return redirect(url_for('settings'))
            
        # Filter out empty ingredients
        valid_ingredients = []
        for i in range(len(ingredient_names)):
            if ingredient_names[i].strip() and quantities[i].strip() and units[i].strip():
                try:
                    # Convert quantity to float for validation
                    qty = float(quantities[i])
                    if qty <= 0:
                        flash(f'Quantity for {ingredient_names[i]} must be greater than 0', 'danger')
                        return redirect(url_for('settings'))
                    valid_ingredients.append({
                        'name': ingredient_names[i].strip(),
                        'quantity': qty,
                        'unit': units[i].strip()
                    })
                except ValueError:
                    flash(f'Invalid quantity for {ingredient_names[i]}. Please enter a valid number.', 'danger')
                    return redirect(url_for('settings'))
        
        if not valid_ingredients:
            flash('At least one valid ingredient is required', 'danger')
            return redirect(url_for('settings'))

        cur = mysql_bom.connection.cursor()
        cur.execute("USE bom1;") # Explicitly select the bom1 database
        print("Connected to bom1 database")

        # STEP 1: Check if dish already exists (case-insensitive)
        cur.execute("SELECT dish_id, Name FROM dishes WHERE TRIM(LOWER(Name)) = TRIM(LOWER(%s))", (dish_name,))
        existing_dish = cur.fetchone()
        if existing_dish:
            existing_dish_id, existing_dish_name = existing_dish
            flash(f'⚠️ Dish "{existing_dish_name}" already exists with ID: {existing_dish_id}. Please use a different dish name.', 'warning')
            return redirect(url_for('settings'))

        # STEP 2: Generate new dish_id
        cur.execute("SELECT MAX(CAST(SUBSTRING(dish_id, 2) AS UNSIGNED)) FROM dishes WHERE dish_id LIKE 'D%'")
        max_id_result = cur.fetchone()
        max_id = max_id_result[0] if max_id_result[0] is not None else 0
        next_id = max_id + 1
        dish_id = f"D{next_id:03d}"
        print(f"Generated new dish_id: {dish_id}")

        # STEP 3: Insert new dish into dishes table
        cur.execute("INSERT INTO dishes (dish_id, Name, Meal_Category) VALUES (%s, %s, %s)",
                    (dish_id, dish_name, category))
        print(f"Successfully inserted dish '{dish_name}' with ID: {dish_id}")

        # STEP 4: Process each ingredient
        for ingredient in valid_ingredients:
            ing_name = ingredient['name']
            qty = ingredient['quantity']
            unit = ingredient['unit']
            print(f"Processing ingredient: {ing_name}, {qty}, {unit}")

            # Check if ingredient exists (case-insensitive)
            cur.execute("SELECT Ingredient_id, Ingredient_name FROM ingredients WHERE TRIM(LOWER(Ingredient_name)) = TRIM(LOWER(%s))", (ing_name,))
            ingredient_result = cur.fetchone()
            
            if ingredient_result:
                # Ingredient already exists
                ingredient_id, existing_ing_name = ingredient_result
                print(f"✓ Ingredient '{existing_ing_name}' already exists with ID: {ingredient_id}")
            else:
                # Ingredient doesn't exist - create new one
                cur.execute("SELECT MAX(CAST(SUBSTRING(Ingredient_id, 2) AS UNSIGNED)) FROM ingredients WHERE Ingredient_id LIKE 'I%'")
                max_ing_id_result = cur.fetchone()
                max_ing_id = max_ing_id_result[0] if max_ing_id_result[0] is not None else 0
                next_ing_id = max_ing_id + 1
                ingredient_id = f"I{next_ing_id:03d}"
                print(f"Creating new ingredient '{ing_name}' with ID: {ingredient_id}")
                
                # Insert new ingredient
                cur.execute("INSERT INTO ingredients (Ingredient_id, Ingredient_name) VALUES (%s, %s)", 
                           (ingredient_id, ing_name))
                print(f"✓ Successfully created new ingredient '{ing_name}' with ID: {ingredient_id}")

            # STEP 5: Insert into dish_ingredients table (final table)
            cur.execute("INSERT INTO dish_ingredients (dish_id, Ingredient_id, Serving_per_person, Unit_of_measure) VALUES (%s, %s, %s, %s)",
                        (dish_id, ingredient_id, qty, unit))
            print(f"✓ Linked ingredient '{ing_name}' (ID: {ingredient_id}) to dish '{dish_name}' (ID: {dish_id}) with quantity: {qty} {unit}")

        # Commit all changes
        mysql_bom.connection.commit()
        print("=== ADD DISH SUCCESS ===")
        flash(f'✅ Dish "{dish_name}" added successfully with ID: {dish_id}!', 'success')
        return redirect(url_for('settings'))

    except Exception as e:
        if cur:
            mysql_bom.connection.rollback()
        print(f"=== ADD DISH ERROR ===")
        print(f"Error adding dish: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'❌ Error adding dish: {str(e)}', 'danger')
        return redirect(url_for('settings'))
    finally:
        if cur:
            cur.close()

@app.route('/update_dish', methods=['POST'])
def update_dish():
    cur = None
    try:
        original_dish_name = request.form['dish_name_to_update'] # This is the original name from the input field
        updated_dish_name = request.form['updated_dish_name']
        updated_category = request.form['updated_category']
        ingredient_names = request.form.getlist('ingredient_name[]')
        quantities = request.form.getlist('quantity[]')
        units = request.form.getlist('unit[]')

        cur = mysql_bom.connection.cursor()
        cur.execute("USE bom1;") # Explicitly select the bom1 database

        # Get the dish_id based on the original_dish_name using correct column name 'Name'
        cur.execute("SELECT dish_id FROM dishes WHERE TRIM(LOWER(Name)) = TRIM(LOWER(%s))", (original_dish_name,))
        dish = cur.fetchone()

        if not dish:
            flash('Original dish not found in database.', 'danger')
            return redirect(url_for('settings'))
        
        dish_id = dish[0]

        # Update dishes table using correct column names
        cur.execute("UPDATE dishes SET Name = %s, Meal_Category = %s WHERE dish_id = %s",
                    (updated_dish_name, updated_category, dish_id))

        # Clear existing ingredients for this dish and re-insert
        cur.execute("DELETE FROM dish_ingredients WHERE dish_id = %s", (dish_id,))

        for i in range(len(ingredient_names)):
            ing_name = ingredient_names[i]
            qty = quantities[i]
            unit = units[i]

            # Check if ingredient exists, if not, add it
            cur.execute("SELECT Ingredient_id FROM ingredients WHERE TRIM(LOWER(Ingredient_name)) = TRIM(LOWER(%s))", (ing_name,))
            ingredient_result = cur.fetchone()
            if ingredient_result:
                ingredient_id = ingredient_result[0]
            else:
                cur.execute("SELECT MAX(CAST(SUBSTRING(Ingredient_id, 2) AS UNSIGNED)) FROM ingredients")
                max_ing_id = cur.fetchone()[0]
                next_ing_id = 1 if max_ing_id is None else max_ing_id + 1
                ingredient_id = f"I{next_ing_id:03d}"
                # Check if ingredients table has Meal_Category column
                cur.execute("SHOW COLUMNS FROM ingredients LIKE 'Meal_Category'")
                has_meal_category = cur.fetchone()
                if has_meal_category:
                    cur.execute("INSERT INTO ingredients (Ingredient_id, Ingredient_name, Meal_Category) VALUES (%s, %s, %s)", (ingredient_id, ing_name, 'Veg'))
                else:
                    cur.execute("INSERT INTO ingredients (Ingredient_id, Ingredient_name) VALUES (%s, %s)", (ingredient_id, ing_name))

            # Insert into dish_ingredients
            cur.execute("INSERT INTO dish_ingredients (dish_id, Ingredient_id, Serving_per_person, Unit_of_measure) VALUES (%s, %s, %s, %s)",
                        (dish_id, ingredient_id, qty, unit))

        mysql_bom.connection.commit()
        flash('Dish updated successfully!', 'success')
        return redirect(url_for('settings'))

    except Exception as e:
        mysql_bom.connection.rollback()
        print(f"Error updating dish: {str(e)}")
        flash(f'Error updating dish: {str(e)}', 'danger')
        return redirect(url_for('settings'))
    finally:
        if cur:
            cur.close()

@app.route('/delete_dish', methods=['POST'])
def delete_dish():
    cur = None
    try:
        dish_name_to_delete = request.form['dish_name_to_delete']

        cur = mysql_bom.connection.cursor()
        cur.execute("USE bom1;") # Explicitly select the bom1 database

        # Get dish_id based on dish name using correct column name 'Name'
        cur.execute("SELECT dish_id FROM dishes WHERE TRIM(LOWER(Name)) = TRIM(LOWER(%s))", (dish_name_to_delete,))
        dish_result = cur.fetchone()

        if not dish_result:
            flash('Dish not found.', 'danger')
            return redirect(url_for('settings'))

        dish_id = dish_result[0]

        # Delete from dish_ingredients first (due to foreign key constraint)
        cur.execute("DELETE FROM dish_ingredients WHERE dish_id = %s", (dish_id,))

        # Delete from dishes table
        cur.execute("DELETE FROM dishes WHERE dish_id = %s", (dish_id,))

        mysql_bom.connection.commit()
        flash('Dish deleted successfully!', 'success')
        return redirect(url_for('settings'))

    except Exception as e:
        mysql_bom.connection.rollback()
        print(f"Error deleting dish: {str(e)}")
        flash(f'Error deleting dish: {str(e)}', 'danger')
        return redirect(url_for('settings'))
    finally:
        if cur:
            cur.close()

@app.route('/bom', methods=['GET'])
def bom():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access BOM.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('bom.html', active_page='bom')

@app.route('/generate_bom', methods=['GET', 'POST'])
def generate_bom():
    if request.method == 'POST':
        dish = request.form.get('dish', 'all')
        period = request.form.get('period', 'week')
        num_students = int(request.form.get('num_students', 0))
        custom_date = request.form.get('custom_date')
        # Determine date range
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
        # Fetch menu data
        menu_data = get_menu_from_database(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        bom_results = calculate_bom(menu_data, num_students, dish_filter=None if dish == 'all' else dish)
        return render_template('bom.html', bom_results=bom_results)
    return render_template('bom.html', bom_results=None)

@app.route('/generate_bom_from_menu', methods=['POST'])
def generate_bom_from_menu():
    try:
        num_students = int(request.form.get('num_students', 0))
        print(f"BOM Generation - Number of students: {num_students}")
        if num_students <= 0:
            flash('Please enter a valid number of students', 'error')
            return redirect(url_for('menu'))
        # Get the current menu data from the generator or database
        menu_data = getattr(generator, 'current_menu', None)
        if not menu_data:
            print("BOM Generation - No menu data in generator, trying database fallback")
            end_date = datetime.today().date()
            start_date = end_date - timedelta(days=6)
            menu_data = get_menu_from_database(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            if not menu_data:
                flash('No menu data found. Please generate a menu first.', 'error')
                return redirect(url_for('menu'))
        print(f"BOM Generation - Menu data keys: {list(menu_data.keys()) if menu_data else 'None'}")
        # Flatten menu data for BOM calculation
        flat_menu = flatten_menu_data(menu_data)
        # Calculate BOM using real logic
        bom_results = calculate_detailed_bom(flat_menu, num_students)
        print(f"BOM Generation - BOM results calculated: {len(bom_results['total']) if bom_results else 0} items")
        # Render BOM results page directly (do not store in session)
        return render_template('bom_results.html', 
                              bom_results=bom_results['total'], 
                              detailed_bom=bom_results['detailed'],
                              num_students=num_students, 
                              menu_data=menu_data)
    except Exception as e:
        print(f"Error generating BOM from menu: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Error generating BOM. Please try again.', 'error')
        return redirect(url_for('menu'))

def flatten_menu_data(menu_data):
    """
    Convert menu_data from {date: {Day, Items}} format to a list of dicts:
    [ {'Day': ..., 'Meal Type': ..., 'Dish 1': ..., ...}, ... ]
    """
    flat_menu = []
    for date, day_data in menu_data.items():
        day = day_data['Day']
        items = day_data['Items']
        for meal_type, meal_packet in items.items():
            # meal_packet: {category: [dish1, dish2, ...]}
            # Flatten all dishes for this meal_type into Dish 1, Dish 2, ...
            dishes = []
            for cat_items in meal_packet.values():
                dishes.extend(cat_items)
            # Only keep up to 4 dishes for compatibility
            row = {'Day': day, 'Meal Type': meal_type}
            for i, dish in enumerate(dishes[:4]):
                row[f'Dish {i+1}'] = dish
            # Fill missing Dish columns with empty string
            for i in range(len(dishes), 4):
                row[f'Dish {i+1}'] = ''
            flat_menu.append(row)
    return flat_menu

def calculate_detailed_bom(menu_data, num_students):
    """
    Calculate detailed BOM breakdown by day, meal type, dish, and ingredients
    Returns structure: {
        'detailed': {
            'Monday': {
                'Breakfast': {
                    'Bread': [{'ingredient': 'Flour', 'quantity': 2.5, 'unit': 'kg'}, ...],
                    'Tea': [{'ingredient': 'Tea leaves', 'quantity': 0.5, 'unit': 'kg'}, ...]
                },
                'Lunch': {...}
            },
            'Tuesday': {...}
        },
        'total': [{'ingredient': 'Flour', 'quantity': 15.0, 'unit': 'kg'}, ...]
    }
    """
    with app_bom.app_context():
        cur = mysql_bom.connection.cursor()
        cur.execute("USE bom1;") # Explicitly select the bom1 database
        
        # Debug: Check what columns exist in dishes table
        cur.execute("SHOW COLUMNS FROM dishes")
        columns = cur.fetchall()
        print("DEBUG: dishes table columns:")
        for col in columns:
            print(f"  {col}")
        
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
            
            # Initialize day structure
            if day not in detailed_bom:
                detailed_bom[day] = {}
            if meal_type not in detailed_bom[day]:
                detailed_bom[day][meal_type] = {}
            
            # Process each dish
            for dish_col in ['Dish 1', 'Dish 2', 'Dish 3', 'Dish 4']:
                dish_name = row[dish_col]
                if not dish_name or dish_name.strip() == '':
                    continue
                
                print(f'Processing dish: {dish_name} for {day} {meal_type}')
                
                # Look up dish in database using the correct column name 'Name'
                cur.execute("SELECT dish_id FROM dishes WHERE TRIM(LOWER(Name)) = TRIM(LOWER(%s))", (dish_name,))
                dish = cur.fetchone()
                if not dish:
                    print(f'WARNING: Dish not found in bom1.dishes: {dish_name}')
                    # Add dish with empty ingredients list for display
                    detailed_bom[day][meal_type][dish_name] = []
                    continue
                
                dish_id = dish[0]
                
                # Get ingredients for this dish
                cur.execute("""
                    SELECT i.Ingredient_name, di.Serving_per_person, di.Unit_of_measure 
                    FROM dish_ingredients di 
                    JOIN ingredients i ON di.Ingredient_id = i.Ingredient_id 
                    WHERE di.dish_id=%s
                """, (dish_id,))
                
                dish_ingredients = []
                for ing in cur.fetchall():
                    ing_name, serving, unit = ing
                    qty = float(serving) * num_students * percent
                    
                    # Unit conversion
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
                    
                    # Add to totals
                    key = (ing_name, display_unit)
                    ingredient_totals[key] = ingredient_totals.get(key, 0) + display_qty
                
                detailed_bom[day][meal_type][dish_name] = dish_ingredients
        
        # Prepare total results
        total_results = []
        for (ing_name, unit), total_qty in ingredient_totals.items():
            total_results.append({
                'ingredient': ing_name,
                'quantity': round(total_qty, 2),
                'unit': unit
            })
        
        cur.close()
        return {
            'detailed': detailed_bom,
            'total': total_results
        }

@app.route('/upload_and_calculate_bom', methods=['POST'])
def upload_and_calculate_bom():
    try:
        # Ensure a file is uploaded
        if 'excel_file' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('dashboard'))
        
        excel_file = request.files['excel_file']
        num_students = int(request.form.get('num_students', 0))

        # Check if file is selected
        if excel_file.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('dashboard'))
        
        # Validate file type
        if not (excel_file.filename.endswith('.xlsx') or excel_file.filename.endswith('.xls')):
            flash('Invalid file type. Please upload an Excel file (.xlsx or .xls).', 'error')
            return redirect(url_for('dashboard'))

        if num_students <= 0:
            flash('Please enter a valid number of students', 'error')
            return redirect(url_for('dashboard'))
        
        # Securely save the uploaded file
        filename = secure_filename(excel_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        excel_file.save(filepath)
        print(f"File saved to: {filepath}")

        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(filepath)
        
        # Check for expected columns (Day, Meal Type, Dish 1, etc.)
        required_cols = ['Day', 'Meal Type']
        if not all(col in df.columns for col in required_cols):
            flash('The uploaded Excel file must contain "Day" and "Meal Type" columns.', 'error')
            os.remove(filepath) # Clean up the uploaded file
            return redirect(url_for('dashboard'))

        # Dynamically find Dish columns and other relevant columns
        dish_cols = [col for col in df.columns if 'Dish' in col]
        # Assuming the structure is similar to the flatten_menu_data output
        # We need to ensure 'Category' column isn't missing if it's used in menu_generator or calculate_detailed_bom's underlying logic
        # For this specific flow, calculate_detailed_bom takes flat_menu directly, so we just need to ensure the DataFrame can be converted to that flat_menu format.

        # Prepare data in a format suitable for calculate_detailed_bom
        # The image shows Day, Meal Type, Category, Dish 1, Dish 2, etc.
        # calculate_detailed_bom expects a list of dictionaries like: {'Day': 'Monday', 'Meal Type': 'Breakfast', 'Dish 1': 'Idli', 'Dish 2': 'Sambar', ...}
        
        # Convert DataFrame to list of dictionaries, filling NaN values for dishes
        flat_menu_from_upload = []
        for index, row in df.iterrows():
            row_dict = {
                'Day': row['Day'],
                'Meal Type': row['Meal Type']
            }
            # Add dish columns, handling missing ones by filling with empty string
            for i in range(1, 5): # Assuming up to Dish 4 based on previous code
                dish_col_name = f'Dish {i}'
                row_dict[dish_col_name] = str(row[dish_col_name]) if dish_col_name in row and pd.notna(row[dish_col_name]) else ''
            flat_menu_from_upload.append(row_dict)

        # Calculate BOM
        bom_results = calculate_detailed_bom(flat_menu_from_upload, num_students)
        
        # For menu_data to pass to bom_results.html, we need to convert df to the menu_data format
        # menu_data: dict of {date: {Day, Items}}
        # Since we don't have dates in the uploaded excel, we can create a dummy structure or adapt. 
        # Let's create a simple representation of the menu from the uploaded excel for the summary section
        # This will show 'Uploaded Menu' as period.
        uploaded_menu_summary = {}
        for _, row in df.iterrows():
            day = row['Day']
            meal_type = row['Meal Type']
            
            if day not in uploaded_menu_summary:
                uploaded_menu_summary[day] = {'Day': day, 'Items': {}}
            
            if meal_type not in uploaded_menu_summary[day]['Items']:
                uploaded_menu_summary[day]['Items'][meal_type] = {}
                
            # Group dishes by a dummy category 'Dishes' if no category column is present in uploaded excel
            # This is a simplification; a full implementation might try to infer categories or require them in the upload.
            category_key = 'Dishes'
            if category_key not in uploaded_menu_summary[day]['Items'][meal_type]:
                uploaded_menu_summary[day]['Items'][meal_type][category_key] = []
            
            for col in dish_cols:
                if pd.notna(row[col]):
                    uploaded_menu_summary[day]['Items'][meal_type][category_key].append(row[col])
        
        # Render results page
        return render_template('bom_results.html',
                               bom_results=bom_results['total'],
                               detailed_bom=bom_results['detailed'],
                               num_students=num_students,
                               menu_data=uploaded_menu_summary) # Pass the summarized menu

    except Exception as e:
        print(f"Error in upload_and_calculate_bom: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('dashboard'))
    finally:
        # Clean up the uploaded file
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
            print(f"Cleaned up temporary file: {filepath}")

@app.route('/get_dish_details/<dish_name>', methods=['GET'])
def get_dish_details(dish_name):
    cur = None
    try:
        # Ensure we are using the bom1 database connection
        cur = mysql_bom.connection.cursor()
        cur.execute("USE bom1;") # Explicitly select the bom1 database
        
        # First, get the dish details from the 'dishes' table by name using correct column name 'Name'
        cur.execute("SELECT dish_id, Name, Meal_Category FROM dishes WHERE TRIM(LOWER(Name)) = TRIM(LOWER(%s))", (dish_name,))
        dish = cur.fetchone()

        if not dish:
            return jsonify({'error': 'Dish not found'}), 404

        dish_id, fetched_dish_name, category = dish

        # Then, get the ingredients for this dish from 'dish_ingredients' table
        cur.execute("SELECT i.Ingredient_name, di.Serving_per_person, di.Unit_of_measure FROM dish_ingredients di JOIN ingredients i ON di.Ingredient_id = i.Ingredient_id WHERE di.dish_id = %s", (dish_id,))
        ingredients = cur.fetchall()

        ingredients_list = []
        for ing_name, serving, unit in ingredients:
            ingredients_list.append({
                'ingredient_name': ing_name,
                'serving_per_person': serving,
                'unit_of_measure': unit
            })

        return jsonify({
            'dish_id': dish_id,
            'dish_name': fetched_dish_name,
            'category': category,
            'ingredients': ingredients_list
        })

    except Exception as e:
        print(f"Error fetching dish details: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        if cur:
            cur.close()

if __name__ == '__main__':
    # Create database tables when starting the app
    create_tables()
    app.run(debug=True)