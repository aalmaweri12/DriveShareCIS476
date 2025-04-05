/**
 * DriveShare - Main JavaScript File
 * Simple functionality for the DriveShare application
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  
    // User menu dropdown toggle
    const userMenuToggle = document.querySelector('.user-menu-toggle');
    const userMenuDropdown = document.querySelector('.user-menu-dropdown');
    
    if (userMenuToggle && userMenuDropdown) {
      userMenuToggle.addEventListener('click', function() {
        userMenuDropdown.classList.toggle('active');
      });
      
      // Close dropdown when clicking outside
      document.addEventListener('click', function(event) {
        if (!userMenuToggle.contains(event.target) && !userMenuDropdown.contains(event.target)) {
          userMenuDropdown.classList.remove('active');
        }
      });
    }
    
    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.alert');
    if (flashMessages.length > 0) {
      flashMessages.forEach(message => {
        // Auto dismiss after 5 seconds
        setTimeout(() => {
          message.style.opacity = '0';
          setTimeout(() => {
            message.remove();
          }, 500);
        }, 5000);
        
        // Add close button functionality
        const closeBtn = message.querySelector('.close');
        if (closeBtn) {
          closeBtn.addEventListener('click', () => {
            message.remove();
          });
        }
      });
    }
    
    // Date input validation for bookings
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (startDateInput && endDateInput) {
      // Set minimum date to today
      const today = new Date();
      const todayFormatted = today.toISOString().split('T')[0];
      startDateInput.min = todayFormatted;
      
      // Update end date minimum when start date changes
      startDateInput.addEventListener('change', function() {
        endDateInput.min = this.value;
        
        // If end date is earlier than start date, update it
        if (endDateInput.value && endDateInput.value < this.value) {
          endDateInput.value = this.value;
        }
      });
    }
    
    // Car availability check
    const availabilityForm = document.getElementById('availability-form');
    const availabilityResult = document.getElementById('availability-result');
    
    if (availabilityForm && availabilityResult) {
      availabilityForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const carId = this.querySelector('[name="car_id"]').value;
        const startDate = this.querySelector('[name="start_date"]').value;
        const endDate = this.querySelector('[name="end_date"]').value;
        
        // Simple validation
        if (!startDate || !endDate) {
          availabilityResult.innerHTML = '<div class="alert alert-warning">Please select both start and end dates.</div>';
          return;
        }
        
        // Check availability via API
        fetch(`/bookings/api/check-availability?car_id=${carId}&start_date=${startDate}&end_date=${endDate}`)
          .then(response => response.json())
          .then(data => {
            if (data.available) {
              availabilityResult.innerHTML = '<div class="alert alert-success">This car is available for the selected dates!</div>';
            } else {
              availabilityResult.innerHTML = '<div class="alert alert-danger">Sorry, this car is not available for the selected dates.</div>';
            }
          })
          .catch(error => {
            availabilityResult.innerHTML = '<div class="alert alert-danger">Error checking availability. Please try again.</div>';
            console.error('Error:', error);
          });
      });
    }
    
    // Payment button confirmation
    const paymentButton = document.getElementById('payment-button');
    
    if (paymentButton) {
      paymentButton.addEventListener('click', function(e) {
        if (!confirm('Are you sure you want to proceed with this payment?')) {
          e.preventDefault();
        }
      });
    }
    
    // Simple form validation
    const forms = document.querySelectorAll('form.needs-validation');
    
    forms.forEach(form => {
      form.addEventListener('submit', function(e) {
        if (!form.checkValidity()) {
          e.preventDefault();
          e.stopPropagation();
        }
        
        form.classList.add('was-validated');
      });
    });
  });