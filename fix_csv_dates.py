import pandas as pd
import os

# List of CSV files to fix
target_files = [
    'Pax ML/Pax ML (1).csv',
    'Pax ML/Unique Dish.csv',
]

def fix_csv_date_column(csv_path):
    print(f'Processing {csv_path}...')
    df = pd.read_csv(csv_path)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        df.to_csv(csv_path, index=False)
        print(f'  Fixed Date column in {csv_path}')
    else:
        # For Unique Dish.csv, may not have headers
        # Try to fix first column if it looks like a date
        first_col = df.columns[0]
        try:
            df[first_col] = pd.to_datetime(df[first_col], errors='coerce').dt.strftime('%Y-%m-%d')
            df.to_csv(csv_path, index=False, header=False)
            print(f'  Fixed first column as Date in {csv_path}')
        except Exception as e:
            print(f'  Could not fix {csv_path}: {e}')

if __name__ == '__main__':
    for file in target_files:
        if os.path.exists(file):
            fix_csv_date_column(file)
        else:
            print(f'File not found: {file}') 