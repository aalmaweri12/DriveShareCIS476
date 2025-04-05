# routes/__init__.py
# Initialize the routes package and set up function to register all blueprints

from flask import Blueprint
from .auth import auth_bp
from .car import car_bp
from .booking import booking_bp
from .message import message_bp
from .payment import payment_bp

# Create main blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Home page route.
    """
    from flask import render_template
    return render_template('index.html')

def register_blueprints(app):
    """
    Register all blueprints with the Flask application.
    
    Args:
        app: The Flask application
    """
    # Register main blueprint
    app.register_blueprint(main_bp)
    
    # Register feature blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(car_bp, url_prefix='/cars')
    app.register_blueprint(booking_bp, url_prefix='/bookings')
    app.register_blueprint(message_bp, url_prefix='/messages')
    app.register_blueprint(payment_bp, url_prefix='/payments')