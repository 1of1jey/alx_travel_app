from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Listing(models.Model):
    # Primary key
    listing_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic information
    title = models.CharField(max_length=200, help_text="Title of the listing")
    description = models.TextField(help_text="Detailed description of the listing")
    location = models.CharField(max_length=200, help_text="Location of the listing")
    price_per_night = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price per night in USD"
    )
    
    # Property details
    number_of_bedrooms = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of bedrooms"
    )
    number_of_bathrooms = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of bathrooms"
    )
    max_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of guests"
    )
    
    # Relationships
    host = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='listings',
        help_text="Host who owns this listing"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_available = models.BooleanField(default=True, help_text="Whether the listing is available for booking")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Listing"
        verbose_name_plural = "Listings"
    
    def __str__(self):
        return f"{self.title} - {self.location}"
    
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return 0.0


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    # Primary key
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        help_text="The listing being booked"
    )
    guest = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        help_text="The guest making the booking"
    )
    
    # Booking details
    check_in_date = models.DateField(help_text="Check-in date")
    check_out_date = models.DateField(help_text="Check-out date")
    number_of_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of guests for this booking"
    )
    
    # Pricing
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Total price for the booking"
    )
    
    # Status and timestamps
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        help_text="Current status of the booking"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields
    special_requests = models.TextField(
        blank=True, 
        null=True,
        help_text="Any special requests from the guest"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        # Ensure no overlapping bookings for the same listing
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out_date__gt=models.F('check_in_date')),
                name='check_out_after_check_in'
            )
        ]
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.listing.title}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.check_in_date and self.check_out_date:
            if self.check_out_date <= self.check_in_date:
                raise ValidationError("Check-out date must be after check-in date.")
        
        if self.number_of_guests and self.listing:
            if self.number_of_guests > self.listing.max_guests:
                raise ValidationError(
                    f"Number of guests ({self.number_of_guests}) exceeds maximum allowed ({self.listing.max_guests})."
                )
    
    def duration_nights(self):
        if self.check_in_date and self.check_out_date:
            return (self.check_out_date - self.check_in_date).days
        return 0


class Review(models.Model):
    # Primary key
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        help_text="The listing being reviewed"
    )
    reviewer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        help_text="The user who wrote the review"
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='review',
        null=True,
        blank=True,
        help_text="The booking associated with this review"
    )
    
    # Review content
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(help_text="Written review comment")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        # Ensure one review per user per listing
        unique_together = ['listing', 'reviewer']
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.listing.title} - {self.rating} stars"
