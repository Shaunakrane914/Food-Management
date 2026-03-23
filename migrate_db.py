import os
from sqlalchemy import create_engine, MetaData, Table, text, event, String, DateTime, Integer, Boolean
from sqlalchemy.dialects.mysql import ENUM, DATETIME, TINYINT

@event.listens_for(Table, "column_reflect")
def column_reflect(inspector, table, column_info):
    t = column_info['type']
    if isinstance(t, ENUM):
        column_info['type'] = String(length=255)
    elif isinstance(t, DATETIME):
        column_info['type'] = DateTime()
    elif isinstance(t, TINYINT):
        if hasattr(t, 'display_width') and t.display_width == 1:
            column_info['type'] = Boolean()
        else:
            column_info['type'] = Integer()
            
    default = column_info.get('default')
    if default is not None and 'ON UPDATE' in str(default).upper():
        column_info['default'] = text('CURRENT_TIMESTAMP')

def migrate():
    # Source DB: MySQL
    mysql_url = "mysql+pymysql://root:mysql@localhost/bom"
    source_engine = create_engine(mysql_url)
    
    # Dest DB: Supabase Postgres
    postgres_url = "postgresql+psycopg2://postgres.qjcpaoxhueijqkqjmhph:shaunak43rane@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"
    dest_engine = create_engine(postgres_url)
    
    # Reflect metadata
    meta = MetaData()
    meta.reflect(bind=source_engine)
    
    print("Reflected MySQL schema. Tables found:", meta.tables.keys())
    
    from sqlalchemy import CheckConstraint
    for table in meta.tables.values():
        table.constraints = {c for c in table.constraints if not isinstance(c, CheckConstraint)}
    
    # Create tables in destination
    # Dropping them first ensures a clean slate
    meta.drop_all(bind=dest_engine)
    meta.create_all(bind=dest_engine)
    
    print("Schema mirrored to PostgreSQL.")

    for table in meta.sorted_tables:
        print(f"Migrating table {table.name}...")
        
        # Read from source
        with source_engine.connect() as src_conn:
            result = src_conn.execute(table.select())
            rows = result.fetchall()
            
        if not rows:
            print(f"  Table {table.name} is empty. Skipping data insertion.")
            continue
            
        # Write to dest
        with dest_engine.begin() as dest_conn:
            insert_data = [dict(row._mapping) for row in rows]
            chunk_size = 500
            for i in range(0, len(insert_data), chunk_size):
                chunk = insert_data[i:i + chunk_size]
                dest_conn.execute(table.insert(), chunk)
        
        print(f"  Successfully migrated {len(rows)} rows for {table.name}.")
        
    # Reset Postgres Sequences for auto-incrementing columns
    print("Resetting primary key sequences...")
    with dest_engine.begin() as dest_conn:
        for table in meta.sorted_tables:
            for column in table.columns:
                if column.primary_key and column.autoincrement == True and str(column.type).upper() in ['INTEGER', 'BIGINT', 'SMALLINT']:
                    seq_name = f"{table.name}_{column.name}_seq"
                    try:
                        dest_conn.execute(text(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX({column.name}) FROM {table.name}), 1), false)"))
                    except Exception as e:
                        print(f"  Could not reset sequence {seq_name}: {e}")
                        
    print("Migration to Supabase essentially completed successfully!")

if __name__ == "__main__":
    migrate()
