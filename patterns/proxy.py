# Proxy Pattern for Payment Processing

from abc import ABC, abstractmethod

class IPaymentProcessor(ABC):
    """
    Interface for payment processors.
    """
    @abstractmethod
    def process_payment(self, booking_id, amount):
        """
        Process a payment.
        
        Args:
            booking_id: The ID of the booking
            amount: The payment amount
            
        Returns:
            True if the payment was successful, False otherwise
        """
        pass

class RealPaymentProcessor(IPaymentProcessor):
    """
    Concrete payment processor that actually processes payments.
    """
    def process_payment(self, booking_id, amount):
        """
        Process a payment.
        
        Args:
            booking_id: The ID of the booking
            amount: The payment amount
            
        Returns:
            True if the payment was successful, False otherwise
        """
        # This import is placed here to avoid circular imports
        from models.booking import Booking
        from models.payment import Payment
        from app import db
        
        try:
            # Get the booking
            booking = db.session.query(Booking).get(booking_id)
            
            if not booking:
                return False
            
            # Update user balances (in a real app, this would interact with a payment gateway)
            self._update_balance(booking.renter_id, -amount)
            self._update_balance(booking.car.owner_id, amount)
            
            # Create payment record
            payment = Payment(
                booking_id=booking_id,
                amount=amount,
                status="completed"
            )
            
            # Save to database
            db.session.add(payment)
            db.session.commit()
            
            # Log the transaction
            self._log_transaction(booking_id, amount)
            
            return True
            
        except Exception as e:
            print(f"Payment error: {str(e)}")
            return False
    
    def _update_balance(self, user_id, amount):
        """
        Update a user's balance.
        
        Args:
            user_id: The ID of the user
            amount: The amount to add to the balance (negative for deductions)
        """
        # In a real application, this would update the user's balance in the database
        # For this simple implementation, we'll just print a message
        print(f"Updating balance for user {user_id} by {amount}")
    
    def _log_transaction(self, booking_id, amount):
        """
        Log a payment transaction.
        
        Args:
            booking_id: The ID of the booking
            amount: The payment amount
        """
        # In a real application, this would log the transaction in the database
        # For this simple implementation, we'll just print a message
        print(f"Logging transaction for booking {booking_id}: ${amount}")

class PaymentProxy(IPaymentProcessor):
    """
    Proxy for the payment processor that adds security checks and notifications.
    """
    def __init__(self):
        """
        Initialize the proxy with a real payment processor.
        """
        self._real_processor = RealPaymentProcessor()
    
    def process_payment(self, booking_id, amount):
        """
        Process a payment with additional security checks and notifications.
        
        Args:
            booking_id: The ID of the booking
            amount: The payment amount
            
        Returns:
            True if the payment was successful, False otherwise
        """
        # Perform security checks
        if not self._check_fraud(booking_id, amount):
            print("Payment declined: Failed fraud check")
            return False
        
        if not self._validate_booking(booking_id):
            print("Payment declined: Invalid booking")
            return False
        
        # Process the payment using the real processor
        result = self._real_processor.process_payment(booking_id, amount)
        
        # Send notifications
        if result:
            self._notify_users(booking_id)
        
        return result
    
    def _check_fraud(self, booking_id, amount):
        """
        Check for fraudulent activity.
        
        Args:
            booking_id: The ID of the booking
            amount: The payment amount
            
        Returns:
            True if the payment seems legitimate, False otherwise
        """
        # In a real application, this would implement fraud detection
        # For this simple implementation, we'll approve all transactions
        return True
    
    def _validate_booking(self, booking_id):
        """
        Validate that the booking exists and is in a valid state.
        
        Args:
            booking_id: The ID of the booking
            
        Returns:
            True if the booking is valid, False otherwise
        """
        # This import is placed here to avoid circular imports
        from models.booking import Booking
        from app import db
        
        booking = db.session.query(Booking).get(booking_id)
        
        if not booking:
            return False
        
        if booking.status not in ["pending", "confirmed"]:
            return False
        
        return True
    
    def _notify_users(self, booking_id):
        """
        Notify users about payment processing.
        
        Args:
            booking_id: The ID of the booking
        """
        # This import is placed here to avoid circular imports
        from datetime import datetime
        from models import Booking, User, Car
        from patterns.observer import NotificationSubject, EmailNotifier, AppNotifier
        
        # Get the booking
        booking = Booking.query.get(booking_id)
        if not booking:
            return
        
        # Get the users
        renter = User.query.get(booking.renter_id)
        car = Car.query.get(booking.car_id)
        owner = User.query.get(car.owner_id)
        
        # Create notification subject and observers
        notification_subject = NotificationSubject()
        email_notifier = EmailNotifier()
        app_notifier = AppNotifier()
        
        # Register observers
        notification_subject.attach(email_notifier)
        notification_subject.attach(app_notifier)
        
        # Calculate total price
        days = (booking.end_date - booking.start_date).days + 1
        amount = days * car.daily_price
        
        # Prepare notification data for renter
        renter_notification_data = {
            'notification_type': 'payment_confirmation',
            'user_id': booking.renter_id,
            'user_email': renter.email,
            'booking_id': booking.id,
            'amount': amount,
            'payment_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'car_name':  car.model,  # Adjust this based on your Car model
            'start_date': booking.start_date.strftime('%Y-%m-%d'),
            'end_date': booking.end_date.strftime('%Y-%m-%d'),
            'message': "Payment completed for your booking"
        }
        
        # Send notification to renter
        notification_subject.notify(renter_notification_data)
        
        # Prepare notification data for owner
        owner_notification_data = {
            'notification_type': 'payment_confirmation',
            'user_id': car.owner_id,
            'user_email': owner.email,
            'booking_id': booking.id,
            'amount': amount,
            'payment_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'car_name':  car.model,  # Adjust this based on your Car model
            'start_date': booking.start_date.strftime('%Y-%m-%d'),
            'end_date': booking.end_date.strftime('%Y-%m-%d'),
            'message': f"Payment of ${amount} received for your car booking"
        }
        
        # Send notification to owner
        notification_subject.notify(owner_notification_data)