# routes/car.py
# Routes for car listing management (create, view, update, delete)

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from datetime import datetime

from app import db
from models import Car
from patterns.builder import CarListingBuilder, CarListingDirector
from patterns.mediator import UIMediator, SearchComponent

# Create Blueprint
car_bp = Blueprint('car', __name__)

# Create UI mediator for component communication
ui_mediator = UIMediator()

@car_bp.route('/cars')
def list_cars():
    """
    Display all available cars or search results.
    """
    # Get search parameters
    location = request.args.get('location', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    
    # Initialize search component with mediator
    search_component = SearchComponent(ui_mediator)
    ui_mediator.register_component('search_component', search_component)
    
    # Prepare search criteria
    criteria = {'location': location}
    
    # Convert dates if provided
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            criteria['start_date'] = start_date
            criteria['end_date'] = end_date
        except ValueError:
            flash('Invalid date format.')
    
    # Search for cars using the search component
    search_component.search(criteria)
    
    # Get the results from the database (in a real app, this would be handled by the mediator)
    if 'start_date' in criteria and 'end_date' in criteria:
        cars = Car.search_available_cars(location, criteria['start_date'], criteria['end_date'])
    else:
        cars = Car.search_available_cars(location)
    
    return render_template(
        'cars/list.html',
        cars=cars,
        location=location,
        start_date=start_date_str,
        end_date=end_date_str
    )

@car_bp.route('/my-cars')
@login_required
def my_cars():
    """
    Display the current user's car listings.
    """
    cars = Car.query.filter_by(owner_id=current_user.id).all()
    return render_template('cars/my_cars.html', cars=cars)

@car_bp.route('/cars/<int:car_id>')
def view_car(car_id):
    """
    Display details for a specific car.
    
    Args:
        car_id: The ID of the car to view
    """
    car = Car.query.get_or_404(car_id)
    is_owner = current_user.is_authenticated and car.owner_id == current_user.id
    return render_template('cars/detail.html', car=car, is_owner=is_owner)

@car_bp.route('/cars/create', methods=['GET', 'POST'])
@login_required
def create_car():
    """
    Create a new car listing.
    """
    if request.method == 'POST':
        # Get form data
        model = request.form.get('model')
        year = request.form.get('year')
        mileage = request.form.get('mileage')
        daily_price = request.form.get('daily_price')
        location = request.form.get('location')
        availability_start_str = request.form.get('availability_start')
        availability_end_str = request.form.get('availability_end')
        
        # Validate form data
        if not model or not year or not mileage or not daily_price or not location or not availability_start_str or not availability_end_str:
            flash('Please fill in all required fields.')
            return redirect(url_for('car.create_car'))
        
        try:
            # Convert strings to numbers
            year = int(year)
            mileage = float(mileage)
            daily_price = float(daily_price)
            
            # Convert dates
            availability_start = datetime.strptime(availability_start_str, '%Y-%m-%d').date()
            availability_end = datetime.strptime(availability_end_str, '%Y-%m-%d').date()
            
            if availability_start > availability_end:
                flash('Start date cannot be after end date.')
                return redirect(url_for('car.create_car'))
                
        except ValueError:
            flash('Invalid input format.')
            return redirect(url_for('car.create_car'))
        
        # Use Builder pattern to create the car listing
        builder = CarListingBuilder(current_user.id)
        director = CarListingDirector(builder)
        
        car = director.construct_custom_car(
            model=model,
            year=year,
            mileage=mileage,
            daily_price=daily_price,
            location=location,
            start_date=availability_start,
            end_date=availability_end
        )
        
        # Save to database
        db.session.add(car)
        db.session.commit()
        
        flash('Car listing created successfully!')
        return redirect(url_for('car.my_cars'))
    
    return render_template('cars/create.html')

@car_bp.route('/cars/<int:car_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    """
    Edit an existing car listing.
    
    Args:
        car_id: The ID of the car to edit
    """
    car = Car.query.get_or_404(car_id)
    
    # Check if user is the owner
    if car.owner_id != current_user.id:
        flash('You are not authorized to edit this car listing.')
        return redirect(url_for('car.view_car', car_id=car_id))
    
    if request.method == 'POST':
        # Get form data
        model = request.form.get('model')
        year = request.form.get('year')
        mileage = request.form.get('mileage')
        daily_price = request.form.get('daily_price')
        location = request.form.get('location')
        availability_start_str = request.form.get('availability_start')
        availability_end_str = request.form.get('availability_end')
        
        # Validate form data
        if not model or not year or not mileage or not daily_price or not location or not availability_start_str or not availability_end_str:
            flash('Please fill in all required fields.')
            return redirect(url_for('car.edit_car', car_id=car_id))
        
        try:
            # Convert strings to numbers
            year = int(year)
            mileage = float(mileage)
            daily_price = float(daily_price)
            
            # Convert dates
            availability_start = datetime.strptime(availability_start_str, '%Y-%m-%d').date()
            availability_end = datetime.strptime(availability_end_str, '%Y-%m-%d').date()
            
            if availability_start > availability_end:
                flash('Start date cannot be after end date.')
                return redirect(url_for('car.edit_car', car_id=car_id))
                
        except ValueError:
            flash('Invalid input format.')
            return redirect(url_for('car.edit_car', car_id=car_id))
        
        # Update car details
        car.update_details(
            model=model,
            year=year,
            mileage=mileage,
            daily_price=daily_price,
            location=location,
            availability_start=availability_start,
            availability_end=availability_end
        )
        
        flash('Car listing updated successfully!')
        return redirect(url_for('car.view_car', car_id=car_id))
    
    return render_template('cars/edit.html', car=car)

@car_bp.route('/cars/<int:car_id>/delete', methods=['POST'])
@login_required
def delete_car(car_id):
    """
    Delete a car listing.
    
    Args:
        car_id: The ID of the car to delete
    """
    car = Car.query.get_or_404(car_id)
    
    # Check if user is the owner
    if car.owner_id != current_user.id:
        flash('You are not authorized to delete this car listing.')
        return redirect(url_for('car.view_car', car_id=car_id))
    
    # Check if car has active bookings
    active_bookings = [b for b in car.bookings if b.status in ['pending', 'confirmed']]
    
    if active_bookings:
        flash('Cannot delete a car with active bookings.')
        return redirect(url_for('car.view_car', car_id=car_id))
    
    # Delete the car
    db.session.delete(car)
    db.session.commit()
    
    flash('Car listing deleted successfully!')
    return redirect(url_for('car.my_cars'))

@car_bp.route('/cars/quick-create', methods=['GET', 'POST'])
@login_required
def quick_create_car():
    """
    Quickly create a car listing using predefined templates.
    """
    if request.method == 'POST':
        # Get form data
        car_type = request.form.get('car_type')
        location = request.form.get('location')
        availability_start_str = request.form.get('availability_start')
        availability_end_str = request.form.get('availability_end')
        
        # Validate form data
        if not car_type or not location or not availability_start_str or not availability_end_str:
            flash('Please fill in all required fields.')
            return redirect(url_for('car.quick_create_car'))
        
        try:
            # Convert dates
            availability_start = datetime.strptime(availability_start_str, '%Y-%m-%d').date()
            availability_end = datetime.strptime(availability_end_str, '%Y-%m-%d').date()
            
            if availability_start > availability_end:
                flash('Start date cannot be after end date.')
                return redirect(url_for('car.quick_create_car'))
                
        except ValueError:
            flash('Invalid date format.')
            return redirect(url_for('car.quick_create_car'))
        
        # Use Builder pattern with Director to create the car listing
        builder = CarListingBuilder(current_user.id)
        director = CarListingDirector(builder)
        
        if car_type == 'economy':
            car = director.construct_economy_car(
                location=location,
                start_date=availability_start,
                end_date=availability_end
            )
        elif car_type == 'luxury':
            car = director.construct_luxury_car(
                location=location,
                start_date=availability_start,
                end_date=availability_end
            )
        else:
            flash('Invalid car type.')
            return redirect(url_for('car.quick_create_car'))
        
        # Save to database
        db.session.add(car)
        db.session.commit()
        
        flash('Car listing created successfully!')
        return redirect(url_for('car.my_cars'))
    
    return render_template('cars/quick_create.html')