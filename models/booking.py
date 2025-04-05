# models/booking.py
# Booking model to store car rental booking information

from datetime import datetime
from database import db
from app import db

class Booking(db.Model):
    """
    Model representing a car booking in the system.
    Stores information about who is renting which car and when.
    """
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=True)  # Allow null for backward compatibility
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, confirmed, completed, cancelled
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    car = db.relationship('Car', back_populates='bookings')
    renter = db.relationship('User', back_populates='bookings')
    messages = db.relationship('Message', back_populates='booking', cascade='all, delete-orphan')
    payment = db.relationship('Payment', back_populates='booking', uselist=False, cascade='all, delete-orphan')

    def __init__(self, car_id, renter_id, start_date, end_date, status='pending'):
        """
        Initialize a new booking.
        
        Args:
            car_id: The ID of the car being booked
            renter_id: The ID of the user making the booking
            start_date: The start date of the booking
            end_date: The end date of the booking
            status: The booking status (default: 'pending')
        """
        self.car_id = car_id
        self.renter_id = renter_id
        self.start_date = start_date
        self.end_date = end_date
        self.status = status

    def __repr__(self):
        """
        String representation of the booking.
        
        Returns:
            String representation
        """
        return f"<Booking {self.id} - Car {self.car_id} - Renter {self.renter_id} - {self.start_date} to {self.end_date} - {self.status}>"

    def to_dict(self):
        """
        Convert the booking to a dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'car_id': self.car_id,
            'renter_id': self.renter_id,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    @staticmethod
    def create_booking(car_id, renter_id, start_date, end_date):
        """
        Static method to create a new booking and save it to the database.
        
        Args:
            car_id: The ID of the car being booked
            renter_id: The ID of the user making the booking
            start_date: The start date of the booking
            end_date: The end date of the booking
            
        Returns:
            The newly created Booking object
        """
        from app import db
        
        # Check if the car is already booked for the requested period
        existing_bookings = Booking.query.filter(
            Booking.car_id == car_id,
            Booking.status.in_(['pending', 'confirmed']),
            db.or_(
                db.and_(Booking.start_date <= start_date, Booking.end_date >= start_date),
                db.and_(Booking.start_date <= end_date, Booking.end_date >= end_date),
                db.and_(Booking.start_date >= start_date, Booking.end_date <= end_date)
            )
        ).all()
        
        if existing_bookings:
            raise ValueError("The car is already booked for the requested period")
        
        # Create the booking
        booking = Booking(
            car_id=car_id,
            renter_id=renter_id,
            start_date=start_date,
            end_date=end_date,
            status='pending'
        )
        
        # Add to database
        db.session.add(booking)
        db.session.commit()
        
        return booking

    def update_status(self, new_status):
        """
        Update the booking status.
        
        Args:
            new_status: The new status
        """
        from app import db
        
        valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
        
        self.status = new_status
        db.session.commit()