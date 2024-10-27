import xgboost as xgb
import pandas as pd
import joblib
from sqlalchemy import create_engine
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

def train_and_save_model():
    # Create a connection to the SQLite database
    db_path = r'F:\Assignements\Binny_inventorymanagement\inventory_management\sales_data.db'
    engine = create_engine(f'sqlite:///{db_path}')

    # Load your training data from the database
    query = "SELECT * FROM sales;"  # Adjust this to select the necessary fields
    df = pd.read_sql(query, engine)

    # Ensure that 'demand' is a column in your DataFrame
    if 'demand' not in df.columns:
        raise ValueError("The 'Demand' column is missing from the sales data.")

    # Split your data into features (X) and target (y)
    X = df.drop('demand', axis=1)  # Features
    y = df['demand']  # Target

    # Define categorical columns (adjust these based on your actual DataFrame)
    categorical_cols = X.select_dtypes(include=['object']).columns.tolist()

    # Create a preprocessor for categorical features
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(drop='first'), categorical_cols)  # One-hot encoding
        ],
        remainder='passthrough'  # Keep other features unchanged
    )

    # Create a pipeline with preprocessing and model training
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', xgb.XGBRegressor(objective='reg:squarederror'))  # Specify the objective
    ])

    # Fit the model
    model_pipeline.fit(X, y)

    # Save the trained model
    joblib.dump(model_pipeline, 'xgboost_demand_forecast.pkl')
    print("Model trained and saved as 'xgboost_demand_forecast.pkl'.")

if __name__ == "__main__":
    train_and_save_model()
