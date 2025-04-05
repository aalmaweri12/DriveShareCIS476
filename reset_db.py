from app import create_app
from database import db
from models import User, Car, Booking, Message, Payment, PaymentMethod
import os

# Delete existing database file if it exists
if os.path.exists('driveshare.db'):
    os.remove('driveshare.db')
    print("Deleted existing database.")

# Create app and initialize database
app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("Created database tables.")
    
    # You can add sample data here if needed
    # For example:
    # admin = User(...)
    # db.session.add(admin)
    # db.session.commit()
    
    print("Database reset complete!")