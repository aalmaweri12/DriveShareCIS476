# models/payment.py
# Payment model to store payment transaction information

from datetime import datetime
from database import db  # Remove the duplicate import

class Payment(db.Model):
    """
    Model representing a payment transaction in the system.
    Stores information about payments for car rentals.
    """
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, completed, failed, refunded
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'), nullable=True)  # New field for saved payment method

    # Relationship
    booking = db.relationship('Booking', back_populates='payment')
    payment_method = db.relationship('PaymentMethod', back_populates='payments')  # New relationship

    def __init__(self, booking_id, amount, status='pending', payment_method_id=None):
        """
        Initialize a new payment transaction.
        
        Args:
            booking_id: The ID of the booking being paid for
            amount: The payment amount
            status: The payment status (default: 'pending')
            payment_method_id: The ID of the payment method used (optional)
        """
        self.booking_id = booking_id
        self.amount = amount
        self.status = status
        self.payment_method_id = payment_method_id

    def __repr__(self):
        """
        String representation of the payment.
        
        Returns:
            String representation
        """
        return f"<Payment {self.id} - Booking {self.booking_id} - ${self.amount} - {self.status}>"

    def to_dict(self):
        """
        Convert the payment to a dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'amount': self.amount,
            'status': self.status,
            'payment_method_id': self.payment_method_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def complete_payment(self):
        """
        Mark the payment as completed.
        """
        # Import here to avoid circular imports
        from patterns.observer import NotificationSubject, EmailNotifier, AppNotifier
        
        # Update payment status
        self.status = 'completed'
        db.session.commit()
        
        # Get booking and user IDs for notification
        booking = self.booking
        
        # Create notification subject
        notification = NotificationSubject()
        
        # Attach observers
        notification.attach(EmailNotifier())
        notification.attach(AppNotifier())
        
        # Notify users
        notification.notify(f"Payment of ${self.amount} has been completed for your booking", booking.renter_id)
        notification.notify(f"Payment of ${self.amount} has been received for your car rental", booking.car.owner_id)
        
        # Update booking status
        booking.status = 'confirmed'
        db.session.commit()

    def refund_payment(self):
        """
        Refund the payment.
        """
        # Import here to avoid circular imports
        from patterns.observer import NotificationSubject, EmailNotifier, AppNotifier
        
        # Update payment status
        self.status = 'refunded'
        db.session.commit()
        
        # Get booking and user IDs for notification
        booking = self.booking
        
        # Create notification subject
        notification = NotificationSubject()
        
        # Attach observers
        notification.attach(EmailNotifier())
        notification.attach(AppNotifier())
        
        # Notify users
        notification.notify(f"Refund of ${self.amount} has been processed for your booking", booking.renter_id)
        notification.notify(f"Refund of ${self.amount} has been processed for your car rental", booking.car.owner_id)
        
        # Update booking status
        booking.status = 'cancelled'
        db.session.commit()

    @staticmethod
    def process_payment(booking_id, amount, payment_method_id=None):
        """
        Static method to process a payment for a booking.
        
        Args:
            booking_id: The ID of the booking
            amount: The payment amount
            payment_method_id: The ID of the payment method used (optional)
            
        Returns:
            The Payment object if successful, None otherwise
        """
        # Import here to avoid circular imports
        from patterns.proxy import PaymentProxy
        from models.booking import Booking
        
        # Check if payment already exists
        existing_payment = Payment.query.filter_by(booking_id=booking_id).first()
        if existing_payment and existing_payment.status in ['completed', 'pending']:
            return existing_payment
            
        # Create or update payment
        if existing_payment:
            existing_payment.amount = amount
            existing_payment.status = 'pending'
            existing_payment.payment_method_id = payment_method_id
            payment = existing_payment
        else:
            payment = Payment(booking_id=booking_id, amount=amount, status='pending', payment_method_id=payment_method_id)
            db.session.add(payment)
            
        db.session.commit()
        
        # Use the PaymentProxy to process the payment
        payment_proxy = PaymentProxy()
        success = payment_proxy.process_payment(booking_id, amount)
        
        if success:
            payment.complete_payment()
            return payment
        else:
            payment.status = 'failed'
            db.session.commit()
            return None