# routes/payment.py
# Routes for payment processing

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from database import db
from models import Booking, Payment, PaymentMethod
from patterns.proxy import PaymentProxy
from patterns.observer import NotificationSubject, EmailNotifier, AppNotifier

# Create Blueprint
payment_bp = Blueprint('payment', __name__)

# This code should be added to your existing payment.py file in the routes directory

# Update the make_payment function to include email notifications
@payment_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def make_payment(booking_id):
    """
    Process payment for a booking.
    
    Args:
        booking_id: The ID of the booking to pay for
    """
    # Get the booking
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is authorized to make the payment
    if booking.renter_id != current_user.id:
        flash('You are not authorized to make this payment.')
        return redirect(url_for('booking.list_bookings'))
    
    # Check if booking is in a state that allows payment
    if booking.status not in ['pending', 'confirmed']:
        flash('This booking is not available for payment.')
        return redirect(url_for('booking.view_booking', booking_id=booking_id))
    
    # Check if payment already exists
    existing_payment = Payment.query.filter_by(booking_id=booking_id).first()
    if existing_payment and existing_payment.status == 'completed':
        flash('Payment has already been processed for this booking.')
        return redirect(url_for('booking.view_booking', booking_id=booking_id))
    
    # Calculate the total amount
    total_days = (booking.end_date - booking.start_date).days + 1
    amount = booking.car.daily_price * total_days
    
    if request.method == 'POST':
        payment_type = request.form.get('payment_type', 'new')
        payment_method_id = None
        
        # Process payment based on payment type
        if payment_type == 'saved':
            card_id = request.form.get('card_id')
            if not card_id:
                flash('Please select a saved card.')
                return redirect(url_for('payment.make_payment', booking_id=booking_id))
            
            # Get the saved card
            card = PaymentMethod.query.get(card_id)
            if not card or card.user_id != current_user.id:
                flash('Invalid payment method selected.')
                return redirect(url_for('payment.make_payment', booking_id=booking_id))
            
            # Check if card is expired
            if card.is_expired():
                flash('The selected card is expired. Please use a different card.')
                return redirect(url_for('payment.make_payment', booking_id=booking_id))
                
            payment_method_id = card.id
                
        else:  # New card
            # Get form data for the new card
            card_holder_name = request.form.get('card_holder_name')
            card_number = request.form.get('card_number', '').replace(' ', '')
            expiry_date = request.form.get('expiry_date', '')
            cvv = request.form.get('cvv')
            save_card = 'save_card' in request.form
            make_default = 'make_default' in request.form
            
            # Validate card details
            if not card_holder_name or not card_number or not expiry_date or not cvv:
                flash('Please fill in all card details.')
                return redirect(url_for('payment.make_payment', booking_id=booking_id))
            
            # Simple validation
            if len(card_number) < 13 or len(card_number) > 19:
                flash('Invalid card number.')
                return redirect(url_for('payment.make_payment', booking_id=booking_id))
                
            # Parse expiry date (MM/YY)
            try:
                expiry_parts = expiry_date.split('/')
                expiry_month = int(expiry_parts[0])
                expiry_year = int(expiry_parts[1]) + 2000  # Assuming 20xx
                
                if expiry_month < 1 or expiry_month > 12:
                    raise ValueError("Invalid month")
                    
                # Check if card is expired
                now = datetime.now()
                if expiry_year < now.year or (expiry_year == now.year and expiry_month < now.month):
                    flash('The card is expired.')
                    return redirect(url_for('payment.make_payment', booking_id=booking_id))
                    
            except (IndexError, ValueError):
                flash('Invalid expiry date. Use MM/YY format.')
                return redirect(url_for('payment.make_payment', booking_id=booking_id))
            
            # Determine card type (simplified)
            if card_number.startswith('4'):
                card_type = 'Visa'
            elif card_number.startswith('5'):
                card_type = 'Mastercard'
            elif card_number.startswith('3'):
                card_type = 'American Express'
            elif card_number.startswith('6'):
                card_type = 'Discover'
            else:
                card_type = 'Credit Card'
            
            # Save the card if requested
            if save_card:
                # If make_default is checked, set all other cards to non-default
                if make_default:
                    for card in current_user.payment_methods:
                        card.is_default = False
                    
                new_card = PaymentMethod(
                    user_id=current_user.id,
                    card_type=card_type,
                    last_four=card_number[-4:],
                    card_holder_name=card_holder_name,
                    expiry_month=expiry_month,
                    expiry_year=expiry_year,
                    is_default=make_default or len(current_user.payment_methods) == 0  # Default if first card
                )
                
                db.session.add(new_card)
                db.session.commit()
                
                payment_method_id = new_card.id
        
        # Use PaymentProxy to process the payment
        payment_proxy = PaymentProxy()
        success = payment_proxy.process_payment(booking_id, amount)
        
        if success:
            # Update the payment with the payment method ID if it was a saved card
            if payment_method_id:
                payment = Payment.query.filter_by(booking_id=booking_id).first()
                if payment:
                    payment.payment_method_id = payment_method_id
                    db.session.commit()
            
            # Send email notification using Observer pattern
            notification_subject = NotificationSubject()
            email_notifier = EmailNotifier()
            app_notifier = AppNotifier()
            
            # Register observers
            notification_subject.attach(email_notifier)
            notification_subject.attach(app_notifier)
            
            # Create notification data
            notification_data = {
                'notification_type': 'payment_confirmation',
                'user_id': current_user.id,
                'user_email': current_user.email,
                'booking_id': booking_id,
                'amount': amount,
                'payment_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'car_name': booking.car.model,
                'start_date': booking.start_date.strftime('%Y-%m-%d'),
                'end_date': booking.end_date.strftime('%Y-%m-%d')
            }
            
            # Send notifications
            notification_subject.notify(notification_data)
            
            flash('Payment processed successfully!')
            return redirect(url_for('booking.view_booking', booking_id=booking_id))
        else:
            flash('Payment processing failed. Please try again.')
    
    return render_template('payments/payment.html', booking=booking, amount=amount)

@payment_bp.route('/payment/history')
@login_required
def payment_history():
    """
    Display payment history for the current user.
    """
    # Get bookings where the user is the renter
    renter_bookings = Booking.query.filter_by(renter_id=current_user.id).all()
    renter_booking_ids = [b.id for b in renter_bookings]
    
    # Get payments for these bookings
    payments_made = Payment.query.filter(Payment.booking_id.in_(renter_booking_ids)).all()
    
    # Get cars owned by the user
    car_ids = [car.id for car in current_user.cars]
    
    # Get bookings for these cars
    owner_bookings = Booking.query.filter(Booking.car_id.in_(car_ids)).all()
    owner_booking_ids = [b.id for b in owner_bookings]
    
    # Get payments for these bookings
    payments_received = Payment.query.filter(Payment.booking_id.in_(owner_booking_ids)).all()
    
    return render_template(
        'payments/history.html',
        payments_made=payments_made,
        payments_received=payments_received
    )

@payment_bp.route('/payment/refund/<int:payment_id>', methods=['POST'])
@login_required
def refund_payment(payment_id):
    """
    Process a refund for a payment.
    
    Args:
        payment_id: The ID of the payment to refund
    """
    # Get the payment
    payment = Payment.query.get_or_404(payment_id)
    
    # Get the booking
    booking = payment.booking
    
    # Check if user is authorized to process the refund
    is_car_owner = booking.car.owner_id == current_user.id
    
    if not is_car_owner:
        flash('You are not authorized to process this refund.')
        return redirect(url_for('payment.payment_history'))
    
    # Check if payment can be refunded
    if payment.status != 'completed':
        flash('This payment cannot be refunded.')
        return redirect(url_for('payment.payment_history'))
    
    # Process the refund
    payment.refund_payment()
    
    flash('Refund processed successfully!')
    return redirect(url_for('payment.payment_history'))

@payment_bp.route('/payment-methods')
@login_required
def payment_methods():
    """
    Display and manage payment methods.
    """
    payment_methods = PaymentMethod.query.filter_by(user_id=current_user.id).all()
    return render_template('payments/payment_methods.html', payment_methods=payment_methods)

@payment_bp.route('/payment-methods/delete/<int:method_id>', methods=['POST'])
@login_required
def delete_payment_method(method_id):
    """
    Delete a payment method.
    
    Args:
        method_id: The ID of the payment method to delete
    """
    payment_method = PaymentMethod.query.get_or_404(method_id)
    
    # Check if the payment method belongs to the current user
    if payment_method.user_id != current_user.id:
        flash('You are not authorized to delete this payment method.')
        return redirect(url_for('payment.payment_methods'))
    
    # Check if it's the default payment method
    was_default = payment_method.is_default
    
    # Delete the payment method
    db.session.delete(payment_method)
    
    # If it was the default, set a new default if there are other payment methods
    if was_default:
        remaining_method = PaymentMethod.query.filter_by(user_id=current_user.id).first()
        if remaining_method:
            remaining_method.is_default = True
    
    db.session.commit()
    
    flash('Payment method deleted successfully.')
    return redirect(url_for('payment.payment_methods'))

@payment_bp.route('/payment-methods/set-default/<int:method_id>', methods=['POST'])
@login_required
def set_default_payment_method(method_id):
    """
    Set a payment method as the default.
    
    Args:
        method_id: The ID of the payment method to set as default
    """
    payment_method = PaymentMethod.query.get_or_404(method_id)
    
    # Check if the payment method belongs to the current user
    if payment_method.user_id != current_user.id:
        flash('You are not authorized to modify this payment method.')
        return redirect(url_for('payment.payment_methods'))
    
    # Set all payment methods to non-default
    for method in current_user.payment_methods:
        method.is_default = False
    
    # Set the selected payment method as default
    payment_method.is_default = True
    
    db.session.commit()
    
    flash('Default payment method updated successfully.')
    return redirect(url_for('payment.payment_methods'))

@payment_bp.route('/api/payment-status/<int:booking_id>')
@login_required
def payment_status(booking_id):
    """
    API endpoint to check payment status.
    
    Args:
        booking_id: The ID of the booking
    """
    # Get the booking
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is authorized
    if booking.renter_id != current_user.id and booking.car.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get payment
    payment = Payment.query.filter_by(booking_id=booking_id).first()
    
    if not payment:
        return jsonify({
            'status': 'unpaid',
            'booking_id': booking_id
        })
    
    return jsonify({
        'status': payment.status,
        'amount': payment.amount,
        'booking_id': booking_id,
        'payment_id': payment.id,
        'date': payment.created_at.strftime('%Y-%m-%d %H:%M:%S')
    })