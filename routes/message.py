# routes/message.py
# Routes for messaging functionality

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user

from app import db
from models import Message, User, Booking, Car
from patterns.mediator import UIMediator, MessageComponent
from patterns.observer import NotificationSubject, EmailNotifier, AppNotifier

# Create Blueprint
message_bp = Blueprint('message', __name__)

# Create UI mediator for component communication
ui_mediator = UIMediator()

@message_bp.route('/messages')
@login_required
def inbox():
    """
    Display user's message inbox.
    """
    # Get all unique conversations (grouped by the other user)
    sent_messages = Message.query.filter_by(sender_id=current_user.id).all()
    received_messages = Message.query.filter_by(receiver_id=current_user.id).all()
    
    # Combine messages and get unique conversations
    conversations = {}
    
    # Process sent messages
    for msg in sent_messages:
        other_user_id = msg.receiver_id
        if other_user_id not in conversations:
            other_user = User.query.get(other_user_id)
            conversations[other_user_id] = {
                'user': other_user,
                'last_message': msg,
                'unread_count': 0
            }
        elif msg.created_at > conversations[other_user_id]['last_message'].created_at:
            conversations[other_user_id]['last_message'] = msg
    
    # Process received messages
    for msg in received_messages:
        other_user_id = msg.sender_id
        if other_user_id not in conversations:
            other_user = User.query.get(other_user_id)
            conversations[other_user_id] = {
                'user': other_user,
                'last_message': msg,
                'unread_count': 1 if not msg.is_read else 0
            }
        else:
            if msg.created_at > conversations[other_user_id]['last_message'].created_at:
                conversations[other_user_id]['last_message'] = msg
            if not msg.is_read:
                conversations[other_user_id]['unread_count'] += 1
    
    # Convert to list and sort by most recent message
    conversation_list = list(conversations.values())
    conversation_list.sort(key=lambda x: x['last_message'].created_at, reverse=True)
    
    return render_template('messages/inbox.html', conversations=conversation_list)

@message_bp.route('/messages/conversation/<int:user_id>', methods=['GET', 'POST'])
@login_required
def conversation(user_id):
    """
    View and continue a conversation with another user.
    
    Args:
        user_id: The ID of the other user in the conversation
    """
    # Get the other user
    other_user = User.query.get_or_404(user_id)
    
    # Check if there's a booking context
    booking_id = request.args.get('booking_id')
    booking = None
    if booking_id:
        booking = Booking.query.get(booking_id)
        # Verify the booking involves both users
        if booking and (booking.renter_id != current_user.id and booking.renter_id != user_id) and \
           (booking.car.owner_id != current_user.id and booking.car.owner_id != user_id):
            booking = None
    
    # Handle sending a new message
    if request.method == 'POST':
        content = request.form.get('content')
        
        if not content:
            flash('Message cannot be empty.')
            return redirect(url_for('message.conversation', user_id=user_id, booking_id=booking_id))
        
        # Use MessageComponent with Mediator pattern
        message_component = MessageComponent(ui_mediator)
        ui_mediator.register_component('message_component', message_component)
        
        if booking:
            message_component.set_booking(booking.id)
            
        # Send the message
        message = message_component.send_message(current_user.id, user_id, content)
        
        # Use Observer pattern to send notification
        notification = NotificationSubject()
        notification.attach(EmailNotifier())
        notification.attach(AppNotifier())
        #notification.notify(f"New message from {current_user.name}", user_id)
        #notification.notify(f"New message from {current_user.name} to user {user_id}")
        notification.notify({
            'notification_type': 'message',
            'user_id': user_id,
            'message': f"New message from {current_user.name}"
            })
        flash('Message sent.')
        return redirect(url_for('message.conversation', user_id=user_id, booking_id=booking_id))
    
    # Get conversation history
    messages = Message.get_conversation(current_user.id, user_id, booking.id if booking else None)
    
    # Mark received messages as read
    for msg in messages:
        if msg.receiver_id == current_user.id and not msg.is_read:
            msg.mark_as_read()
    
    return render_template('messages/conversation.html', 
                          other_user=other_user, 
                          messages=messages, 
                          booking=booking)

@message_bp.route('/messages/new', methods=['GET', 'POST'])
@login_required
def new_message():
    """
    Start a new conversation.
    """
    if request.method == 'POST':
        receiver_id = request.form.get('receiver_id')
        content = request.form.get('content')
        
        if not receiver_id or not content:
            flash('Please select a recipient and enter a message.')
            return redirect(url_for('message.new_message'))
        
        # Validate receiver
        receiver = User.query.get(receiver_id)
        if not receiver:
            flash('Invalid recipient.')
            return redirect(url_for('message.new_message'))
        
        # Use MessageComponent with Mediator pattern
        message_component = MessageComponent(ui_mediator)
        ui_mediator.register_component('message_component', message_component)
        
        # Send the message
        message = message_component.send_message(current_user.id, receiver_id, content)
        
        # Use Observer pattern to send notification
        notification = NotificationSubject()
        notification.attach(EmailNotifier())
        notification.attach(AppNotifier())
        #notification.notify(f"New message from {current_user.name}", receiver_id)
        notification.notify({
            'notification_type': 'message',
            'user_id': receiver_id,
            'message': f"New message from {current_user.name}"
            })
        flash('Message sent.')
        return redirect(url_for('message.conversation', user_id=receiver_id))
    
    # Get potential recipients (users with whom the current user has a booking relationship)
    # This query finds all users who are either:
    # 1. Owners of cars the current user has booked
    # 2. Renters who have booked the current user's cars
    
    # Get IDs of cars owned by the current user
    owned_car_ids = [car.id for car in current_user.cars]
    
    # Find renters who booked the current user's cars
    renter_ids = db.session.query(Booking.renter_id).filter(Booking.car_id.in_(owned_car_ids)).distinct().all()
    renter_ids = [r[0] for r in renter_ids]
    
    # Find owners of cars booked by the current user
    owner_ids = db.session.query(User.id).join(Car).join(Booking).filter(Booking.renter_id == current_user.id).distinct().all()
    #owner_ids = db.session.query(User.id).join(Booking).filter(Booking.renter_id == current_user.id).distinct().all()

    owner_ids = [o[0] for o in owner_ids]
    
    # Combine and remove duplicates
    user_ids = list(set(renter_ids + owner_ids))
    
    # Get the users
    users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
    
    return render_template('messages/new.html', users=users)

@message_bp.route('/messages/mark-read/<int:message_id>', methods=['POST'])
@login_required
def mark_read(message_id):
    """
    Mark a message as read.
    
    Args:
        message_id: The ID of the message to mark as read
    """
    message = Message.query.get_or_404(message_id)
    
    # Check if user is the receiver
    if message.receiver_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    message.mark_as_read()
    return jsonify({'success': True})

@message_bp.route('/messages/unread-count')
@login_required
def unread_count():
    """
    Get the count of unread messages.
    """
    count = Message.get_unread_count(current_user.id)
    return jsonify({'count': count})