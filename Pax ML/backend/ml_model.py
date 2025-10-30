import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import numpy as np
from datetime import datetime

# Load unique dish mapping and pax data
unique_dish_df = pd.read_csv('Pax ML/Unique Dish.csv', header=None, names=['Date', 'Day', 'Meal Type', 'UniqueDish'])
unique_dish_df = unique_dish_df.reset_index(drop=True)
pax_df = pd.read_csv('Pax ML/Pax ML (1).csv')
pax_df = pax_df.rename(columns=lambda x: x.strip())
pax_df = pax_df[~pax_df['Sr.No'].astype(str).str.contains('Total', na=False)]

# Standardize date format for merging
unique_dish_df['Date'] = pd.to_datetime(unique_dish_df['Date'], errors='coerce').dt.date
pax_df['Date'] = pd.to_datetime(pax_df['Date'], errors='coerce').dt.date

# Melt pax_df to long format for merging
meal_columns = ['Breakfast', 'Brunch', 'Lunch', 'Snacks', 'Dinner']
pax_long = pax_df.melt(
    id_vars=['Date', 'Day'],
    value_vars=meal_columns,
    var_name='Meal Type',
    value_name='Pax'
)
pax_long = pax_long.dropna(subset=['Pax'])
pax_long['Meal Type'] = pax_long['Meal Type'].str.strip().replace({' Snacks': 'Snacks'})
unique_dish_df['Meal Type'] = unique_dish_df['Meal Type'].str.strip().replace({' Snacks': 'Snacks'})

# Merge unique dish and pax data on Date, Day, Meal Type
merged = pd.merge(unique_dish_df, pax_long, on=['Date', 'Day', 'Meal Type'], how='inner')

# Add date as ordinal feature
merged['DateOrdinal'] = pd.to_datetime(merged['Date']).map(datetime.toordinal)

# One-hot encode the unique dish, meal type, and day (no prefix or underscore for UniqueDish)
merged = pd.get_dummies(
    merged,
    columns=['UniqueDish', 'Meal Type', 'Day'],
    prefix=['', 'Meal Type', 'Day'],
    prefix_sep=['', '_', '_']
)

# Features and target
feature_cols = [col for col in merged.columns if col not in ['Date', 'Pax']]
X = merged[feature_cols]
y = merged['Pax']

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model, columns, and feature info
joblib.dump({
    'model': model,
    'columns': list(X.columns),
    'unique_dish_df': unique_dish_df,
    'pax_long': pax_long,
    'date_feature': 'DateOrdinal',
}, 'Pax ML/backend/pax_predictor.pkl')

print('Model trained and saved with date feature and dish columns as dish name only.') 