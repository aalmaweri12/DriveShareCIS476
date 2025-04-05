# Observer Pattern for Notification System - Enhanced with Email Support

from abc import ABC, abstractmethod
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models.user import User
from app import db
import os

# Email configuration - Add these to your config.py file
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USER = os.environ.get('EMAIL_USER', 'driveshare70@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'gsrywpxmahfpennc')

class NotificationObserver(ABC):
    """
    Abstract base class for notification observers.
    """
    @abstractmethod
    def update(self, notification_data):
        """
        Update method to be implemented by concrete observers.
        
        Args:
            notification_data: Dictionary containing notification details
        """
        pass
    
class EmailNotifier(NotificationObserver):
    """
    Concrete observer that sends email notifications.
    """
    def update(self, notification_data):
        """
        Send an email notification based on notification type.
        
        Args:
            notification_data: Dictionary containing notification details
        """
        notification_type = notification_data.get('notification_type')
        user_id = notification_data.get('user_id')
        user_email = notification_data.get('user_email')
        
        if not user_email and user_id:
            # Get user email from database if not provided
            user = User.query.get(user_id)
            if user:
                user_email = user.email
        
        if not user_email:
            print("No email address available for notification")
            return
            
        if notification_type == 'booking_created':
            self._send_booking_notification(user_email, notification_data)
        elif notification_type == 'booking_confirmed':
            self._send_booking_status_notification(user_email, notification_data, 'confirmed')
        elif notification_type == 'booking_rejected':
            self._send_booking_status_notification(user_email, notification_data, 'rejected')
        elif notification_type == 'payment_confirmation':
            self._send_payment_notification(user_email, notification_data)
        elif notification_type == 'booking_request':
            self._send_booking_request_notification(user_email, notification_data)
        elif notification_type == 'booking_cancelled':
            self._send_booking_status_notification(user_email, notification_data, 'cancelled')
        else:
            # Generic notification
            message = notification_data.get('message', 'You have a new notification')
            self.send_email(user_email, "DriveShare Notification", message)
    
    def _send_booking_request_notification(self, user_email, notification_data):
        """
        Send a notification to car owner about new booking request.
        
        Args:
            user_email: The email address to send to (car owner)
            notification_data: Dictionary containing booking details
        """
        subject = "DriveShare: New Booking Request"
        
        body = f"""
        Hello,
        
        You have received a new booking request for your car.
        
        Booking Details:
        Car: {notification_data.get('car_name', 'Not specified')}
        Renter: {notification_data.get('renter_name', 'Not specified')}
        Start Date: {notification_data.get('start_date', 'Not specified')}
        End Date: {notification_data.get('end_date', 'Not specified')}
        Total Price: ${notification_data.get('total_price', 'Not specified')}
        
        Please log in to your DriveShare account to confirm or reject this booking.
        
        Thank you for using DriveShare!
        """
        
        self.send_email(user_email, subject, body)
        
    def _send_booking_notification(self, user_email, notification_data):
        """
        Send a booking notification email.
        
        Args:
            user_email: The email address to send to
            notification_data: Dictionary containing booking details
        """
        subject = "DriveShare: New Booking Request"
        
        body = f"""
        Hello,
        
        Your booking request has been received successfully.
        
        Booking Details:
        Car: {notification_data.get('car_name', 'Not specified')}
        Start Date: {notification_data.get('start_date', 'Not specified')}
        End Date: {notification_data.get('end_date', 'Not specified')}
        Total Price: ${notification_data.get('total_price', 'Not specified')}
        
        The car owner will review your request soon.
        
        Thank you for using DriveShare!
        """
        
        self.send_email(user_email, subject, body)
    
    def _send_booking_status_notification(self, user_email, notification_data, status):
        """
        Send a booking status update notification email.
        
        Args:
            user_email: The email address to send to
            notification_data: Dictionary containing booking details
            status: The new booking status
        """
        subject = f"DriveShare: Booking {status.capitalize()}"
        
        if status == 'confirmed':
            body = f"""
            Hello,
            
            Great news! Your booking request has been confirmed by the car owner.
            
            Booking Details:
            Car: {notification_data.get('car_name', 'Not specified')}
            Start Date: {notification_data.get('start_date', 'Not specified')}
            End Date: {notification_data.get('end_date', 'Not specified')}
            
            You can now proceed to make the payment.
            
            Thank you for using DriveShare!
            """
        elif status == 'cancelled':
            body = f"""
            Hello,
            
            This is a confirmation that your booking has been cancelled.
            
            Booking Details:
            Car: {notification_data.get('car_name', 'Not specified')}
            Start Date: {notification_data.get('start_date', 'Not specified')}
            End Date: {notification_data.get('end_date', 'Not specified')}
            
            If you have any questions, please contact our support team.
            
            Thank you for using DriveShare!
            """
        else:
            body = f"""
            Hello,
            
            We regret to inform you that your booking request has been rejected by the car owner.
            
            Booking Details:
            Car: {notification_data.get('car_name', 'Not specified')}
            Start Date: {notification_data.get('start_date', 'Not specified')}
            End Date: {notification_data.get('end_date', 'Not specified')}
            
            Reason: {notification_data.get('reason', 'No reason provided')}
            
            Please try booking another car or different dates.
            
            Thank you for using DriveShare!
            """
        
        self.send_email(user_email, subject, body)
    
    def _send_payment_notification(self, user_email, notification_data):
        """
        Send a payment confirmation email.
        
        Args:
            user_email: The email address to send to
            notification_data: Dictionary containing payment details
        """
        subject = "DriveShare: Payment Confirmation"
        
        body = f"""
        Hello,
        
        Your payment has been processed successfully.
        
        Payment Details:
        Booking ID: {notification_data.get('booking_id', 'Not specified')}
        Amount Paid: ${notification_data.get('amount', 'Not specified')}
        Date: {notification_data.get('payment_date', 'Not specified')}
        
        Car Details:
        Car: {notification_data.get('car_name', 'Not specified')}
        Start Date: {notification_data.get('start_date', 'Not specified')}
        End Date: {notification_data.get('end_date', 'Not specified')}
        
        Thank you for choosing DriveShare!
        """
        
        self.send_email(user_email, subject, body)
        
    def send_email(self, recipient_email, subject, message):
        """
        Send an email using SMTP.
        
        Args:
            recipient_email: The email address to send to
            subject: The email subject
            message: The email body
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            print(f"Email sent successfully to {recipient_email}")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

class AppNotifier(NotificationObserver):
    """
    Concrete observer that sends in-app notifications.
    """
    def update(self, notification_data):
        """
        Send an in-app notification.
        
        Args:
            notification_data: Dictionary containing notification details
        """
        user_id = notification_data.get('user_id')
        notification_type = notification_data.get('notification_type')
        
        if not user_id:
            print("No user ID provided for in-app notification")
            return
            
        # Create appropriate message based on notification type
        if notification_type == 'booking_created':
            message = f"Your booking for {notification_data.get('car_name', 'a car')} has been created."
        elif notification_type == 'booking_confirmed':
            message = f"Your booking for {notification_data.get('car_name', 'a car')} has been confirmed."
        elif notification_type == 'booking_rejected':
            message = f"Your booking for {notification_data.get('car_name', 'a car')} has been rejected."
        elif notification_type == 'booking_cancelled':
            message = f"Your booking for {notification_data.get('car_name', 'a car')} has been cancelled."
        elif notification_type == 'payment_confirmation':
            message = f"Your payment of ${notification_data.get('amount', '0')} has been processed."
        else:
            message = notification_data.get('message', 'You have a new notification')
            
        self.send_notification(user_id, message)
        
    def send_notification(self, user_id, message):
        """
        Send an in-app notification to a specific user.
        
        Args:
            user_id: The ID of the user to notify
            message: The notification message
        """
        # In a real application, this would create a notification in the database
        # For this simple implementation, we'll just print the message
        print(f"Sending in-app notification to user {user_id}: {message}")
        
        # Uncomment this code if you have a Notification model and want to store in DB
        '''
        from models.notification import Notification
        from app import db
        
        notification = Notification(
            user_id=user_id,
            message=message,
            is_read=False
        )
        
        db.session.add(notification)
        db.session.commit()
        '''

class NotificationSubject:
    """
    Subject class that maintains a list of observers and notifies them of changes.
    """
    def __init__(self):
        """
        Initialize the subject with an empty list of observers.
        """
        self._observers = []
    
    def attach(self, observer):
        """
        Attach an observer to the subject.
        
        Args:
            observer: The observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer):
        """
        Detach an observer from the subject.
        
        Args:
            observer: The observer to detach
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
    
    def notify(self, notification_data):
        """
        Notify all observers of a change.
        
        Args:
            notification_data: Dictionary containing notification details
        """
        for observer in self._observers:
            observer.update(notification_data)

class BookingManager(NotificationSubject):
    """
    Concrete subject that manages bookings and notifies observers.
    """
    def create_booking(self, car_id, user_id, start_date, end_date):
        """
        Create a new booking and notify observers.
        
        Args:
            car_id: The ID of the car being booked
            user_id: The ID of the user making the booking
            start_date: The start date of the booking
            end_date: The end date of the booking
            
        Returns:
            The newly created Booking object
        """
        # This import is placed here to avoid circular imports
        from models import Booking, Car
        from app import db
        
        # Create the booking (without total_price parameter)
        booking = Booking(
            car_id=car_id,
            renter_id=user_id,
            start_date=start_date,
            end_date=end_date,
            status="pending"
        )
        
        # Save to database
        db.session.add(booking)
        db.session.commit()
        
        # Get car details for notification (calculate total price here)
        car = Car.query.get(car_id)
        days = (end_date - start_date).days + 1
        total_price = days * car.daily_price
        
        # For the notification_data, you can still include the calculated total_price
        # even though it's not stored in the database
        
        return booking
    
    def update_booking_status(self, booking_id, status):
        """
        Update a booking's status and notify observers.
        
        Args:
            booking_id: The ID of the booking to update
            status: The new status
        """
        # This import is placed here to avoid circular imports
        from models import Booking, Car, User
        from app import db
        
        # Get the booking
        booking = db.session.query(Booking).get(booking_id)
        
        if booking:
            # Save old status for reference
            old_status = booking.status
            
            # Update the status
            booking.status = status
            db.session.commit()
            
            # Get additional information for notifications
            car = Car.query.get(booking.car_id)
            renter = User.query.get(booking.renter_id)
            
            # Calculate total price on the fly
            days = (booking.end_date - booking.start_date).days + 1
            total_price = days * car.daily_price
            
            # Create notification data
            notification_data = {
                'notification_type': f'booking_{status}',
                'user_id': booking.renter_id,
                'user_email': renter.email,
                'booking_id': booking.id,
                'car_name': car.model,
                'start_date': booking.start_date.strftime('%Y-%m-%d'),
                'end_date': booking.end_date.strftime('%Y-%m-%d'),
                'total_price': total_price
            }
            
            # If the status is 'rejected', check for a reason
            if status == 'rejected' and hasattr(booking, 'rejection_reason'):
                notification_data['reason'] = booking.rejection_reason
            
            # Notify observers 
            self.notify(notification_data)
            
            # Also notify car owner about status change if appropriate
            if status in ['cancelled'] and old_status in ['confirmed']:
                owner = User.query.get(car.owner_id)
                owner_notification_data = notification_data.copy()
                owner_notification_data['user_id'] = car.owner_id
                owner_notification_data['user_email'] = owner.email
                owner_notification_data['renter_name'] = renter.name
                self.notify(owner_notification_data)