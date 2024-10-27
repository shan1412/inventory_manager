# model_builder.py

from app import db  # Import the db object from app.py
from sqlalchemy import Column, Integer, String, Float, DateTime
import pandas as pd
import xgboost as xgb  # Ensure XGBoost is imported
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

# Define the DemandPrediction model using db.Model from Flask-SQLAlchemy
class DemandPrediction(db.Model):
    __tablename__ = 'demand_prediction'

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


# Define the DemandPredictor class to handle data loading, preprocessing, model training, and prediction
class DemandPredictor:
    def __init__(self, db_connection_string, query, csv_file_path):
        self.db_connection_string = db_connection_string
        self.query = query
        self.csv_file_path = csv_file_path
        self.model = None

    def load_data(self):
        """Load sales data from a database or CSV into a DataFrame."""
        try:
            # Check if the database table is empty
            count = db.session.query(DemandPrediction).count()
            if count == 0:
                # Load data from CSV if the database table is empty
                print("Database is empty. Loading data from CSV...")
                sales_data = pd.read_csv(self.csv_file_path)
                sales_data.to_sql(DemandPrediction.__tablename__, db.engine, if_exists='replace', index=False)
                print("Data loaded into the database from CSV.")
            else:
                # Load data from the database if not empty
                print("Loading data from the database...")
                sales_data = pd.read_sql(self.query, db.engine)

            # Clean column names
            sales_data.columns = sales_data.columns.str.strip().str.lower()
            return sales_data
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def preprocess_data(self, sales_data):
        """Preprocess the sales data for modeling."""
        if 'date' not in sales_data.columns:
            raise ValueError("The 'date' column is missing from the sales data.")

        demand_column = 'demand'
        if demand_column not in sales_data.columns:
            raise ValueError(f"The '{demand_column}' column is missing from the sales data.")

        # Convert date column to datetime
        sales_data['date'] = pd.to_datetime(sales_data['date'])
        sales_data['week'] = sales_data['date'].dt.isocalendar().week
        sales_data['year'] = sales_data['date'].dt.year
        sales_data.sort_values(by=['name', 'date'], inplace=True)

        # Creating lag and rolling mean features
        sales_data['lag_1'] = sales_data.groupby('name')[demand_column].shift(1)
        sales_data['rolling_mean'] = sales_data.groupby('name')[demand_column].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean().shift(1)
        )

        # Drop rows with NaN values
        sales_data.dropna(inplace=True)
        return sales_data

    def train_model(self, sales_data):
        """Train the XGBoost model on the sales data."""
        # Define features and target
        X = sales_data[['week', 'year', 'lag_1', 'rolling_mean']]
        y = sales_data['demand']

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Initialize the XGBoost regressor
        self.model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1)

        # Fit the model
        self.model.fit(X_train, y_train)

        # Make predictions and evaluate the model
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Mean Squared Error: {mse}")

    def save_model(self, filename):
        """Save the trained model to a file."""
        joblib.dump(self.model, filename)
        print(f"Model saved to {filename}")

    def load_model(self, filename):
        """Load the model from a file."""
        self.model = joblib.load(filename)
        print(f"Model loaded from {filename}")

    def predict(self, X_new):
        """Predict demand for new data."""
        if self.model is None:
            raise ValueError("Model has not been trained or loaded.")
        return self.model.predict(X_new)
