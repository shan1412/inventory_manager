# utils.py
import joblib
from datetime import datetime
from database import db
from models import DemandPrediction

def load_model(model_path):
    try:
        model = joblib.load(model_path)
        print(f"Model loaded from {model_path}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def store_prediction(product_id, predicted_demand):
    prediction = DemandPrediction(
        name=product_id,
        demand=predicted_demand,
        date=datetime.now()
    )
    db.session.add(prediction)
    db.session.commit()
