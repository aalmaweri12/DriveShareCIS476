# models/message.py
# Message model to store communication between users

from datetime import datetime
from database import db
from app import db

class Message(db.Model):
    """
    Model representing a message between users in the system.
    Stores communication between car owners and renters.
    """
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_messages')
    booking = db.relationship('Booking', back_populates='messages')

    def __init__(self, sender_id, receiver_id, content, booking_id=None, is_read=False):
        """
        Initialize a new message.
        
        Args:
            sender_id: The ID of the message sender
            receiver_id: The ID of the message receiver
            content: The message content
            booking_id: The ID of the related booking (optional)
            is_read: Whether the message has been read (default: False)
        """
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.booking_id = booking_id
        self.is_read = is_read

    def __repr__(self):
        """
        String representation of the message.
        
        Returns:
            String representation
        """
        return f"<Message {self.id} - From {self.sender_id} to {self.receiver_id}>"

    def to_dict(self):
        """
        Convert the message to a dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'booking_id': self.booking_id,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def mark_as_read(self):
        """
        Mark the message as read.
        """
        from app import db
        
        self.is_read = True
        db.session.commit()

    @staticmethod
    def get_conversation(user1_id, user2_id, booking_id=None):
        """
        Get the conversation between two users, optionally filtered by booking.
        
        Args:
            user1_id: The ID of the first user
            user2_id: The ID of the second user
            booking_id: The ID of the booking (optional)
            
        Returns:
            List of messages between the users
        """
        from app import db
        
        # Build the query to get messages between the two users
        query = Message.query.filter(
            db.or_(
                db.and_(Message.sender_id == user1_id, Message.receiver_id == user2_id),
                db.and_(Message.sender_id == user2_id, Message.receiver_id == user1_id)
            )
        )
        
        # If booking_id is provided, filter by booking
        if booking_id is not None:
            query = query.filter(Message.booking_id == booking_id)
        
        # Order by creation time
        query = query.order_by(Message.created_at)
        
        return query.all()

    @staticmethod
    def get_unread_count(user_id):
        """
        Get the count of unread messages for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Count of unread messages
        """
        return Message.query.filter_by(receiver_id=user_id, is_read=False).count()

    @staticmethod
    def send_message(sender_id, receiver_id, content, booking_id=None):
        """
        Static method to create and send a new message.
        
        Args:
            sender_id: The ID of the message sender
            receiver_id: The ID of the message receiver
            content: The message content
            booking_id: The ID of the related booking (optional)
            
        Returns:
            The newly created Message object
        """
        from app import db
        
        # Create the message
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            booking_id=booking_id,
            is_read=False
        )
        
        # Add to database
        db.session.add(message)
        db.session.commit()
        
        # In a real application, you would trigger a notification here
        # using the Observer pattern to notify the receiver
        
        return message