# Class to handle menu data structure
class MenuData:
    def __init__(self):
        self.categories = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
        self.items_by_category = {cat: set() for cat in self.categories}
    
    def add_menu_day(self, date, day, menu_items):
        """Add menu items for a specific day"""
        for category, items in menu_items.items():
            if category in self.items_by_category:
                self.items_by_category[category].update(items)