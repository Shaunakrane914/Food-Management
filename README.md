# Food Website - Database Setup Guide

## Overview
This is a Flask-based food management system that handles menu generation, BOM (Bill of Materials) calculations, and inventory management. The application uses MySQL databases for data storage.

## Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Food-Website
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup

#### Required Databases
The application uses **two separate MySQL databases**:

1. **`rafeedo`** - Main application database
2. **`bom1`** - BOM (Bill of Materials) database

#### Create Databases
```sql
CREATE DATABASE rafeedo;
CREATE DATABASE bom1;
```

#### Database Configuration

**Main Application Database (`rafeedo`):**
- **Location**: `app.py` (lines 15-18)
- **Current Configuration**:
  ```python
  app.config['MYSQL_HOST'] = 'localhost'
  app.config['MYSQL_USER'] = 'root'
  app.config['MYSQL_PASSWORD'] = '16042006'  # UPDATE THIS PASSWORD
  app.config['MYSQL_DB'] = 'rafeedo'
  ```

**BOM Database (`bom1`):**
- **Location**: `app.py` (lines 23-28) and `BOM2/main.py` (lines 8-14)
- **Current Configuration**:
  ```python
  # In app.py
  app_bom.config['MYSQL_HOST'] = 'localhost'
  app_bom.config['MYSQL_USER'] = 'root'
  app_bom.config['MYSQL_PASSWORD'] = '16042006'  # UPDATE THIS PASSWORD
  app_bom.config['MYSQL_DB'] = 'bom1'
  
  # In BOM2/main.py
  host=os.environ.get("MYSQLHOST", "localhost"),
  user=os.environ.get("MYSQLUSER", "root"),
  password=os.environ.get("MYSQLPASSWORD", "Shaunak43@ra"),  # UPDATE THIS PASSWORD
  database=os.environ.get("MYSQLDATABASE", "bom1"),
  ```

### 4. Update MySQL Passwords

**⚠️ IMPORTANT: Update the MySQL passwords in the following files:**

1. **`app.py`** (lines 17 and 26):
   ```python
   app.config['MYSQL_PASSWORD'] = 'YOUR_MYSQL_PASSWORD'
   app_bom.config['MYSQL_PASSWORD'] = 'YOUR_MYSQL_PASSWORD'
   ```

2. **`BOM2/main.py`** (line 11):
   ```python
   password=os.environ.get("MYSQLPASSWORD", "YOUR_MYSQL_PASSWORD"),
   ```

### 5. SQL Files Setup

#### For `rafeedo` Database
The main application database (`rafeedo`) uses **auto-created tables**. The application will automatically create the following tables when it starts:

- `users` - User authentication
- `user_logins` - Login tracking
- `dishes` - Dish information
- `menu_variations` - Menu variations
- `menu_days` - Menu day records
- `menu_items` - Menu item details
- `dish_ingredients` - Dish ingredient mappings

**No SQL files need to be imported for the `rafeedo` database.**

#### For `bom1` Database
The BOM database (`bom1`) requires the following tables to be created manually. You'll need to create SQL files or execute the following SQL commands:

**Required Tables:**
1. `Dishes` - Contains dish information
2. `Ingredients` - Contains ingredient information
3. `Dish_Ingredients` - Maps dishes to ingredients with quantities
4. `weekly_menu` - Stores weekly menu data

**Sample SQL Structure:**
```sql
-- Create Dishes table
CREATE TABLE Dishes (
    dish_id VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Ingredients table
CREATE TABLE Ingredients (
    Ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    Ingredient_name VARCHAR(100) NOT NULL,
    Unit_of_measure VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Dish_Ingredients table
CREATE TABLE Dish_Ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dish_id VARCHAR(10),
    Ingredient_id INT,
    Serving_per_person DECIMAL(10,3),
    Unit_of_measure VARCHAR(20),
    FOREIGN KEY (dish_id) REFERENCES Dishes(dish_id),
    FOREIGN KEY (Ingredient_id) REFERENCES Ingredients(Ingredient_id)
);

-- Create weekly_menu table
CREATE TABLE weekly_menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day VARCHAR(20),
    meal_type VARCHAR(50),
    dish_1 VARCHAR(100),
    dish_2 VARCHAR(100),
    dish_3 VARCHAR(100),
    dish_4 VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. Environment Variables (Optional)
For the BOM2 module, you can set environment variables instead of hardcoding passwords:

```bash
export MYSQLHOST=localhost
export MYSQLUSER=root
export MYSQLPASSWORD=your_password_here
export MYSQLDATABASE=bom1
export MYSQLPORT=3306
```

## Running the Application

### Main Application
```bash
python app.py
```
The application will be available at `http://localhost:5000`

### BOM2 Module (Separate)
```bash
cd BOM2
python main.py
```

## File Structure
```
Food-Website/
├── app.py                 # Main Flask application
├── menu_generator.py      # Menu generation logic
├── requirements.txt       # Python dependencies
├── BOM2/                 # BOM calculation module
│   ├── main.py           # BOM Flask application
│   └── Script.py         # BOM scripts
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS)
├── uploads/              # File upload directory
└── images/               # Image assets
```

## Database Schema Summary

### rafeedo Database (Auto-created)
- User management and authentication
- Menu generation and storage
- Dish management

### bom1 Database (Manual setup required)
- Dish ingredient mappings
- BOM calculations
- Weekly menu storage

## Troubleshooting

### Common Issues:
1. **MySQL Connection Error**: Ensure MySQL server is running and passwords are correctly updated
2. **Database Not Found**: Create both `rafeedo` and `bom1` databases
3. **Missing Tables**: The `rafeedo` database tables are auto-created, but `bom1` tables need manual creation
4. **Permission Errors**: Ensure MySQL user has proper permissions for both databases

### MySQL User Permissions
```sql
GRANT ALL PRIVILEGES ON rafeedo.* TO 'your_username'@'localhost';
GRANT ALL PRIVILEGES ON bom1.* TO 'your_username'@'localhost';
FLUSH PRIVILEGES;
```

## Security Notes
- ⚠️ **Change default passwords** before deploying to production
- Use environment variables for sensitive configuration
- Ensure proper MySQL user permissions
- Consider using a dedicated MySQL user instead of root

## Support
For issues related to:
- Database setup: Check MySQL server status and user permissions
- Application errors: Check Flask logs and database connectivity
- BOM calculations: Ensure `bom1` database tables are properly populated 