# models/car.py
# Car model to store vehicle listing information

from datetime import datetime
from database import db
from app import db

class Car(db.Model):
    """
    Model representing a car listing in the system.
    Stores information about cars available for rental.
    """
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Float, nullable=False)
    daily_price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    availability_start = db.Column(db.Date, nullable=False)
    availability_end = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = db.relationship('User', back_populates='cars')
    bookings = db.relationship('Booking', back_populates='car', cascade='all, delete-orphan')

    def __init__(self, owner_id, model=None, year=None, mileage=None, daily_price=None, 
                 location=None, availability_start=None, availability_end=None):
        """
        Initialize a new car listing.
        
        Args:
            owner_id: The ID of the car owner
            model: The car model
            year: The car year
            mileage: The car mileage
            daily_price: The daily rental price
            location: The car pickup location
            availability_start: The start date of availability
            availability_end: The end date of availability
        """
        self.owner_id = owner_id
        self.model = model
        self.year = year
        self.mileage = mileage
        self.daily_price = daily_price
        self.location = location
        self.availability_start = availability_start
        self.availability_end = availability_end

    def __repr__(self):
        """
        String representation of the car listing.
        
        Returns:
            String representation
        """
        return f"<Car {self.id} - {self.model} ({self.year}) - Owner {self.owner_id}>"

    def to_dict(self):
        """
        Convert the car listing to a dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'model': self.model,
            'year': self.year,
            'mileage': self.mileage,
            'daily_price': self.daily_price,
            'location': self.location,
            'availability_start': self.availability_start.strftime('%Y-%m-%d') if self.availability_start else None,
            'availability_end': self.availability_end.strftime('%Y-%m-%d') if self.availability_end else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    @staticmethod
    def search_available_cars(location=None, start_date=None, end_date=None):
        """
        Search for available cars based on location and date range.
        
        Args:
            location: The pickup location (optional)
            start_date: The start date of rental (optional)
            end_date: The end date of rental (optional)
            
        Returns:
            List of available cars matching the criteria
        """
        from app import db
        from models.booking import Booking
        
        # Start with all cars
        query = Car.query
        
        # Filter by location if provided
        if location:
            query = query.filter(Car.location.like(f"%{location}%"))
        
        # Filter by availability dates if provided
        if start_date and end_date:
            query = query.filter(
                Car.availability_start <= start_date,
                Car.availability_end >= end_date
            )
            
            # Exclude cars that are already booked for the requested period
            booked_car_ids = db.session.query(Booking.car_id).filter(
                Booking.status.in_(['pending', 'confirmed']),
                db.or_(
                    db.and_(Booking.start_date <= start_date, Booking.end_date >= start_date),
                    db.and_(Booking.start_date <= end_date, Booking.end_date >= end_date),
                    db.and_(Booking.start_date >= start_date, Booking.end_date <= end_date)
                )
            ).all()
            
            booked_car_ids = [car_id for (car_id,) in booked_car_ids]
            
            if booked_car_ids:
                query = query.filter(~Car.id.in_(booked_car_ids))
        
        return query.all()

    def is_available(self, start_date, end_date):
        """
        Check if the car is available for a specific date range.
        
        Args:
            start_date: The start date to check
            end_date: The end date to check
            
        Returns:
            True if the car is available, False otherwise
        """
        from app import db
        from models.booking import Booking
        
        # Check if the requested dates are within the car's availability period
        if start_date < self.availability_start or end_date > self.availability_end:
            return False
        
        # Check if there are any overlapping bookings
        existing_bookings = Booking.query.filter(
            Booking.car_id == self.id,
            Booking.status.in_(['pending', 'confirmed']),
            db.or_(
                db.and_(Booking.start_date <= start_date, Booking.end_date >= start_date),
                db.and_(Booking.start_date <= end_date, Booking.end_date >= end_date),
                db.and_(Booking.start_date >= start_date, Booking.end_date <= end_date)
            )
        ).all()
        
        return len(existing_bookings) == 0

    def update_details(self, model=None, year=None, mileage=None, daily_price=None,
                      location=None, availability_start=None, availability_end=None):
        """
        Update the car listing details.
        
        Args:
            model: The car model (optional)
            year: The car year (optional)
            mileage: The car mileage (optional)
            daily_price: The daily rental price (optional)
            location: The car pickup location (optional)
            availability_start: The start date of availability (optional)
            availability_end: The end date of availability (optional)
        """
        from app import db
        
        if model is not None:
            self.model = model
            
        if year is not None:
            self.year = year
            
        if mileage is not None:
            self.mileage = mileage
            
        if daily_price is not None:
            self.daily_price = daily_price
            
        if location is not None:
            self.location = location
            
        if availability_start is not None:
            self.availability_start = availability_start
            
        if availability_end is not None:
            self.availability_end = availability_end
            
        db.session.commit()