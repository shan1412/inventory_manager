from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import os
from werkzeug.utils import secure_filename
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from database import db  # Import db from database.py
from models import DemandPrediction  # Import models after db initialization
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Float, String, Table
from sqlalchemy.exc import IntegrityError
import pandas as pd
from werkzeug.utils import secure_filename
import os
import logging
import sqlite3



# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Set the upload folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16 MB
db.init_app(app)
CORS(app)
migrate = Migrate(app, db)  # Bind Flask app and SQLAlchemy
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database within app context
with app.app_context():
    db.create_all()

# Only import InventoryManager here to avoid circular dependency
from inventory import InventoryManager

# Initialize inventory manager
model_path = 'xgboost_demand_forecast.pkl'
inventory_manager = InventoryManager(model_path)


# Database connection function
def get_db_connection():
    conn = sqlite3.connect(r'F:\Assignements\Binny_inventorymanagement\inventory_management\instance\inventory.db')  # Update with your DB path
    conn.row_factory = sqlite3.Row  # This allows you to access columns by name
    return conn

# Define dynamic model class
def create_dynamic_model(table_name, columns):
    """Dynamically create a SQLAlchemy model class with a primary key."""
    attributes = {'__tablename__': table_name}

    # Define a primary key column
    attributes['id'] = Column(Integer, primary_key=True, autoincrement=True)

    for column in columns:
        # Skip adding the column if it already exists in the CSV
        if column['name'].lower() == 'id':
            continue  # Skip the existing ID column

        # Add the column to the model dynamically
        if 'int' in column['type']:
            attributes[column['name']] = Column(Integer)
        elif 'float' in column['type']:
            attributes[column['name']] = Column(Float)
        else:
            attributes[column['name']] = Column(String)

    # Create a new dynamic model class
    DynamicModel = type(table_name.capitalize(), (db.Model,), attributes)

    return DynamicModel

@app.route('/load_data', methods=['POST'])
def load_data():
    """Load data from an uploaded CSV file into the database."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            data = pd.read_csv(file_path)
            table_name = filename.split('.')[0]  # Use filename as table name

            # Prepare columns for the dynamic model
            columns = [{'name': col, 'type': 'float' if data[col].dtype == 'float64' else 'int' if data[col].dtype == 'int64' else 'str'} for col in data.columns]

            # Create dynamic model
            DynamicModel = create_dynamic_model(table_name, columns)

            # Create the table in the database
            db.create_all()  # Ensure all tables are created

            # Insert data into the dynamic table
            for index, row in data.iterrows():
                # Create an entry while skipping the existing ID column
                entry_data = row.to_dict()
                entry_data.pop('ID', None)  # Remove the ID key if it exists to prevent conflicts
                entry = DynamicModel(**entry_data)
                db.session.add(entry)
            db.session.commit()
            logger.info("Data loaded successfully from CSV.")
            return jsonify({"message": "Data loaded successfully.", "table": table_name}), 200
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error loading data from CSV: Integrity Error: {e}")
            return jsonify({"error": "Data integrity error, please check your CSV."}), 500
        except Exception as e:
            logger.error(f"Error loading data from CSV: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file type. Only CSV files are allowed."}), 400


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/inventory', methods=['GET'])
def get_inventory():
    try:
        cursor = get_db_connection().cursor()
        cursor.execute("SELECT * FROM sales_4yrs limit 10;")  # Adjust your query
        rows = cursor.fetchall()
        inventory = [dict(row) for row in rows]
        print(inventory)
        return jsonify(inventory), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/inventory', methods=['POST'])
def add_item():
    data = request.json
    if not data or 'name' not in data or 'quantity' not in data:
        return jsonify({"error": "Invalid data"}), 400

    result = inventory_manager.add_item(data)  # Ensure this method exists in InventoryManager
    return jsonify(result), 201

@app.route('/inventory/<string:item_id>', methods=['GET'])
def get_item(item_id):
    item = inventory_manager.get_item(item_id)  # Ensure this method exists in InventoryManager
    if item:
        return jsonify(item), 200
    else:
        return jsonify({"error": "Item not found"}), 404
    
@app.route('/inventory/<string:item_id>', methods=['PUT'])
def update_inventory(item_id):
    data = request.json
    if not data or 'quantity' not in data:
        return jsonify({"error": "Invalid data"}), 400

    result = inventory_manager.update_inventory(item_id, data)  # Ensure this method exists in InventoryManager
    if result:
        return jsonify(result), 200
    else:
        return jsonify({"error": "Item not found"}), 404

@app.route('/inventory/check', methods=['POST'])
def check_stock():
    item_id = request.json.get('item_id')
    if not item_id:
        return jsonify({"error": "Item ID is required"}), 400

    result = inventory_manager.is_in_stock(item_id)  # Ensure this method exists in InventoryManager
    return jsonify(result), 200

@app.route('/order', methods=['POST'])
def place_order():
    order_data = request.json
    if not order_data or 'item_id' not in order_data or 'quantity' not in order_data:
        return jsonify({"error": "Invalid order data"}), 400

    result = inventory_manager.process_order(order_data["item_id"], order_data["quantity"])  # Ensure this method exists
    return jsonify(result), 200

@app.route('/predict_demand', methods=['POST'])
def predict():
    data = request.get_json()
    if 'Demand' not in data or 'product_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        prediction = inventory_manager.predict_demand(data)  # Pass data directly
        inventory_manager.store_prediction(data.get("product_id"), prediction)  # Use the store_prediction method
        return jsonify({'predicted_demand': prediction}), 200
    except Exception as e:
        logger.error(f"Error predicting demand: {e}")
        return jsonify({'error': str(e)}), 500

# Scheduler for automated predictions
scheduler = BackgroundScheduler()
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
