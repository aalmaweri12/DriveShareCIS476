# routes/auth.py
# Routes for user authentication (register, login, logout, password recovery)

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from models import User
from patterns.singleton import UserSession
from patterns.chain import QuestionOneHandler, QuestionTwoHandler, QuestionThreeHandler, PasswordResetHandler

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        # Get security questions and answers
        security_question_1 = request.form.get('security_question_1')
        security_answer_1 = request.form.get('security_answer_1')
        security_question_2 = request.form.get('security_question_2')
        security_answer_2 = request.form.get('security_answer_2')
        security_question_3 = request.form.get('security_question_3')
        security_answer_3 = request.form.get('security_answer_3')
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('Email already exists.')
            return redirect(url_for('auth.register'))
            
        # Validate form data
        if not email or not password or not name:
            flash('Please fill in all required fields.')
            return redirect(url_for('auth.register'))
            
        if not security_question_1 or not security_answer_1 or not security_question_2 or not security_answer_2 or not security_question_3 or not security_answer_3:
            flash('Please fill in all security questions and answers.')
            return redirect(url_for('auth.register'))
            
        # Create new user
        new_user = User(
            email=email,
            password=password,  # Password will be hashed in __init__
            name=name,
            security_question_1=security_question_1,
            security_answer_1=security_answer_1,
            security_question_2=security_question_2,
            security_answer_2=security_answer_2,
            security_question_3=security_question_3,
            security_answer_3=security_answer_3
        )
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        
        # Log in the new user
        login_user(new_user)
        
        # Use Singleton pattern to manage user session
        user_session = UserSession.get_instance()
        user_session.login(new_user.id)
        
        flash('Registration successful!')
        return redirect(url_for('main.index'))
        
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
            
        # Log in the user
        login_user(user, remember=remember)
        
        # Use Singleton pattern to manage user session
        user_session = UserSession.get_instance()
        user_session.login(user.id)
        
        return redirect(url_for('main.index'))
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout route.
    """
    # Use Singleton pattern to manage user session
    user_session = UserSession.get_instance()
    user_session.logout()
    
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Forgot password route (step 1).
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email not found.')
            return redirect(url_for('auth.forgot_password'))
            
        # Store email in session for the next steps
        session['reset_email'] = email
        
        # Redirect to security question 1
        return redirect(url_for('auth.security_question', question_number=1))
        
    return render_template('auth/forgot_password.html')

@auth_bp.route('/security-question/<int:question_number>', methods=['GET', 'POST'])
def security_question(question_number):
    """
    Security question route for password recovery.
    
    Args:
        question_number: The security question number (1, 2, or 3)
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    # Check if reset_email is in session
    if 'reset_email' not in session:
        flash('Please start the password recovery process again.')
        return redirect(url_for('auth.forgot_password'))
        
    email = session['reset_email']
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('User not found.')
        return redirect(url_for('auth.forgot_password'))
        
    if question_number not in [1, 2, 3]:
        flash('Invalid question number.')
        return redirect(url_for('auth.forgot_password'))
        
    # Get the security question
    question = user.get_security_question(question_number)
    
    if request.method == 'POST':
        # Get form data
        answer = request.form.get('answer')
        
        # Use Chain of Responsibility pattern for security questions
        if question_number == 1:
            # Create the first handler
            handler = QuestionOneHandler()
            
            if handler.handle(email, answer):
                # If successful, move to question 2
                return redirect(url_for('auth.security_question', question_number=2))
            else:
                flash('Incorrect answer. Please try again.')
                
        elif question_number == 2:
            # Create the second handler
            handler = QuestionTwoHandler()
            
            if handler.handle(email, answer):
                # If successful, move to question 3
                return redirect(url_for('auth.security_question', question_number=3))
            else:
                flash('Incorrect answer. Please try again.')
                
        elif question_number == 3:
            # Create the third handler
            handler = QuestionThreeHandler()
            
            if handler.handle(email, answer):
                # If successful, move to reset password
                return redirect(url_for('auth.reset_password'))
            else:
                flash('Incorrect answer. Please try again.')
                
    return render_template('auth/security_question.html', question=question, question_number=question_number)

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """
    Reset password route (final step).
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    # Check if reset_email is in session
    if 'reset_email' not in session:
        flash('Please start the password recovery process again.')
        return redirect(url_for('auth.forgot_password'))
        
    email = session['reset_email']
    
    if request.method == 'POST':
        # Get form data
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('auth.reset_password'))
            
        # Create the final handler
        handler = PasswordResetHandler()
        
        if handler.handle(email, password):
            # Clear session data
            session.pop('reset_email', None)
            
            flash('Password has been reset. You can now log in with your new password.')
            return redirect(url_for('auth.login'))
        else:
            flash('An error occurred. Please try again.')
            
    return render_template('auth/reset_password.html')