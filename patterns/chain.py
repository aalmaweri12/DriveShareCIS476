# Chain of Responsibility Pattern for Password Recovery

from abc import ABC, abstractmethod

class PasswordRecoveryHandler(ABC):
    """
    Abstract base class for password recovery handlers.
    Implements the Chain of Responsibility pattern.
    """
    def __init__(self):
        """
        Initialize the handler with no next handler.
        """
        self._next_handler = None
    
    def set_next(self, handler):
        """
        Set the next handler in the chain.
        
        Args:
            handler: The next handler
            
        Returns:
            The next handler for chaining
        """
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, email, answer):
        """
        Handle the password recovery request.
        
        Args:
            email: The user's email
            answer: The answer to the security question
            
        Returns:
            True if the request was handled successfully, False otherwise
        """
        pass

class QuestionOneHandler(PasswordRecoveryHandler):
    """
    Handler for the first security question.
    """
    def handle(self, email, answer):
        """
        Handle the first security question.
        
        Args:
            email: The user's email
            answer: The answer to the first security question
            
        Returns:
            True if the answer is correct, False otherwise
        """
        # Verify the answer to the first question
        if self._verify_answer(email, answer):
            # If successful and there's a next handler, pass to it
            if self._next_handler:
                return self._next_handler.handle(email, None)
            return True
        
        return False
    
    def _verify_answer(self, email, answer):
        """
        Verify the answer to the first security question.
        
        Args:
            email: The user's email
            answer: The answer to verify
            
        Returns:
            True if the answer is correct, False otherwise
        """
        # This import is placed here to avoid circular imports
        from models.user import User
        from app import db
        
        user = db.session.query(User).filter_by(email=email).first()
        
        if not user:
            return False
        
        return user.security_answer_1.lower() == answer.lower()

class QuestionTwoHandler(PasswordRecoveryHandler):
    """
    Handler for the second security question.
    """
    def handle(self, email, answer):
        """
        Handle the second security question.
        
        Args:
            email: The user's email
            answer: The answer to the second security question
            
        Returns:
            True if the answer is correct, False otherwise
        """
        # Verify the answer to the second question
        if self._verify_answer(email, answer):
            # If successful and there's a next handler, pass to it
            if self._next_handler:
                return self._next_handler.handle(email, None)
            return True
        
        return False
    
    def _verify_answer(self, email, answer):
        """
        Verify the answer to the second security question.
        
        Args:
            email: The user's email
            answer: The answer to verify
            
        Returns:
            True if the answer is correct, False otherwise
        """
        # This import is placed here to avoid circular imports
        from models.user import User
        from app import db
        
        user = db.session.query(User).filter_by(email=email).first()
        
        if not user:
            return False
        
        return user.security_answer_2.lower() == answer.lower()

class QuestionThreeHandler(PasswordRecoveryHandler):
    """
    Handler for the third security question.
    """
    def handle(self, email, answer):
        """
        Handle the third security question.
        
        Args:
            email: The user's email
            answer: The answer to the third security question
            
        Returns:
            True if the answer is correct, False otherwise
        """
        # Verify the answer to the third question
        if self._verify_answer(email, answer):
            # If successful and there's a next handler, pass to it
            if self._next_handler:
                return self._next_handler.handle(email, None)
            return True
        
        return False
    
    def _verify_answer(self, email, answer):
        """
        Verify the answer to the third security question.
        
        Args:
            email: The user's email
            answer: The answer to verify
            
        Returns:
            True if the answer is correct, False otherwise
        """
        # This import is placed here to avoid circular imports
        from models.user import User
        from app import db
        
        user = db.session.query(User).filter_by(email=email).first()
        
        if not user:
            return False
        
        return user.security_answer_3.lower() == answer.lower()

class PasswordResetHandler(PasswordRecoveryHandler):
    """
    Final handler that resets the password after all security questions are verified.
    """
    def handle(self, email, new_password):
        """
        Reset the user's password.
        
        Args:
            email: The user's email
            new_password: The new password
            
        Returns:
            True if the password was reset successfully, False otherwise
        """
        return self.reset_password(email, new_password)
    
    def reset_password(self, email, new_password):
        """
        Reset the user's password.
        
        Args:
            email: The user's email
            new_password: The new password
            
        Returns:
            True if the password was reset successfully, False otherwise
        """
        # This import is placed here to avoid circular imports
        from models.user import User
        from app import db
        from werkzeug.security import generate_password_hash
        
        user = db.session.query(User).filter_by(email=email).first()
        
        if not user:
            return False
        
        # Update the password with a hashed version
        user.password = generate_password_hash(new_password)
        
        # Save to database
        db.session.commit()
        
        return True