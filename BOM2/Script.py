import pandas as pd
import mysql.connector

# Load Excel
df = pd.read_excel("Weekly_Menu_Template.xlsx")

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shaunak43@ra",
    database="bom1"
)
cursor = conn.cursor()

# Insert rows
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO weekly_menu (day, meal_type, dish_1, dish_2, dish_3, dish_4)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (row['Day'], row['Meal Type'], row['Dish 1'], row['Dish 2'], row['Dish 3'], row['Dish 4']))

conn.commit()
cursor.close()
conn.close()
