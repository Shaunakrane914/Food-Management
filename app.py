from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQLHOST", "localhost"),
        user=os.environ.get("MYSQLUSER", "root"),
        password=os.environ.get("MYSQLPASSWORD", "Shaunak43@ra"),
        database=os.environ.get("MYSQLDATABASE", "BOM"),
        port=int(os.environ.get("MYSQLPORT", 3306))
    )

# Attendance percentages
ATTENDANCE = {
    "breakfast": 0.5,
    "snacks": 0.5,
    "lunch": 0.85,
    "dinner": 0.85,
    "brunch": 0.85  # for Sunday
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'menu_file' in request.files:
            file = request.files['menu_file']
            num_students = int(request.form['num_students'])
            if file:
                filepath = os.path.join('uploads', file.filename)
                file.save(filepath)
                print(f"File saved to {filepath}")

                # Read Excel data
                df = pd.read_excel(filepath)
                # Store the data in session
                session['num_students'] = num_students
                session['menu_data'] = df.to_dict('records')
                return redirect(url_for('edit_menu'))
    return render_template('index.html')

@app.route('/edit_menu', methods=['GET', 'POST'])
def edit_menu():
    if 'menu_data' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Get the edited data
        menu_data = []
        days = request.form.getlist('day[]')
        meal_types = request.form.getlist('meal_type[]')
        dish1s = request.form.getlist('dish_1[]')
        dish2s = request.form.getlist('dish_2[]')
        dish3s = request.form.getlist('dish_3[]')
        dish4s = request.form.getlist('dish_4[]')
        
        for i in range(len(days)):
            menu_data.append({
                'Day': days[i],
                'Meal Type': meal_types[i],
                'Dish 1': dish1s[i],
                'Dish 2': dish2s[i],
                'Dish 3': dish3s[i],
                'Dish 4': dish4s[i]
            })
        
        # Update session data
        session['menu_data'] = menu_data
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM weekly_menu")  # Clear previous data
        for row in menu_data:
            cursor.execute("""
                INSERT INTO weekly_menu (day, meal_type, dish_1, dish_2, dish_3, dish_4)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (row['Day'], row['Meal Type'], row['Dish 1'], row['Dish 2'], row['Dish 3'], row['Dish 4']))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Calculate ingredients with edited data
        results = calculate_ingredients_from_data(menu_data, session['num_students'])
        return render_template('results.html', 
            daily_results=results['daily'], 
            total_results=results['total'], 
            dish_wise_bom=results['dish_wise_bom'])
    
    return render_template('edit_menu.html', menu_data=session['menu_data'])

def get_dish_bom(dish_name, num_students, attendance_percent):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT dish_id FROM Dishes WHERE Name=%s", (dish_name,))
    dish = cursor.fetchone()
    if not dish:
        return None
    
    dish_id = dish['dish_id']
    cursor.execute("SELECT i.Ingredient_name, di.Serving_per_person, di.Unit_of_measure "
                  "FROM Dish_Ingredients di "
                  "JOIN Ingredients i ON di.Ingredient_id = i.Ingredient_id "
                  "WHERE di.dish_id=%s", (dish_id,))
    
    ingredients = []
    for ing in cursor.fetchall():
        qty = float(ing['Serving_per_person']) * num_students * attendance_percent
        ingredients.append({
            'name': ing['Ingredient_name'],
            'quantity': round(qty, 2),
            'unit': ing['Unit_of_measure']
        })
    
    cursor.close()
    return ingredients

def calculate_ingredients_from_data(menu_data, num_students):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    daily_ingredients = {}  # Store ingredients by day
    ingredient_totals = {}  # Store total ingredients
    dish_wise_bom = {}  # Store dish-wise BOM for each day

    for row in menu_data:
        day = row['Day']
        if day not in daily_ingredients:
            daily_ingredients[day] = {}
            
        meal_type = row['Meal Type'].lower()
        percent = ATTENDANCE.get(meal_type, 1)
        
        for dish_col in ['Dish 1', 'Dish 2', 'Dish 3', 'Dish 4']:
            dish_name = row[dish_col]
            if not dish_name:
                continue
                
            cursor.execute("SELECT dish_id FROM Dishes WHERE Name=%s", (dish_name,))
            dish = cursor.fetchone()
            if not dish:
                continue
                
            dish_id = dish['dish_id']
            cursor.execute("SELECT Ingredient_id, Serving_per_person, Unit_of_measure FROM Dish_Ingredients WHERE dish_id=%s", (dish_id,))
            
            for ing in cursor.fetchall():
                qty = float(ing['Serving_per_person']) * num_students * percent
                key = (ing['Ingredient_id'], ing['Unit_of_measure'])
                
                # Add to daily totals
                if key not in daily_ingredients[day]:
                    daily_ingredients[day][key] = 0
                daily_ingredients[day][key] += qty
                
                # Add to overall totals
                ingredient_totals[key] = ingredient_totals.get(key, 0) + qty

    # Process results for both daily and total
    daily_results = {}
    total_results = []
    dish_wise_bom = {}  # Store dish-wise BOM for each day
    
    # Process daily ingredients
    for day, ingredients in daily_ingredients.items():
        daily_results[day] = []
        for (ing_id, unit), qty in ingredients.items():
            cursor.execute("SELECT Ingredient_name FROM Ingredients WHERE Ingredient_id=%s", (ing_id,))
            name = cursor.fetchone()['Ingredient_name']
            
            # Calculate dish-wise BOM for each day
            for row in menu_data:
                if row['Day'] == day:
                    meal_type = row['Meal Type'].lower()
                    percent = ATTENDANCE.get(meal_type, 1)
                    for dish_col in ['Dish 1', 'Dish 2', 'Dish 3', 'Dish 4']:
                        dish_name = row[dish_col]
                        if dish_name:
                            if day not in dish_wise_bom:
                                dish_wise_bom[day] = {}
                            if dish_name not in dish_wise_bom[day]:
                                dish_wise_bom[day][dish_name] = get_dish_bom(dish_name, num_students, percent)
            
            # Unit conversion for daily results
            display_qty = round(qty, 2)
            display_unit = unit
            if unit in ['gm', 'g'] and qty >= 1000:
                display_qty = round(qty / 1000, 2)
                display_unit = 'kg'
            elif unit in ['ml', 'mL'] and qty >= 1000:
                display_qty = round(qty / 1000, 2)
                display_unit = 'L'
            
            daily_results[day].append({
                'ingredient': name,
                'quantity': display_qty,
                'unit': display_unit
            })
    
    # Process total ingredients
    for (ing_id, unit), total_qty in ingredient_totals.items():
        cursor.execute("SELECT Ingredient_name FROM Ingredients WHERE Ingredient_id=%s", (ing_id,))
        name = cursor.fetchone()['Ingredient_name']
        
        # Unit conversion for totals
        display_qty = round(total_qty, 2)
        display_unit = unit
        if unit in ['gm', 'g'] and total_qty >= 1000:
            display_qty = round(total_qty / 1000, 2)
            display_unit = 'kg'
        elif unit in ['ml', 'mL'] and total_qty >= 1000:
            display_qty = round(total_qty / 1000, 2)
            display_unit = 'L'
            
        total_results.append({
            'ingredient': name,
            'quantity': display_qty,
            'unit': display_unit
        })

    cursor.close()
    conn.close()
    return {'daily': daily_results, 'total': total_results, 'dish_wise_bom': dish_wise_bom}

def calculate_ingredients(filepath, num_students):
    df = pd.read_excel(filepath)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    ingredient_totals = {}

    for _, row in df.iterrows():
        day = row['Day']
        meal_type = row['Meal Type'].lower()
        percent = ATTENDANCE.get(meal_type, 1)
        for dish_col in ['Dish 1', 'Dish 2', 'Dish 3', 'Dish 4']:
            dish_name = row[dish_col]
            if pd.isna(dish_name):
                continue
            # Get dish_id
            cursor.execute("SELECT dish_id FROM Dishes WHERE Name=%s", (dish_name,))
            dish = cursor.fetchone()
            if not dish:
                continue
            dish_id = dish['dish_id']
            # Get ingredients for dish
            cursor.execute("SELECT Ingredient_id, Serving_per_person, Unit_of_measure FROM Dish_Ingredients WHERE dish_id=%s", (dish_id,))
            for ing in cursor.fetchall():
                qty = float(ing['Serving_per_person']) * num_students * percent
                key = (ing['Ingredient_id'], ing['Unit_of_measure'])
                ingredient_totals[key] = ingredient_totals.get(key, 0) + qty

    # Get ingredient names
    results = []
    for (ing_id, unit), total_qty in ingredient_totals.items():
        cursor.execute("SELECT Ingredient_name FROM Ingredients WHERE Ingredient_id=%s", (ing_id,))
        name = cursor.fetchone()['Ingredient_name']
        # Unit conversion
        display_qty = round(total_qty, 2)
        display_unit = unit
        # Convert grams to kilograms
        if unit in ['gm', 'g'] and total_qty >= 1000:
            display_qty = round(total_qty / 1000, 2)
            display_unit = 'kg'
        # Convert milliliters to liters
        elif unit in ['ml', 'mL'] and total_qty >= 1000:
            display_qty = round(total_qty / 1000, 2)
            display_unit = 'L'
        results.append({'ingredient': name, 'quantity': display_qty, 'unit': display_unit})

    cursor.close()
    conn.close()
    return results

@app.route('/dish_wise_bom')
def dish_wise_bom():
    if 'menu_data' not in session:
        return redirect(url_for('index'))
    
    # Calculate ingredients with the stored data
    results = calculate_ingredients_from_data(session['menu_data'], session['num_students'])
    return render_template('dish_wise_bom.html', dish_wise_bom=results['dish_wise_bom'])

if __name__ == '__main__':
    app.run(debug=True)