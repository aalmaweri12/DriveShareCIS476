# DriveShareCIS476
# DriveShare - Peer-to-Peer Car Rental Platform

DriveShare is a web-based platform that connects car owners with individuals seeking short-term car rentals. The platform facilitates listing, searching, booking, and payment processing for personal vehicle rentals.

## Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Screenshots](#screenshots)
- [Contributors](#contributors)

## Features

### User Authentication and Management
- User registration with email and password
- Three security questions for account recovery
- Secure login/logout functionality
- Password recovery using Chain of Responsibility pattern

### Car Listing and Management
- List personal vehicles with details (model, year, mileage, etc.)
- Set availability calendar and rental pricing
- Edit and delete car listings
- Quick listing creation with predefined templates

### Search and Booking
- Search for available cars by location and date
- Filter search results
- Book cars for specific periods
- Prevents double-booking through availability validation

### Messaging System
- Direct communication between car owners and renters
- Conversation history
- Booking-related messaging

### Payment Processing
- Simulated payment system
- Payment history tracking
- Refund processing

### Notifications
- Booking request notifications
- Booking status updates
- Payment confirmations
- In-app and email notifications

## Technology Stack

- **Backend**: Python with Flask framework
- **Database**: SQLAlchemy ORM with SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login
- **Email**: SMTP for email notifications

## Design Patterns

The project implements several design patterns to ensure clean and maintainable code:

### Singleton Pattern
- `UserSession` class for managing user sessions securely

### Observer Pattern
- `NotificationSubject`, `EmailNotifier`, and `AppNotifier` classes for notifications
- `BookingManager` for booking status updates

### Mediator Pattern
- `UIMediator` class for managing communication between UI components
- `SearchComponent`, `BookingComponent`, and `MessageComponent` classes

### Builder Pattern
- `CarListingBuilder` and `CarListingDirector` for flexible car listing creation

### Proxy Pattern
- `PaymentProxy` for secure payment processing

### Chain of Responsibility Pattern
- Security question validation for password recovery
- `QuestionOneHandler`, `QuestionTwoHandler`, `QuestionThreeHandler`, and `PasswordResetHandler` classes

## Project Structure

```
driveshare/
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── database.py            # Database initialization
├── models/                # Database models
│   ├── __init__.py
│   ├── booking.py
│   ├── car.py
│   ├── message.py
│   ├── payment.py
│   ├── payment_method.py
│   └── user.py
├── patterns/              # Design pattern implementations
│   ├── __init__.py
│   ├── builder.py
│   ├── chain.py
│   ├── mediator.py
│   ├── observer.py
│   ├── proxy.py
│   └── singleton.py
├── routes/                # Route handlers
│   ├── __init__.py
│   ├── auth.py
│   ├── booking.py
│   ├── car.py
│   ├── message.py
│   └── payment.py
├── static/                # Static assets
│   ├── css/
│   └── js/
└── templates/             # HTML templates
    ├── auth/
    ├── bookings/
    ├── cars/
    ├── errors/
    ├── messages/
    ├── payments/
    └── layout.html
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/driveshare.git
   cd driveshare
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional):
   ```bash
   export FLASK_ENV=development
   export SECRET_KEY=your_secret_key
   export EMAIL_HOST=your_email_host
   export EMAIL_PORT=your_email_port
   export EMAIL_USER=your_email_user
   export EMAIL_PASSWORD=your_email_password
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

## Configuration

Configuration settings can be found in `config.py`:

- Development, testing, and production configurations
- Database connection settings
- Email settings for notifications
- Secret key for session security

You can override these settings using environment variables.

## Usage

1. Start the application:
   ```bash
   python app.py
   ```
   or
   ```bash
   flask run
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. Register an account to start using the platform as either a car owner or renter.

### For Car Owners:
- Click on "List Your Car" to create a new listing
- Set availability and pricing
- Manage booking requests
- Communicate with renters

### For Renters:
- Search for available cars
- Make booking requests
- Make payments
- Communicate with car owners

## Database Schema

The application uses the following main models:

- **User**: Stores user account information and security questions
- **Car**: Stores car listing details and availability
- **Booking**: Manages the rental booking process
- **Message**: Handles communication between users
- **Payment**: Tracks payment transactions
- **PaymentMethod**: Stores saved payment methods

## API Endpoints

The application provides the following API endpoints:

- `/api/check-availability`: Check if a car is available for specific dates
- `/api/payment-status/<booking_id>`: Get the payment status for a booking

## Screenshots

the screenshots are in the report.docx

## Contributors

- Abdulmajeed Almaweri (https://github.com/aalmaweri12/DriveShareCIS476)

## License

This project is licensed under the MIT License - see the LICENSE file for details.