# Singleton Pattern for User Session Management

class UserSession:
    """
    Singleton pattern implementation for managing user sessions.
    Ensures only one user session exists at a time.
    """
    _instance = None
    
    def __new__(cls):
        """
        Create a new instance only if one doesn't exist.
        Returns the single instance of UserSession.
        """
        if cls._instance is None:
            cls._instance = super(UserSession, cls).__new__(cls)
            cls._instance.user_id = None
            cls._instance.is_authenticated = False
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance or create one if it doesn't exist.
        """
        if cls._instance is None:
            return cls()
        return cls._instance
    
    def login(self, user_id):
        """
        Log in a user by setting the user_id and authentication status.
        
        Args:
            user_id: The ID of the user logging in
        """
        self.user_id = user_id
        self.is_authenticated = True
    
    def logout(self):
        """
        Log out the current user by resetting the user_id and authentication status.
        """
        self.user_id = None
        self.is_authenticated = False
    
    def get_current_user(self):
        """
        Get the current logged-in user.
        
        Returns:
            The User object if authenticated, None otherwise
        """
        if not self.is_authenticated:
            return None
            
        # This import is placed here to avoid circular imports
        from models.user import User
        from app import db
        
        return db.session.query(User).get(self.user_id)