from app import create_app, db
from models import User, Car, Booking, Message, Payment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def init_db():
    """Initialize the database with sample data."""
    app = create_app()
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create tables
        db.create_all()
        
        print("Creating sample users...")
        # Create sample users
        admin = User(
            email='admin@example.com',
            password='password',
            name='Admin User',
            security_question_1='What was your first pet\'s name?',
            security_answer_1='fluffy',
            security_question_2='What is your mother\'s maiden name?',
            security_answer_2='smith',
            security_question_3='What was the name of your first school?',
            security_answer_3='lincoln'
        )
        
        user1 = User(
            email='john@example.com',
            password='password',
            name='John Smith',
            security_question_1='What was your first pet\'s name?',
            security_answer_1='rover',
            security_question_2='What is your mother\'s maiden name?',
            security_answer_2='jones',
            security_question_3='What was the name of your first school?',
            security_answer_3='jefferson'
        )
        
        user2 = User(
            email='jane@example.com',
            password='password',
            name='Jane Doe',
            security_question_1='What was your first pet\'s name?',
            security_answer_1='whiskers',
            security_question_2='What is your mother\'s maiden name?',
            security_answer_2='brown',
            security_question_3='What was the name of your first school?',
            security_answer_3='washington'
        )
        
        db.session.add_all([admin, user1, user2])
        db.session.commit()
        
        print("Creating sample cars...")
        # Create sample cars
        today = datetime.now().date()
        
        car1 = Car(
            owner_id=user1.id,
            model='Toyota Camry',
            year=2018,
            mileage=35000,
            daily_price=45.00,
            location='123 Main St, Anytown, USA',
            availability_start=today,
            availability_end=today + timedelta(days=90)
        )
        
        car2 = Car(
            owner_id=user1.id,
            model='Honda Civic',
            year=2020,
            mileage=15000,
            daily_price=50.00,
            location='123 Main St, Anytown, USA',
            availability_start=today,
            availability_end=today + timedelta(days=90)
        )
        
        car3 = Car(
            owner_id=user2.id,
            model='Tesla Model 3',
            year=2021,
            mileage=8000,
            daily_price=95.00,
            location='456 Oak Ave, Othertown, USA',
            availability_start=today,
            availability_end=today + timedelta(days=90)
        )
        
        db.session.add_all([car1, car2, car3])
        db.session.commit()
        
        print("Creating sample bookings...")
        # Create sample bookings
        booking1 = Booking(
            car_id=car3.id,
            renter_id=user1.id,
            start_date=today + timedelta(days=5),
            end_date=today + timedelta(days=8),
            status='confirmed'
        )
        
        booking2 = Booking(
            car_id=car1.id,
            renter_id=user2.id,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=15),
            status='pending'
        )
        
        db.session.add_all([booking1, booking2])
        db.session.commit()
        
        print("Creating sample messages...")
        # Create sample messages
        message1 = Message(
            sender_id=user1.id,
            receiver_id=user2.id,
            booking_id=booking1.id,
            content='Hi, I\'m looking forward to renting your Tesla. Is there anything I should know before pickup?',
            is_read=True
        )
        
        message2 = Message(
            sender_id=user2.id,
            receiver_id=user1.id,
            booking_id=booking1.id,
            content='Hi John! The car will be fully charged. Make sure to bring your license and a credit card for the security deposit.',
            is_read=False
        )
        
        message3 = Message(
            sender_id=user2.id,
            receiver_id=user1.id,
            booking_id=booking2.id,
            content='I\'m interested in renting your Camry. Is it possible to pick it up earlier on that day?',
            is_read=True
        )
        
        db.session.add_all([message1, message2, message3])
        db.session.commit()
        
        print("Creating sample payment...")
        # Create sample payment
        payment = Payment(
            booking_id=booking1.id,
            amount=95.00 * 4,  # 4 days at $95 per day
            status='completed'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()