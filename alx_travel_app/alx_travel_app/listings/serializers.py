from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model."""
    
    host = UserSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'listing_id', 'title', 'description', 'location', 
            'price_per_night', 'number_of_bedrooms', 'number_of_bathrooms', 
            'max_guests', 'host', 'created_at', 'updated_at', 
            'is_available', 'average_rating', 'total_reviews'
        ]
        read_only_fields = ['listing_id', 'created_at', 'updated_at', 'host']
    
    def get_average_rating(self, obj):
        """Get the average rating for the listing."""
        return obj.average_rating()
    
    def get_total_reviews(self, obj):
        """Get the total number of reviews for the listing."""
        return obj.reviews.count()
    
    def validate(self, data):
        """Custom validation for listing data."""
        if data.get('price_per_night') and data['price_per_night'] <= 0:
            raise serializers.ValidationError("Price per night must be greater than 0.")
        
        if data.get('number_of_bedrooms') and data['number_of_bedrooms'] <= 0:
            raise serializers.ValidationError("Number of bedrooms must be at least 1.")
        
        if data.get('number_of_bathrooms') and data['number_of_bathrooms'] <= 0:
            raise serializers.ValidationError("Number of bathrooms must be at least 1.")
        
        if data.get('max_guests') and data['max_guests'] <= 0:
            raise serializers.ValidationError("Maximum guests must be at least 1.")
        
        return data


class ListingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating listings (without host field exposed)."""
    
    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'location', 'price_per_night', 
            'number_of_bedrooms', 'number_of_bathrooms', 'max_guests', 'is_available'
        ]
    
    def create(self, validated_data):
        """Create a new listing with the current user as host."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['host'] = request.user
        return super().create(validated_data)


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""
    
    listing = ListingSerializer(read_only=True)
    guest = UserSerializer(read_only=True)
    listing_id = serializers.UUIDField(write_only=True)
    duration_nights = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'listing', 'listing_id', 'guest', 'check_in_date', 
            'check_out_date', 'number_of_guests', 'total_price', 'status', 
            'created_at', 'updated_at', 'special_requests', 'duration_nights'
        ]
        read_only_fields = ['booking_id', 'created_at', 'updated_at', 'guest', 'total_price', 'status']
    
    def get_duration_nights(self, obj):
        """Get the number of nights for the booking."""
        return obj.duration_nights()
    
    def validate(self, data):
        """Custom validation for booking data."""
        from django.utils import timezone
        from datetime import date
        
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')
        listing_id = data.get('listing_id')
        number_of_guests = data.get('number_of_guests')
        
        # Validate dates
        if check_in_date and check_out_date:
            if check_out_date <= check_in_date:
                raise serializers.ValidationError("Check-out date must be after check-in date.")
            
            if check_in_date < date.today():
                raise serializers.ValidationError("Check-in date cannot be in the past.")
        
        # Validate listing exists and guest capacity
        if listing_id:
            try:
                listing = Listing.objects.get(listing_id=listing_id)
                data['listing'] = listing
                
                if not listing.is_available:
                    raise serializers.ValidationError("This listing is not available for booking.")
                
                if number_of_guests and number_of_guests > listing.max_guests:
                    raise serializers.ValidationError(
                        f"Number of guests ({number_of_guests}) exceeds maximum allowed ({listing.max_guests})."
                    )
                
                # Check for overlapping bookings
                if check_in_date and check_out_date:
                    overlapping_bookings = Booking.objects.filter(
                        listing=listing,
                        status__in=['confirmed', 'pending'],
                        check_in_date__lt=check_out_date,
                        check_out_date__gt=check_in_date
                    )
                    
                    # Exclude current booking if updating
                    if self.instance:
                        overlapping_bookings = overlapping_bookings.exclude(booking_id=self.instance.booking_id)
                    
                    if overlapping_bookings.exists():
                        raise serializers.ValidationError("These dates are not available. Please choose different dates.")
                
            except Listing.DoesNotExist:
                raise serializers.ValidationError("Invalid listing ID.")
        
        return data
    
    def create(self, validated_data):
        """Create a new booking with the current user as guest."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['guest'] = request.user
        
        # Calculate total price
        listing = validated_data['listing']
        check_in_date = validated_data['check_in_date']
        check_out_date = validated_data['check_out_date']
        nights = (check_out_date - check_in_date).days
        validated_data['total_price'] = listing.price_per_night * nights
        
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""
    
    listing = ListingSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    listing_id = serializers.UUIDField(write_only=True)
    booking_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Review
        fields = [
            'review_id', 'listing', 'listing_id', 'reviewer', 
            'booking_id', 'rating', 'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['review_id', 'created_at', 'updated_at', 'reviewer']
    
    def validate(self, data):
        """Custom validation for review data."""
        listing_id = data.get('listing_id')
        booking_id = data.get('booking_id')
        rating = data.get('rating')
        
        # Validate rating
        if rating and (rating < 1 or rating > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        
        # Validate listing exists
        if listing_id:
            try:
                listing = Listing.objects.get(listing_id=listing_id)
                data['listing'] = listing
            except Listing.DoesNotExist:
                raise serializers.ValidationError("Invalid listing ID.")
        
        # Validate booking exists and belongs to the reviewer
        if booking_id:
            try:
                request = self.context.get('request')
                booking = Booking.objects.get(booking_id=booking_id)
                
                if request and hasattr(request, 'user'):
                    if booking.guest != request.user:
                        raise serializers.ValidationError("You can only review bookings you made.")
                    
                    if booking.status != 'completed':
                        raise serializers.ValidationError("You can only review completed bookings.")
                
                data['booking'] = booking
            except Booking.DoesNotExist:
                raise serializers.ValidationError("Invalid booking ID.")
        
        return data
    
    def create(self, validated_data):
        """Create a new review with the current user as reviewer."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['reviewer'] = request.user
        return super().create(validated_data)


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating reviews."""
    
    listing_id = serializers.UUIDField()
    booking_id = serializers.UUIDField(required=False)
    
    class Meta:
        model = Review
        fields = ['listing_id', 'booking_id', 'rating', 'comment']
    
    def validate(self, data):
        """Use the same validation as ReviewSerializer."""
        return ReviewSerializer(context=self.context).validate(data)
    
    def create(self, validated_data):
        """Use the same creation logic as ReviewSerializer."""
        return ReviewSerializer(context=self.context).create(validated_data)