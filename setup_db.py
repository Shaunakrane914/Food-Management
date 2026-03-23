import pymysql

def setup_databases():
    # Connect without database specified to create them
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='mysql'
    )
    
    try:
        cur = conn.cursor()
        
        # Create databases
        cur.execute("CREATE DATABASE IF NOT EXISTS rafeedo")
        cur.execute("CREATE DATABASE IF NOT EXISTS bom")
        print("Databases 'rafeedo' and 'bom' created or already exist.")
        
        # Select 'bom' database for table creation
        conn.select_db('bom')
        
        # Read and execute SQL files for 'bom' database
        sql_files = [
            'bom_ingredients.sql',
            'bom_dishes.sql',
            'bom_dish_ingredients.sql',
            'bom_bom_calculations.sql',
            'bom_bom_ingredients.sql',
            'bom_ingredient_inventory.sql'
        ]
        
        for file in sql_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    sql = f.read()
                    # Simple split by semicolon (might not be perfect for all SQL but works for basic dumps)
                    # A better way is needed if there are complex triggers/procedures
                    for statement in sql.split(';'):
                        if statement.strip():
                            cur.execute(statement)
                print(f"Executed {file}")
            except Exception as e:
                print(f"Error executing {file}: {e}")
                
        conn.commit()
    except Exception as e:
        print(f"Setup failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    setup_databases()
