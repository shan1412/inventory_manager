# database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Initialize db here to avoid circular import issues
