# inventory.py
from database import db
from models import DemandPrediction  # Import models after db is initialized
import pandas as pd
import joblib
from datetime import datetime
from sqlalchemy import text
from flask import jsonify

class InventoryManager:
    def __init__(self, model_path):
        self.model = self.load_model(model_path)

    def get_inventory(self):
        """Get the current inventory level."""
        try:
            # Execute the raw SQL query
            result = db.session.execute(text('select * from sales_4yrs'))
            
            # Convert the result to a list of dictionaries
            self.inventory_data = [dict(row) for row in result.fetchall()]
            
            # Return the serialized data
            return jsonify(self.inventory_data), 200
        except Exception as e:
            print(f"Error retrieving inventory data: {e}")
            return jsonify({"error": str(e)}), 500

    def load_model(self, model_path):
        """Load the trained demand prediction model from file."""
        try:
            model = joblib.load(model_path)
            print(f"Model loaded from {model_path}")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def predict_demand(self, input_data):
        """Predict demand for given input data."""
        if not self.model:
            raise ValueError("Model not loaded. Ensure the model file is available and correctly loaded.")
        
        # Format the data as needed for prediction
        df = pd.DataFrame(input_data)
        predictions = self.model.predict(df)
        return predictions

    def store_prediction(self, name, predicted_demand):
        """Store the demand prediction result in the database."""
        try:
            # Create a new DemandPrediction instance with prediction data
            prediction = DemandPrediction(
                name=name,
                demand=predicted_demand,
                date=datetime.now()
            )
            db.session.add(prediction)
            db.session.commit()
            print(f"Stored prediction for {name}: {predicted_demand}")
        except Exception as e:
            db.session.rollback()
            print(f"Error storing prediction: {e}")

    def update_inventory(self, name, sold_quantity):
        """Update the inventory level based on sold quantity."""
        try:
            # Find the relevant record in the database
            item = DemandPrediction.query.filter_by(name=name).first()
            if item:
                item.inventory_level -= sold_quantity
                db.session.commit()
                print(f"Updated inventory for {name}: New level is {item.inventory_level}")
            else:
                print(f"Item {name} not found in inventory.")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating inventory: {e}")

    def check_reorder(self, name):
        """Check if an item needs to be reordered based on current inventory level and reorder point."""
        item = DemandPrediction.query.filter_by(name=name).first()
        if item:
            if item.inventory_level <= item.reorder_point:
                print(f"{name} needs to be reordered.")
                return True
            else:
                print(f"{name} does not need reordering.")
                return False
        else:
            print(f"{name} not found in inventory.")
            return False

# Example utility functions that could be used externally
def initialize_db():
    """Initializes the database and creates tables if they don't exist."""
    db.create_all()

def load_model(model_path):
    """Load and return the prediction model."""
    try:
        model = joblib.load(model_path)
        print(f"Model loaded from {model_path}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def predict_demand(input_data, model):
    """Predict demand for the input data using the specified model."""
    df = pd.DataFrame(input_data)
    return model.predict(df)

def store_prediction(name, predicted_demand):
    """Store the demand prediction in the database."""
    try:
        prediction = DemandPrediction(name=name, demand=predicted_demand, date=datetime.now())
        db.session.add(prediction)
        db.session.commit()
        print(f"Stored prediction for {name}: {predicted_demand}")
    except Exception as e:
        db.session.rollback()
        print(f"Error storing prediction: {e}")
