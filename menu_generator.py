import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import random

class IndianMenuGenerator:
    def __init__(self):
        self.categories = {
            'Weekday': ['Breakfast', 'Lunch', 'Snacks', 'Dinner'],
            'Sunday': ['Brunch', 'Snacks', 'Dinner']
        }
        self.items_by_category = {cat: {} for cat in ['Breakfast', 'Brunch', 'Lunch', 'Snacks', 'Dinner']}
        self.meal_combinations = defaultdict(list)
        self.day_patterns = {}
        self.used_combinations = defaultdict(set)  # Track used combinations
        self.current_week_start = None  # Track week start date
        
        # Initialize with mandatory items for each category
        self.mandatory_items = {
            'Breakfast': ['Tea', 'Coffee', 'Bread'],
            'Lunch': ['Chapati', 'Rice', 'Dal'],
            'Dinner': ['Chapati', 'Rice', 'Dal'],
            'Snacks': ['Tea', 'Coffee'],
            'Brunch': ['Tea', 'Coffee', 'Poha']
        }
        
        # Initialize meal combinations with mandatory items
        for category, items in self.mandatory_items.items():
            self.meal_combinations[category].append(items)

    def generate_meal(self, category, day):
        meal_items = []
        df = self.menu_data.copy()
        if 'Day' in df.columns and 'Meal Type' in df.columns:
            df['Day'] = df['Day'].astype(str).str.strip().str.lower()
            df['Meal Type'] = df['Meal Type'].astype(str).str.strip().str.lower()
        day_and_meal_data = df[
            (df['Day'] == day.strip().lower()) &
            (df['Meal Type'] == category.strip().lower())
        ]
        if day_and_meal_data.empty:
            return meal_items
        item_columns = [col for col in day_and_meal_data.columns if col.strip().lower().replace(' ', '').startswith('item')]
        for _, row in day_and_meal_data.iterrows():
            for col in item_columns:
                if col in row.index and pd.notna(row[col]) and str(row[col]).strip():
                    meal_items.append(str(row[col]).strip())
        return meal_items

    def generate_menu(self):
        generated_menus = []
        # Normalize columns
        self.menu_data['Day'] = self.menu_data['Day'].astype(str).str.strip().str.capitalize()
        self.menu_data['Meal Type'] = self.menu_data['Meal Type'].astype(str).str.strip().str.capitalize()
        self.menu_data['Date'] = self.menu_data['Date'].astype(str).str.strip()
        # Days of the week in order
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        meal_types = ['Breakfast', 'Lunch', 'Snacks', 'Dinner', 'Brunch']
        for day_name in days_of_week:
            if day_name == 'Sunday':
                # For each unique Sunday (date), only use the first row for each meal type
                sunday_rows = self.menu_data[self.menu_data['Day'] == 'Sunday']
                unique_sundays = sunday_rows.drop_duplicates(subset=['Date', 'Day'])[['Date', 'Day']].values.tolist()
                for date, _ in unique_sundays:
                    menu_day_data = {
                        'Day': 'Sunday',
                        'Items': {}
                    }
                    for meal_type in meal_types:
                        meal_row = self.menu_data[(self.menu_data['Date'] == date) & (self.menu_data['Day'] == 'Sunday') & (self.menu_data['Meal Type'] == meal_type)]
                        if meal_row.empty:
                            continue
                        first_meal_row = meal_row.iloc[0]
                        item_cols = [col for col in meal_row.columns if col.lower().replace(' ', '').startswith('item')]
                        meal_items = []
                        for col in item_cols:
                            dish = str(first_meal_row[col]).strip()
                            if dish and dish.lower() != 'nan':
                                meal_items.append(dish)
                        menu_day_data['Items'][meal_type] = meal_items
                    generated_menus.append(menu_day_data)
            else:
                # Only use the first (date, day) pair for each weekday
                day_rows = self.menu_data[self.menu_data['Day'] == day_name]
                if day_rows.empty:
                    continue
                first_row = day_rows.iloc[0]
                date = first_row['Date']
                menu_day_data = {
                    'Day': day_name,
                    'Items': {}
                }
                for meal_type in meal_types:
                    meal_row = self.menu_data[(self.menu_data['Date'] == date) & (self.menu_data['Day'] == day_name) & (self.menu_data['Meal Type'] == meal_type)]
                    if meal_row.empty:
                        continue
                    first_meal_row = meal_row.iloc[0]
                    item_cols = [col for col in meal_row.columns if col.lower().replace(' ', '').startswith('item')]
                    meal_items = []
                    for col in item_cols:
                        dish = str(first_meal_row[col]).strip()
                        if dish and dish.lower() != 'nan':
                            meal_items.append(dish)
                    menu_day_data['Items'][meal_type] = meal_items
                generated_menus.append(menu_day_data)
        return generated_menus

    def format_menu(self, menu):
        output = []
        output.append(f"{menu['Date']} ({menu['Day']})")
        if menu['Day'] == 'Sunday':
            display_categories = ['Brunch', 'Snacks', 'Dinner']
        else:
            display_categories = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
        for category in display_categories:
            if category not in menu['Items']:
                continue
            output.append(f"\n{category}:")
            items = menu['Items'][category]
            for item in items:
                output.append(f"  • {item}")
        return '\n'.join(output)

    def prepare_data(self, data_file):
        try:
            df = pd.read_excel(data_file)
            self.menu_data = df
        except Exception as e:
            raise

