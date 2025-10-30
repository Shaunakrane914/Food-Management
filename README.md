# Food Website - FastAPI & ML Setup Guide

## Overview
This is a FastAPI-based food management system that handles menu generation, BOM (Bill of Materials) calculations, inventory management, and includes a machine learning model (Pax ML) to predict meal attendance (pax). The application uses MySQL databases for data storage and SQLite for ML settings.

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

#### Database Configuration (Update Your Credentials!)

**Main Application Database (`rafeedo`):**
- **Location:** `main.py` (search for `get_mysql_connection()`)
- **Update these lines with your MySQL credentials:**
  ```python
  return pymysql.connect(
      host='localhost',
      user='root',           # <-- UPDATE THIS
      password='16042006',   # <-- UPDATE THIS
      db='rafeedo',
      cursorclass=pymysql.cursors.Cursor
  )
  ```

**BOM Database (`bom1`):**
- **Location:** `main.py` (search for `get_bom_connection()`)
- **Update these lines with your MySQL credentials:**
  ```python
  return pymysql.connect(
      host='localhost',
      user='root',           # <-- UPDATE THIS
      password='16042006',   # <-- UPDATE THIS
      db='bom',
      cursorclass=pymysql.cursors.Cursor
  )
  ```

**⚠️ IMPORTANT:**
- Change all default MySQL usernames and passwords before deploying.
- You may also use environment variables for credentials for better security.

### 4. SQL Files Setup

#### For `rafeedo` Database
The main application database (`rafeedo`) uses **auto-created tables**. The application will automatically create the following tables when it starts:
- `users`, `user_logins`, `dishes`, `menu_variations`, `menu_days`, `menu_items`, `dish_ingredients`

**No SQL files need to be imported for the `rafeedo` database.**

#### For `bom1` Database
The BOM database (`bom1`) requires the following tables to be created manually. Use the provided SQL files or execute the following SQL commands:

**Required Tables:**
1. `Dishes` - Contains dish information
2. `Ingredients` - Contains ingredient information
3. `Dish_Ingredients` - Maps dishes to ingredients with quantities
4. `weekly_menu` - Stores weekly menu data

**Sample SQL Structure:**
```sql
-- See previous README for full table creation SQL
```

### 5. Pax ML Model & Settings
- The ML model is trained and saved as `Pax ML/backend/pax_predictor.pkl`.
- ML settings (batch, exam rules, etc.) are stored in `pax_settings.db` (SQLite, auto-created).
- No manual setup needed for ML settings DB.

## Running the Application

### Main FastAPI Application
```bash
uvicorn main:app --reload
```
The application will be available at `http://localhost:8000`

### Pax ML Predictor Usage
- Visit `/pax` for the meal predictor interface.
- Visit `/pax_settings` for ML settings (batch, exam rules, exam dates).
- Both pages are styled to match the dashboard.

## File Structure
```
Food-Website/
├── main.py                 # Main FastAPI application
├── menu_generator.py       # Menu generation logic
├── requirements.txt        # Python dependencies
├── Pax ML/                 # ML model and data
│   ├── backend/            # ML model training code
│   └── frontend/           # (legacy) ML UI
├── BOM2/                  # (Legacy) BOM calculation module
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── uploads/                # File upload directory
└── images/                 # Image assets
```

## Configuration Checklist
- [ ] Update MySQL credentials in `main.py` (`get_mysql_connection` and `get_bom_connection`)
- [ ] (Optional) Set environment variables for sensitive info
- [ ] Ensure `requirements.txt` is installed
- [ ] Create MySQL databases and tables as described above

## Troubleshooting
- **MySQL Connection Error:** Ensure MySQL server is running and credentials are correct
- **Database Not Found:** Create both `rafeedo` and `bom1` databases
- **Missing Tables:** The `rafeedo` tables are auto-created, but `bom1` tables need manual creation
- **Permission Errors:** Ensure MySQL user has proper permissions for both databases

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
- Application errors: Check FastAPI logs and database connectivity
- BOM calculations: Ensure `bom1` database tables are properly populated
- Pax ML: Ensure `pax_predictor.pkl` exists and is accessible 