from flask import Flask, render_template
from flask_login import LoginManager
import os
from datetime import datetime
from database import db  # Import db from the separate database.py file

# Initialize extensions
# db = SQLAlchemy()  # Remove this line since we're importing db from database.py
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name='default'):
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load config
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # Register blueprints
    from routes import register_blueprints
    register_blueprints(app)
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    # Context processors (for template variables)
    @app.context_processor
    def utility_processor():
        def format_date(date):
            return date.strftime('%b %d, %Y')
        
        def format_datetime(datetime_obj):
            return datetime_obj.strftime('%b %d, %Y %I:%M %p')
        
        def calculate_days(start_date, end_date):
            delta = end_date - start_date
            return delta.days + 1
        
        def calculate_total_price(daily_price, start_date, end_date):
            days = calculate_days(start_date, end_date)
            return days * daily_price
        
        return dict(
            format_date=format_date,
            format_datetime=format_datetime,
            calculate_days=calculate_days,
            calculate_total_price=calculate_total_price
        )
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

# Main entry point
if __name__ == '__main__':
    # Determine environment from environment variable
    env = os.environ.get('FLASK_ENV', 'default')
    app = create_app(env)
    app.run(debug=app.config['DEBUG'])