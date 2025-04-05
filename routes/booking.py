# routes/booking.py
# Routes for booking management (create, view, update, cancel)

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from app import db
from models import Booking, Car, User, Message
from patterns.observer import BookingManager
from patterns.mediator import UIMediator, BookingComponent, MessageComponent

# Create Blueprint
booking_bp = Blueprint('booking', __name__)

# Create UI mediator for component communication
ui_mediator = UIMediator()

@booking_bp.route('/bookings')
@login_required
def list_bookings():
    """
    Display user's bookings.
    """
    # Get user's bookings (as renter)
    my_bookings = Booking.query.filter_by(renter_id=current_user.id).all()
    
    # If user is also a car owner, get bookings for their cars
    car_ids = [car.id for car in Car.query.filter_by(owner_id=current_user.id).all()]
    received_bookings = Booking.query.filter(Booking.car_id.in_(car_ids)).all() if car_ids else []
    
    return render_template(
        'bookings/list.html',
        my_bookings=my_bookings,
        received_bookings=received_bookings
    )

@booking_bp.route('/bookings/create/<int:car_id>', methods=['GET', 'POST'])
@login_required
def create_booking(car_id):
    """
    Create a new booking for a car.
    
    Args:
        car_id: The ID of the car to book
    """
    # Get the car
    car = Car.query.get_or_404(car_id)
    
    # Check if user owns the car (can't book your own car)
    if car.owner_id == current_user.id:
        flash('You cannot book your own car.')
        return redirect(url_for('car.view_car', car_id=car_id))
    
    if request.method == 'POST':
        # Get form data
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        # Validate dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if start_date > end_date:
                flash('Start date cannot be after end date.')
                return redirect(url_for('booking.create_booking', car_id=car_id))
                
        except ValueError:
            flash('Invalid date format.')
            return redirect(url_for('booking.create_booking', car_id=car_id))
        
        # Check if car is available for the requested dates
        if not car.is_available(start_date, end_date):
            flash('The car is not available for the selected dates.')
            return redirect(url_for('booking.create_booking', car_id=car_id))
        
        try:
            # Use BookingComponent with Mediator pattern
            booking_component = BookingComponent(ui_mediator)
            ui_mediator.register_component('booking_component', booking_component)
            
            # Set the car and create the booking
            booking_component.set_car(car_id)
            booking = booking_component.create_booking(current_user.id, start_date, end_date)
            
            # Set up the MessageComponent for communication
            message_component = MessageComponent(ui_mediator)
            ui_mediator.register_component('message_component', message_component)
            message_component.set_booking(booking.id)
            
            flash('Booking request created successfully!')
            return redirect(url_for('booking.view_booking', booking_id=booking.id))
            
        except ValueError as e:
            flash(str(e))
            return redirect(url_for('booking.create_booking', car_id=car_id))
    
    return render_template('bookings/create.html', car=car)

@booking_bp.route('/bookings/<int:booking_id>')
@login_required
def view_booking(booking_id):
    """
    View a specific booking.
    
    Args:
        booking_id: The ID of the booking to view
    """
    # Get the booking
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is authorized to view this booking
    if booking.renter_id != current_user.id and booking.car.owner_id != current_user.id:
        flash('You are not authorized to view this booking.')
        return redirect(url_for('booking.list_bookings'))
    
    # Get related messages
    messages = Message.query.filter_by(booking_id=booking_id).order_by(Message.created_at).all()
    
    return render_template('bookings/view.html', booking=booking, messages=messages)

@booking_bp.route('/bookings/<int:booking_id>/update-status', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    """
    Update a booking's status.
    
    Args:
        booking_id: The ID of the booking to update
    """
    # Get the booking
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is authorized to update this booking
    is_owner = booking.car.owner_id == current_user.id
    is_renter = booking.renter_id == current_user.id
    
    if not is_owner and not is_renter:
        flash('You are not authorized to update this booking.')
        return redirect(url_for('booking.list_bookings'))
    
    # Get new status
    new_status = request.form.get('status')
    
    # Validate status change permissions
    valid_status_changes = {
        'owner': {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['completed', 'cancelled'],
        },
        'renter': {
            'pending': ['cancelled'],
            'confirmed': ['cancelled'],
        }
    }
    
    user_type = 'owner' if is_owner else 'renter'
    
    if booking.status not in valid_status_changes[user_type] or new_status not in valid_status_changes[user_type][booking.status]:
        flash('Invalid status change.')
        return redirect(url_for('booking.view_booking', booking_id=booking_id))
    
    # Use BookingManager with Observer pattern to update status
    booking_manager = BookingManager()
    booking_manager.update_booking_status(booking_id, new_status)
    
    flash(f'Booking status updated to {new_status}.')
    return redirect(url_for('booking.view_booking', booking_id=booking_id))

@booking_bp.route('/bookings/<int:booking_id>/message', methods=['POST'])
@login_required
def send_message(booking_id):
    """
    Send a message related to a booking.
    
    Args:
        booking_id: The ID of the booking
    """
    # Get the booking
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is authorized to send messages for this booking
    if booking.renter_id != current_user.id and booking.car.owner_id != current_user.id:
        flash('You are not authorized to send messages for this booking.')
        return redirect(url_for('booking.list_bookings'))
    
    # Get message content
    content = request.form.get('content')
    
    if not content:
        flash('Message cannot be empty.')
        return redirect(url_for('booking.view_booking', booking_id=booking_id))
    
    # Determine the receiver based on the current user
    if current_user.id == booking.renter_id:
        receiver_id = booking.car.owner_id
    else:
        receiver_id = booking.renter_id
    
    # Use MessageComponent with Mediator pattern to send the message
    message_component = MessageComponent(ui_mediator)
    ui_mediator.register_component('message_component', message_component)
    message_component.set_booking(booking_id)
    message_component.send_message(current_user.id, receiver_id, content)
    
    flash('Message sent successfully.')
    return redirect(url_for('booking.view_booking', booking_id=booking_id))

@booking_bp.route('/api/check-availability', methods=['GET'])
def check_availability():
    """
    API endpoint to check car availability.
    """
    car_id = request.args.get('car_id')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if not car_id or not start_date_str or not end_date_str:
        return jsonify({'available': False, 'error': 'Missing parameters'})
    
    try:
        car = Car.query.get(car_id)
        
        if not car:
            return jsonify({'available': False, 'error': 'Car not found'})
            
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        available = car.is_available(start_date, end_date)
        
        return jsonify({'available': available})
        
    except Exception as e:
        return jsonify({'available': False, 'error': str(e)})