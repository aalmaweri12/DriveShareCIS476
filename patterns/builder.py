# Builder Pattern for Car Listing Creation

class CarListingBuilder:
    """
    Builder class for creating car listings step by step.
    """
    def __init__(self, owner_id):
        """
        Initialize the builder with owner ID.
        
        Args:
            owner_id: The ID of the car owner
        """
        # This import is placed here to avoid circular imports
        from models.car import Car
        
        self._car = Car(owner_id=owner_id)
    
    def set_model(self, model):
        """
        Set the car model.
        
        Args:
            model: The car model
            
        Returns:
            self for chaining
        """
        self._car.model = model
        return self
    
    def set_year(self, year):
        """
        Set the car year.
        
        Args:
            year: The car year
            
        Returns:
            self for chaining
        """
        self._car.year = year
        return self
    
    def set_mileage(self, mileage):
        """
        Set the car mileage.
        
        Args:
            mileage: The car mileage
            
        Returns:
            self for chaining
        """
        self._car.mileage = mileage
        return self
    
    def set_daily_price(self, price):
        """
        Set the daily rental price.
        
        Args:
            price: The daily rental price
            
        Returns:
            self for chaining
        """
        self._car.daily_price = price
        return self
    
    def set_location(self, location):
        """
        Set the car pickup location.
        
        Args:
            location: The car pickup location
            
        Returns:
            self for chaining
        """
        self._car.location = location
        return self
    
    def set_availability(self, start_date, end_date):
        """
        Set the car availability period.
        
        Args:
            start_date: The start date of availability
            end_date: The end date of availability
            
        Returns:
            self for chaining
        """
        self._car.availability_start = start_date
        self._car.availability_end = end_date
        return self
    
    def build(self):
        """
        Build and return the car listing.
        
        Returns:
            The completed Car object
        """
        return self._car

class CarListingDirector:
    """
    Director class that defines the order of building steps.
    """
    def __init__(self, builder):
        """
        Initialize the director with a builder.
        
        Args:
            builder: The CarListingBuilder instance
        """
        self._builder = builder
    
    def construct_economy_car(self, location, start_date, end_date):
        """
        Construct an economy car listing with default values.
        
        Args:
            location: The car pickup location
            start_date: The start date of availability
            end_date: The end date of availability
            
        Returns:
            The completed Car object
        """
        return (self._builder
                .set_model("Economy")
                .set_year(2015)
                .set_mileage(80000)
                .set_daily_price(35.00)
                .set_location(location)
                .set_availability(start_date, end_date)
                .build())
    
    def construct_luxury_car(self, location, start_date, end_date):
        """
        Construct a luxury car listing with default values.
        
        Args:
            location: The car pickup location
            start_date: The start date of availability
            end_date: The end date of availability
            
        Returns:
            The completed Car object
        """
        return (self._builder
                .set_model("Luxury")
                .set_year(2020)
                .set_mileage(30000)
                .set_daily_price(90.00)
                .set_location(location)
                .set_availability(start_date, end_date)
                .build())
    
    def construct_custom_car(self, model, year, mileage, daily_price, location, start_date, end_date):
        """
        Construct a custom car listing with specified values.
        
        Args:
            model: The car model
            year: The car year
            mileage: The car mileage
            daily_price: The daily rental price
            location: The car pickup location
            start_date: The start date of availability
            end_date: The end date of availability
            
        Returns:
            The completed Car object
        """
        return (self._builder
                .set_model(model)
                .set_year(year)
                .set_mileage(mileage)
                .set_daily_price(daily_price)
                .set_location(location)
                .set_availability(start_date, end_date)
                .build())