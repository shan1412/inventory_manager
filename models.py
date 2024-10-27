from database import db  # Import db from database.py to avoid circular import
from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime  # Import the necessary SQLAlchemy types

# Define the InventoryManager class if it contains only model-specific logic
class InventoryManager:
    def __init__(self, inventory_level, reorder_point, lead_time_days, supplier):
        self.inventory_level = inventory_level
        self.reorder_point = reorder_point
        self.lead_time_days = lead_time_days
        self.supplier = supplier
    
    def check_reorder(self):
        """
        Check if inventory is below the reorder point.
        """
        return self.inventory_level <= self.reorder_point
    
    def __repr__(self):
        return f"<InventoryManager Level: {self.inventory_level}, Reorder Point: {self.reorder_point}>"

# Define the DemandPrediction model using SQLAlchemy
class DemandPrediction(db.Model):
    __tablename__ = 'demand_prediction'  # Name of the table in the database

    id = db.Column(Integer, primary_key=True)
    primary_category_alt = db.Column(String(50), nullable=False)
    name = db.Column(String(100), nullable=False)
    price_range_description = db.Column(String(50), nullable=True)
    price = db.Column(Float, nullable=False)
    discount = db.Column(Float, nullable=True)
    description = db.Column(String(255), nullable=True)
    upload_date_time = db.Column(DateTime, nullable=False)
    status = db.Column(String(50), nullable=True)
    inventory_level = db.Column(Integer, nullable=False)
    reorder_point = db.Column(Integer, nullable=False)
    lead_time_days = db.Column(Integer, nullable=True)
    supplier = db.Column(String(100), nullable=True)
    last_restock_date = db.Column(DateTime, nullable=True)
    discount_percentage = db.Column(Float, nullable=True)
    total_revenue = db.Column(Float, nullable=True)
    demand = db.Column(Float, nullable=False)
    date = db.Column(DateTime, nullable=False)
    week = db.Column(Integer, nullable=False)
    lag_1 = db.Column(Float, nullable=True)
    rolling_mean = db.Column(Float, nullable=True)

    def __repr__(self):
        return f"<DemandPrediction {self.name} - Demand: {self.demand}>"

# Adding the extend_existing option (not necessary here since we're already defining the table)
