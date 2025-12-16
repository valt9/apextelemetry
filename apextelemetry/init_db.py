"""
Database initialization script
Run this to create the database tables
"""
from app import app, db

with app.app_context():
    db.create_all()
    print("Database initialized successfully!")
    print("You can now run the application with: python app.py")

