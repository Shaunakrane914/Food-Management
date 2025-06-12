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
        # Initialize meal packet with specific categories for Sunday Brunch
        meal_packet = {}
        if category == 'Brunch' and day == 'Sunday':
            meal_packet = {
                'Main Course': [],
                'Side Serving': [],
                'Beverages': [],
                'Salad': []
            }
            
            # Get data for Sunday Brunch
            day_and_meal_data = self.menu_data[(self.menu_data['Day'] == day) & (self.menu_data['Meal Type'] == category)]
            
            if not day_and_meal_data.empty:
                # Process each row found for Sunday Brunch
                for index, row in day_and_meal_data.iterrows():
                    if 'Category' in row.index and pd.notna(row['Category']):
                        excel_category = row['Category']
                        
                        # Map Excel category to expected meal_packet category
                        mapped_category = None
                        if excel_category == 'Main Course':
                            mapped_category = 'Main Course'
                        elif excel_category == 'Sides':
                            mapped_category = 'Side Serving' # Map 'Sides' from Excel to 'Side Serving'
                        elif excel_category == 'Beverages':
                            mapped_category = 'Beverages'
                        elif excel_category == 'Salad':
                            mapped_category = 'Salad'

                        if mapped_category:
                            # Get all item columns (Item1, Item2, etc.) for this row
                            item_columns = [col for col in row.index if col.startswith('Item')]
                            # Collect all non-null items from all identified item columns for this row
                            items = []
                            for col in item_columns:
                                if col in row.index and pd.notna(row[col]):
                                     items.append(row[col])
                            # Add collected items to the corresponding brunch category in meal_packet
                            if items:
                                meal_packet[mapped_category].extend(items)
                        else:
                             pass
                    else:
                        pass
            
            return meal_packet
        
        # For non-brunch meals, use the original logic
        day_and_meal_data = self.menu_data[(self.menu_data['Day'] == day) & (self.menu_data['Meal Type'] == category)]
        
        if day_and_meal_data.empty:
            return meal_packet
            
        # Process each row found for this day and meal type
        for index, row in day_and_meal_data.iterrows():
            if 'Category' in row.index and pd.notna(row['Category']):
                excel_category = row['Category']
                
                # Get all item columns (Item1, Item2, etc.) for this row
                item_columns = [col for col in row.index if col.startswith('Item')]
                # Collect all non-null items from all identified item columns for this row
                items = []
                for col in item_columns:
                    if col in row.index and pd.notna(row[col]):
                         items.append(row[col])
                # Add collected items to the corresponding category in meal_packet
                if items:
                    if excel_category not in meal_packet:
                        meal_packet[excel_category] = []
                    meal_packet[excel_category].extend(items)
        
        return meal_packet

    def generate_menu(self, start_date, num_days):
        generated_menus = []
        current_date = datetime.strptime(start_date, '%d-%b-%Y')
        
        for day_offset in range(num_days):
            menu_date = current_date + timedelta(days=day_offset)
            day_name = menu_date.strftime('%A')
            
            menu_day_data = {
                'Date': menu_date.strftime('%d-%b-%Y'),
                'Day': day_name,
                'Items': {}
            }
            
            # Determine meal categories for the day
            if day_name == 'Sunday':
                # For Sunday, generate Brunch, Snacks, and Dinner
                day_categories_to_generate = ['Brunch', 'Snacks', 'Dinner']
            else:
                # For other days, generate Breakfast, Lunch, Snacks', and Dinner
                day_categories_to_generate = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
            
            # Generate menu for each determined category
            for category in day_categories_to_generate:
                try:
                    # Pass the specific category and day name to generate_meal
                    meal_packet = self.generate_meal(category, day_name)
                    menu_day_data['Items'][category] = meal_packet
                except Exception as e:
                    menu_day_data['Items'][category] = {}
            
            generated_menus.append(menu_day_data)
        
        return generated_menus

    def format_menu(self, menu):
        output = []
        # Combine date and day in the header
        output.append(f"{menu['Date']} ({menu['Day']})")
        
        # Determine which categories to display based on the day
        if menu['Day'] == 'Sunday':
            # For Sunday, display Brunch (combined Breakfast and Lunch), Snacks, and Dinner
            display_categories = ['Brunch', 'Snacks', 'Dinner']
        else:
            # For other days, display all categories that exist in the data
            display_categories = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
        
        # Only display categories that are in the menu items
        for category in display_categories:
            if category not in menu['Items']:
                continue
                
            output.append(f"\n{category}:")
            
            # Display items by their Excel categories
            # For Brunch, we display by the mapped categories
            if category == 'Brunch' and menu['Day'] == 'Sunday':
                 for mapped_category, items in menu['Items'][category].items():
                    if items:  # Only display non-empty categories
                        output.append(f"  {mapped_category}:")
                        # Display each item on a new line with a bullet point
                        for item in items:
                            output.append(f"    • {item}")
            else: # For other meals/days, display by Excel categories
                for excel_category, items in menu['Items'][category].items():
                    if items:  # Only display non-empty categories
                        output.append(f"  {excel_category}:")
                        # Display each item on a new line with a bullet point
                        for item in items:
                            output.append(f"    • {item}")
        
        return '\n'.join(output)

    def prepare_data(self, data_file):
        try:
            # Read the Excel file
            df = pd.read_excel(data_file)
            
            # Store the entire dataframe for date-based lookup
            self.menu_data = df
            
        except Exception as e:
            print(f"Error preparing data: {e}")
            import traceback
            traceback.print_exc()
            raise

