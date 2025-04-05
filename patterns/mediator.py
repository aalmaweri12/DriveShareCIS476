# Mediator Pattern for UI Components

from abc import ABC, abstractmethod

class UIMediator:
    """
    Mediator class that coordinates communication between UI components.
    """
    def __init__(self):
        """
        Initialize the mediator with an empty dictionary of components.
        """
        self._components = {}
    
    def register_component(self, name, component):
        """
        Register a component with the mediator.
        
        Args:
            name: The name of the component
            component: The component instance
        """
        self._components[name] = component
        component.mediator = self
    
    def notify(self, sender, event, data=None):
        """
        Notify the mediator of an event, which will coordinate the response.
        
        Args:
            sender: The component sending the notification
            event: The event type
            data: Additional data for the event (optional)
        """
        if event == "search":
            # Coordinate search-related actions
            if "search_component" in self._components:
                self._components["search_component"].display_results(data)
        
        elif event == "select_car":
            # When a car is selected, update the booking component
            if "booking_component" in self._components:
                self._components["booking_component"].set_car(data)
        
        elif event == "create_booking":
            # When a booking is created, update related components
            if "message_component" in self._components:
                self._components["message_component"].set_booking(data)
        
        elif event == "send_message":
            # When a message is sent, update the conversation view
            if "message_component" in self._components:
                self._components["message_component"].refresh_messages()

class BaseComponent(ABC):
    """
    Abstract base class for UI components.
    """
    def __init__(self, mediator=None):
        """
        Initialize the component with an optional mediator.
        
        Args:
            mediator: The mediator instance (optional)
        """
        self._mediator = mediator
    
    @property
    def mediator(self):
        """
        Get the mediator instance.
        
        Returns:
            The mediator instance
        """
        return self._mediator
    
    @mediator.setter
    def mediator(self, mediator):
        """
        Set the mediator instance.
        
        Args:
            mediator: The mediator instance
        """
        self._mediator = mediator

class SearchComponent(BaseComponent):
    """
    Component for searching cars.
    """
    def search(self, criteria):
        """
        Search for cars based on criteria.
        
        Args:
            criteria: The search criteria
        """
        # This import is placed here to avoid circular imports
        from models.car import Car
        from app import db
        
        # Perform the search
        query = db.session.query(Car)
        
        if 'location' in criteria and criteria['location']:
            query = query.filter(Car.location.like(f"%{criteria['location']}%"))
        
        if 'start_date' in criteria and criteria['start_date']:
            query = query.filter(Car.availability_start <= criteria['start_date'])
        
        if 'end_date' in criteria and criteria['end_date']:
            query = query.filter(Car.availability_end >= criteria['end_date'])
            
        results = query.all()
        
        # Notify the mediator of the search results
        self.mediator.notify(self, "search", results)
    
    def display_results(self, results):
        """
        Display the search results.
        
        Args:
            results: The search results
        """
        # In a real application, this would update the UI
        # For this simple implementation, we'll just print the results
        print(f"Displaying {len(results)} search results")

# Enhanced BookingComponent in mediator.py
class BookingComponent(BaseComponent):
    """
    Component for creating bookings.
    """
    def __init__(self, mediator=None):
        """
        Initialize the booking component.
        
        Args:
            mediator: The mediator instance (optional)
        """
        super().__init__(mediator)
        self._car_id = None
    
    def set_car(self, car_id):
        """
        Set the car for booking.
        
        Args:
            car_id: The ID of the car to book
        """
        self._car_id = car_id
    
    def create_booking(self, user_id, start_date, end_date):
        """
        Create a booking for the selected car.
        
        Args:
            user_id: The ID of the user making the booking
            start_date: The start date of the booking
            end_date: The end date of the booking
        """
        if not self._car_id:
            raise ValueError("No car selected for booking")
        
        # This import is placed here to avoid circular imports
        from patterns.observer import BookingManager, NotificationSubject, EmailNotifier, AppNotifier
        from models.car import Car
        from models.user import User
        from app import db
        
        # Create the booking using the BookingManager
        booking_manager = BookingManager()
        booking = booking_manager.create_booking(
            self._car_id, user_id, start_date, end_date
        )
        
        # Notify the mediator of the booking creation
        self.mediator.notify(self, "create_booking", booking.id)
        
        # Get additional information for email notifications
        car = Car.query.get(self._car_id)
        renter = User.query.get(user_id)
        owner = User.query.get(car.owner_id)
        
        # Calculate total price
        days = (end_date - start_date).days + 1
        total_price = days * car.daily_price
        
        # Create notification subject and observers
        notification_subject = NotificationSubject()
        email_notifier = EmailNotifier()
        app_notifier = AppNotifier()
        
        # Register observers
        notification_subject.attach(email_notifier)
        notification_subject.attach(app_notifier)
        
        # Prepare renter notification data
        renter_notification_data = {
            'notification_type': 'booking_created',
            'user_id': user_id,
            'user_email': renter.email,
            'booking_id': booking.id,
            'car_name': car.model,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'total_price': total_price
        }
        
        # Send notification to renter
        notification_subject.notify(renter_notification_data)
        
        # Prepare owner notification data
        owner_notification_data = {
            'notification_type': 'booking_request',
            'user_id': car.owner_id,
            'user_email': owner.email,
            'booking_id': booking.id,
            'car_name': car.model,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'total_price': total_price,
            'renter_name': renter.name,
            'message': f"You have a new booking request for your car '{car.model}'"
        }
        
        # Send notification to car owner
        notification_subject.notify(owner_notification_data)
        
        return booking

class MessageComponent(BaseComponent):
    """
    Component for sending and receiving messages.
    """
    def __init__(self, mediator=None):
        """
        Initialize the message component.
        
        Args:
            mediator: The mediator instance (optional)
        """
        super().__init__(mediator)
        self._booking_id = None
        self._conversation = []
    
    def set_booking(self, booking_id):
        """
        Set the booking context for messages.
        
        Args:
            booking_id: The ID of the booking
        """
        self._booking_id = booking_id
        self.refresh_messages()
    
    def send_message(self, sender_id, receiver_id, content):
        """
        Send a message.
        
        Args:
            sender_id: The ID of the message sender
            receiver_id: The ID of the message receiver
            content: The message content
        """
        # This import is placed here to avoid circular imports
        from models.message import Message
        from app import db
        
        # Create the message
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            booking_id=self._booking_id,
            content=content,
            is_read=False
        )
        
        # Save to database
        db.session.add(message)
        db.session.commit()
        
        # Notify the mediator
        self.mediator.notify(self, "send_message")
        
        return message
    
    def refresh_messages(self):
        """
        Refresh the conversation messages.
        """
        if not self._booking_id:
            self._conversation = []
            return
        
        # This import is placed here to avoid circular imports
        from models.message import Message
        from app import db
        
        # Get all messages for this booking
        messages = db.session.query(Message).filter_by(
            booking_id=self._booking_id
        ).order_by(Message.created_at).all()
        
        self._conversation = messages
    
    def display_messages(self):
        """
        Display the conversation messages.
        """
        # In a real application, this would update the UI
        # For this simple implementation, we'll just print the messages
        print(f"Displaying {len(self._conversation)} messages")