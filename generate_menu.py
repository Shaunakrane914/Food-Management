from menu_generator import IndianMenuGenerator
from datetime import datetime

# Initialize generator
generator = IndianMenuGenerator()

# Prepare data from your Excel file - Updated file name
generator.prepare_data('Final Menu Modified.xlsx')

# Get today's date
start_date = datetime.now().strftime('%d-%b-%Y')

# Generate menu for 7 days
generated_menus = generator.generate_menu(start_date, 7)

# Print the menus
for menu in generated_menus:
    print(generator.format_menu(menu))
    print('\n' + '-'*50 + '\n')