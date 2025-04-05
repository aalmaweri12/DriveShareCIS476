# models/payment_method.py
from database import db
from datetime import datetime

class PaymentMethod(db.Model):
    """
    Model representing a saved payment method (credit card).
    Stores credit card information securely.
    """
    __tablename__ = 'payment_methods'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_type = db.Column(db.String(50), nullable=False)  # Visa, Mastercard, etc.
    last_four = db.Column(db.String(4), nullable=False)  # Last 4 digits only
    card_holder_name = db.Column(db.String(100), nullable=False)
    expiry_month = db.Column(db.Integer, nullable=False)
    expiry_year = db.Column(db.Integer, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='payment_methods')
    payments = db.relationship('Payment', back_populates='payment_method')  # Add this line

    def __init__(self, user_id, card_type, last_four, card_holder_name, expiry_month, expiry_year, is_default=False):
        self.user_id = user_id
        self.card_type = card_type
        self.last_four = last_four
        self.card_holder_name = card_holder_name
        self.expiry_month = expiry_month
        self.expiry_year = expiry_year
        self.is_default = is_default

    def is_expired(self):
        """Check if the card is expired."""
        now = datetime.utcnow()
        return (self.expiry_year < now.year or 
                (self.expiry_year == now.year and self.expiry_month < now.month))

    def to_dict(self):
        """Convert the payment method to a dictionary."""
        return {
            'id': self.id,
            'card_type': self.card_type,
            'last_four': self.last_four,
            'card_holder_name': self.card_holder_name,
            'expiry_month': self.expiry_month,
            'expiry_year': self.expiry_year,
            'is_default': self.is_default
        }