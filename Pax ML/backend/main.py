from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
from sqlalchemy.orm import Session
from .database import SessionLocal, BatchSetting, ExamRule, ExamDate, initialize_default_batches
import pandas as pd
import datetime
import os
import difflib
import traceback
import mysql.connector

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Load ML model with error handling
try:
    ml_bundle = joblib.load('backend/pax_predictor.pkl')
    ml_model = ml_bundle['model']
    ml_columns = ml_bundle['columns']
    unique_dish_df = ml_bundle.get('unique_dish_df')
    pax_long = ml_bundle.get('pax_long')
except Exception as e:
    ml_model = None
    ml_columns = []
    unique_dish_df = None
    pax_long = None

# Initialize default batch settings if needed
initialize_default_batches()

# Load unique dish mapping and historical pax data for fallback logic
UNIQUE_DISH_CSV = os.path.join('..', 'Unique Dish.csv') if not os.path.exists('Pax ML/Unique Dish.csv') else 'Pax ML/Unique Dish.csv'
PAX_CSV = os.path.join('..', 'Pax ML (1).csv') if not os.path.exists('Pax ML/Pax ML (1).csv') else 'Pax ML/Pax ML (1).csv'

# Pydantic models
class PredictRequest(BaseModel):
    total_present: int
    date: str  # YYYY-MM-DD
    is_exam: bool = False
    exam_time: str = None

class PredictResponse(BaseModel):
    breakfast: int
    brunch: int
    lunch: int
    snacks: int
    dinner: int
    notes: list[str] = []

class BatchSettingOut(BaseModel):
    batch_name: str
    total_count: int
    weekend_stay_percent: float
    class Config:
        orm_mode = True

class ExamDateIn(BaseModel):
    date: str  # YYYY-MM-DD
    exam_time: str

class ExamDateOut(BaseModel):
    date: str
    exam_time: str
    class Config:
        orm_mode = True

@app.post("/predict", response_model=PredictResponse)
def predict_pax(req: PredictRequest, db: Session = Depends(get_db)):
    if ml_model is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ML model not loaded. Please train the model.")
    # Parse date
    date_obj = datetime.datetime.strptime(req.date, "%Y-%m-%d")
    day_name = date_obj.strftime("%A")
    is_weekend = int(day_name in ["Saturday", "Sunday"])
    is_sunday = int(day_name == "Sunday")

    # Check if this date is an exam date
    exam_date = db.query(ExamDate).filter(ExamDate.date == req.date).first()
    is_exam = 1 if exam_date else 0
    exam_time = exam_date.exam_time if exam_date else "none"

    # Fetch batch settings from DB
    batches = db.query(BatchSetting).all()
    if not batches:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Batch settings not initialized. Please set up batch settings in /settings/batches.")
    total_count = sum(b.total_count for b in batches)
    batch_features = {}
    for b in batches:
        percent = b.total_count / total_count if total_count else 0
        present = req.total_present * percent
        if is_weekend:
            present *= b.weekend_stay_percent
        batch_features[f"{b.batch_name.lower()}_present"] = present

    # Prepare features for ML model
    features = {
        "is_weekend": is_weekend,
        "is_sunday": is_sunday,
        "is_exam": is_exam,
        "exam_time_none": 0,  # will be set below
    }
    features.update(batch_features)
    # One-hot encode day
    features[f"Day_{day_name}"] = 1
    # One-hot encode exam_time, handle unseen values
    exam_time_key = f"exam_time_{exam_time}" if is_exam and exam_time and f"exam_time_{exam_time}" in ml_columns else "exam_time_none"
    features[exam_time_key] = 1
    # Fill missing columns
    for col in ml_columns:
        if col not in features:
            features[col] = 0
    X = pd.DataFrame([features])[ml_columns]
    # Predict
    pred = ml_model.predict(X)[0]
    notes = []
    # Apply exam rules if needed
    if is_exam and exam_time != "none":
        rules = db.query(ExamRule).filter(ExamRule.exam_time == exam_time).all()
        for rule in rules:
            idx = ["breakfast", "brunch", "lunch", "snacks", "dinner"].index(rule.meal.lower())
            pred[idx] = int(pred[idx] * (1 - rule.reduction_percent))
            notes.append(f"Exam rule applied: {int(rule.reduction_percent*100)}% off {rule.meal}")
    # Round and return
    return PredictResponse(
        breakfast=int(round(pred[0])),
        brunch=int(round(pred[1])),
        lunch=int(round(pred[2])),
        snacks=int(round(pred[3])),
        dinner=int(round(pred[4])),
        notes=notes
    )

# Settings endpoints (simplified)
class BatchSettingIn(BaseModel):
    batch_name: str
    total_count: int
    weekend_stay_percent: float

@app.get("/settings/batches", response_model=list[BatchSettingOut])
def get_batches(db: Session = Depends(get_db)):
    return db.query(BatchSetting).all()

@app.post("/settings/batches")
def set_batch(batch: BatchSettingIn, db: Session = Depends(get_db)):
    obj = db.query(BatchSetting).filter(BatchSetting.batch_name == batch.batch_name).first()
    if obj:
        obj.total_count = batch.total_count
        obj.weekend_stay_percent = batch.weekend_stay_percent
    else:
        obj = BatchSetting(**batch.dict())
        db.add(obj)
    db.commit()
    return {"success": True}

class ExamRuleIn(BaseModel):
    exam_time: str
    meal: str
    reduction_percent: float

class ExamRuleOut(BaseModel):
    exam_time: str
    meal: str
    reduction_percent: float
    class Config:
        orm_mode = True

@app.get("/settings/exam_rules", response_model=list[ExamRuleOut])
def get_exam_rules(db: Session = Depends(get_db)):
    return db.query(ExamRule).all()

@app.post("/settings/exam_rules")
def set_exam_rule(rule: ExamRuleIn, db: Session = Depends(get_db)):
    obj = ExamRule(**rule.dict())
    db.add(obj)
    db.commit()
    return {"success": True}

@app.get("/settings/exam_dates", response_model=list[ExamDateOut])
def get_exam_dates(db: Session = Depends(get_db)):
    return db.query(ExamDate).all()

@app.post("/settings/exam_dates")
def add_exam_date(exam: ExamDateIn, db: Session = Depends(get_db)):
    obj = ExamDate(**exam.dict())
    db.add(obj)
    db.commit()
    return {"success": True}

@app.delete("/settings/exam_dates/{date}")
def delete_exam_date(date: str, db: Session = Depends(get_db)):
    obj = db.query(ExamDate).filter(ExamDate.date == date).first()
    if obj:
        db.delete(obj)
        db.commit()
    return {"success": True}

@app.get("/")
def read_root():
    return {"message": "Canteen Pax Predictor Backend is running."} 

# --- New endpoint for meal-wise pax prediction with fallback logic ---
from typing import List, Dict, Any

class MealPaxRequest(BaseModel):
    menu: List[Dict[str, Any]]  # Each dict: {date, day, meal_type, unique_dish}

class MealPaxResponse(BaseModel):
    predictions: List[Dict[str, Any]]  # Each dict: {date, day, meal_type, unique_dish, predicted_pax, method}

@app.post("/predict_meal_pax", response_model=MealPaxResponse)
def predict_meal_pax(req: MealPaxRequest):
    import pandas as pd
    results = []
    # Load CSVs (adjust file paths as needed)
    try:
        unique_dish_df = pd.read_csv('Pax ML/Unique Dish.csv', skipinitialspace=True)
    except Exception as e:
        unique_dish_df = None
    try:
        pax_df = pd.read_csv('Pax ML/Pax ML (1).csv', skipinitialspace=True)
    except Exception as e:
        pax_df = None
    for entry in req.menu:
        try:
            date = pd.to_datetime(entry['date']).date() if 'date' in entry and entry['date'] else None
            day = entry.get('day', None)
            meal_type = entry.get('meal_type', None)
            unique_dish = entry.get('unique_dish', None)
            method = None
            predicted_pax = None
            if not (date and day and meal_type and unique_dish):
                results.append({
                    'date': str(date) if date else None,
                    'day': day,
                    'meal_type': meal_type,
                    'unique_dish': unique_dish,
                    'predicted_pax': 'no_data',
                    'method': 'no_data'
                })
                continue
            found_csv = False
            if unique_dish_df is not None and pax_df is not None:
                mask = (
                    (unique_dish_df['Date'] == str(date)) &
                    (unique_dish_df['Day'].str.lower().str.strip() == str(day).lower().strip()) &
                    (unique_dish_df['Meal Type'].str.lower().str.strip() == str(meal_type).lower().strip()) &
                    (unique_dish_df['UniqueDish'].str.lower().str.strip() == str(unique_dish).lower().strip())
                )
                if unique_dish_df[mask].shape[0] > 0:
                    pax_mask = (
                        (pax_df['Date'] == str(date)) &
                        (pax_df['Day'].str.lower().str.strip() == str(day).lower().strip()) &
                        (pax_df['Meal Type'].str.lower().str.strip() == str(meal_type).lower().strip())
                    )
                    pax_val = pax_df[pax_mask]['Pax']
                    if not pax_val.empty:
                        predicted_pax = int(round(pax_val.values[0]))
                        method = 'csv_lookup'
                        found_csv = True
            if not found_csv and 'ml_model' in globals() and ml_model is not None:
                features = {col: 0 for col in ml_columns}
                # Always parse date and convert to ordinal for DateOrdinal feature
                if 'DateOrdinal' in features and date:
                    features['DateOrdinal'] = pd.to_datetime(date).toordinal()
                dish_col = None
                if unique_dish:
                    norm_dish = unique_dish.strip().lower()
                    for col in ml_columns:
                        if col.strip().lower() == norm_dish:
                            dish_col = col
                            break
                if dish_col:
                    features[dish_col] = 1
                if f"Meal Type_{meal_type}" in features:
                    features[f"Meal Type_{meal_type}"] = 1
                if f"Day_{day}" in features:
                    features[f"Day_{day}"] = 1
                try:
                    predicted_pax = int(ml_model.predict([list(features.values())])[0])
                    method = 'ml'
                except Exception:
                    predicted_pax = None
            if predicted_pax is None:
                predicted_pax = 'no_data'
                method = 'no_data'
            results.append({
                'date': str(date) if date else None,
                'day': day,
                'meal_type': meal_type,
                'unique_dish': unique_dish,
                'predicted_pax': predicted_pax,
                'method': method
            })
        except Exception:
            results.append({
                'date': entry.get('date', None),
                'day': entry.get('day', None),
                'meal_type': entry.get('meal_type', None),
                'unique_dish': entry.get('unique_dish', None),
                'predicted_pax': 'error',
                'method': 'error'
            })
    return {'predictions': results} 

# --- Inventory and BOM Endpoints ---
def get_inventory_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="16042006",
        database="bom"
    )

class InventoryUpdateRequest(BaseModel):
    ingredient_id: str
    new_quantity: float

class BOMItem(BaseModel):
    ingredient_id: str
    quantity: float

@app.get("/inventory")
def get_inventory():
    conn = get_inventory_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ingredient_inventory")
    inventory = cursor.fetchall()
    cursor.close()
    conn.close()
    return inventory

@app.post("/inventory/update")
def update_inventory(req: InventoryUpdateRequest):
    conn = get_inventory_db_connection()
    cursor = conn.cursor()
    # Get old quantity for logging
    cursor.execute("SELECT quantity FROM ingredient_inventory WHERE ingredient_id = %s", (req.ingredient_id,))
    old_qty = cursor.fetchone()
    old_qty = old_qty[0] if old_qty else None
    cursor.execute(
        "UPDATE ingredient_inventory SET quantity = %s WHERE ingredient_id = %s",
        (req.new_quantity, req.ingredient_id)
    )
    # Log the manual edit
    change_amount = req.new_quantity - (old_qty if old_qty is not None else 0)
    cursor.execute(
        "INSERT INTO inventory_activity (ingredient_id, change_amount, action, note) VALUES (%s, %s, %s, %s)",
        (req.ingredient_id, change_amount, 'manual edit', 'Manual inventory update')
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "success"}

@app.post("/bom/finalize")
def finalize_bom(bom: list[BOMItem] = Body(...)):
    conn = get_inventory_db_connection()
    cursor = conn.cursor()
    for item in bom:
        # Subtract from inventory
        cursor.execute(
            "UPDATE ingredient_inventory SET quantity = quantity - %s WHERE ingredient_id = %s",
            (item.quantity, item.ingredient_id)
        )
        # Log the subtraction
        cursor.execute(
            "INSERT INTO inventory_activity (ingredient_id, change_amount, action, note) VALUES (%s, %s, %s, %s)",
            (item.ingredient_id, -item.quantity, 'subtracted', 'BOM finalized')
        )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "success"}

@app.get("/inventory/activity")
def get_inventory_activity():
    conn = get_inventory_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventory_activity ORDER BY timestamp DESC")
    activity = cursor.fetchall()
    cursor.close()
    conn.close()
    return activity 