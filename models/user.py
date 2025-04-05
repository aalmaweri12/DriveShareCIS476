# models/user.py
# User model to store user account information

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from database import db
from app import db, login_manager

class User(UserMixin, db.Model):
    """
    Model representing a user in the system.
    Stores information about registered users including car owners and renters.
    Inherits from UserMixin to provide Flask-Login compatibility.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Security questions and answers for password recovery
    security_question_1 = db.Column(db.String(200), nullable=False)
    security_answer_1 = db.Column(db.String(200), nullable=False)
    security_question_2 = db.Column(db.String(200), nullable=False)
    security_answer_2 = db.Column(db.String(200), nullable=False)
    security_question_3 = db.Column(db.String(200), nullable=False)
    security_answer_3 = db.Column(db.String(200), nullable=False)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    cars = db.relationship('Car', back_populates='owner', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', foreign_keys='Booking.renter_id', back_populates='renter')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', back_populates='receiver')
    # In models/user.py
# Add this to the existing relationships in the User class
    payment_methods = db.relationship('PaymentMethod', back_populates='user', cascade='all, delete-orphan')
    def __init__(self, email, password, name, security_question_1, security_answer_1,
                 security_question_2, security_answer_2, security_question_3, security_answer_3):
        """
        Initialize a new user.
        
        Args:
            email: User's email address
            password: Plaintext password (will be hashed before storing)
            name: User's full name
            security_question_1: First security question
            security_answer_1: Answer to first security question
            security_question_2: Second security question
            security_answer_2: Answer to second security question
            security_question_3: Third security question
            security_answer_3: Answer to third security question
        """
        self.email = email
        self.password = generate_password_hash(password)
        self.name = name
        self.security_question_1 = security_question_1
        self.security_answer_1 = security_answer_1
        self.security_question_2 = security_question_2
        self.security_answer_2 = security_answer_2
        self.security_question_3 = security_question_3
        self.security_answer_3 = security_answer_3

    def __repr__(self):
        """
        String representation of the user.
        
        Returns:
            String representation
        """
        return f"<User {self.id} - {self.email}>"

    def check_password(self, password):
        """
        Verify the user's password.
        
        Args:
            password: The password to check
            
        Returns:
            True if the password is correct, False otherwise
        """
        return check_password_hash(self.password, password)

    def to_dict(self):
        """
        Convert the user to a dictionary (excluding sensitive information).
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def get_security_question(self, question_number):
        """
        Get a specific security question.
        
        Args:
            question_number: The question number (1, 2, or 3)
            
        Returns:
            The security question
        """
        if question_number == 1:
            return self.security_question_1
        elif question_number == 2:
            return self.security_question_2
        elif question_number == 3:
            return self.security_question_3
        else:
            raise ValueError("Invalid question number")

    def check_security_answer(self, question_number, answer):
        """
        Check if a security answer is correct.
        
        Args:
            question_number: The question number (1, 2, or 3)
            answer: The answer to check
            
        Returns:
            True if the answer is correct, False otherwise
        """
        if question_number == 1:
            return self.security_answer_1.lower() == answer.lower()
        elif question_number == 2:
            return self.security_answer_2.lower() == answer.lower()
        elif question_number == 3:
            return self.security_answer_3.lower() == answer.lower()
        else:
            raise ValueError("Invalid question number")

    def change_password(self, new_password):
        """
        Change the user's password.
        
        Args:
            new_password: The new password
        """
        from app import db
        
        self.password = generate_password_hash(new_password)
        db.session.commit()

    @staticmethod
    def get_user_by_email(email):
        """
        Get a user by email.
        
        Args:
            email: The email address
            
        Returns:
            The User object if found, None otherwise
        """
        return User.query.filter_by(email=email).first()

@login_manager.user_loader
def load_user(user_id):
    """
    Load a user by ID for Flask-Login.
    
    Args:
        user_id: The user ID
        
    Returns:
        The User object if found, None otherwise
    """
    return User.query.get(int(user_id))