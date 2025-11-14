from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
import random
from decimal import Decimal

from listings.models import Listing, Booking, Review


class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--listings',
            type=int,
            default=20,
            help='Number of listings to create (default: 20)'
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=50,
            help='Number of bookings to create (default: 50)'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=30,
            help='Number of reviews to create (default: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                if options['clear']:
                    self.stdout.write(
                        self.style.WARNING('Clearing existing data...')
                    )
                    self.clear_data()

                # Create users if they don't exist
                self.create_users()
                
                # Create listings
                self.create_listings(options['listings'])
                
                # Create bookings
                self.create_bookings(options['bookings'])
                
                # Create reviews
                self.create_reviews(options['reviews'])

                self.stdout.write(
                    self.style.SUCCESS('Successfully seeded the database!')
                )

        except Exception as e:
            raise CommandError(f'Error seeding database: {str(e)}')

    def clear_data(self):
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        # Don't delete users as they might be needed for other purposes
        self.stdout.write('Cleared existing listings, bookings, and reviews.')

    def create_users(self):
        users_data = [
            {'username': 'host1', 'email': 'host1@example.com', 'first_name': 'Jeffrey', 'last_name': 'Eshun'},
            {'username': 'host2', 'email': 'host2@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'username': 'host3', 'email': 'host3@example.com', 'first_name': 'Mike', 'last_name': 'Johnson'},
            {'username': 'host4', 'email': 'host4@example.com', 'first_name': 'Sarah', 'last_name': 'Wilson'},
            {'username': 'guest1', 'email': 'guest1@example.com', 'first_name': 'Alice', 'last_name': 'Brown'},
            {'username': 'guest2', 'email': 'guest2@example.com', 'first_name': 'Bob', 'last_name': 'Davis'},
            {'username': 'guest3', 'email': 'guest3@example.com', 'first_name': 'Carol', 'last_name': 'Garcia'},
            {'username': 'guest4', 'email': 'guest4@example.com', 'first_name': 'David', 'last_name': 'Miller'},
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password('password123')  # Set a default password
                user.save()
                self.stdout.write(f'Created user: {user.username}')

    def create_listings(self, count):
        
        # Sample data for listings
        titles = [
            "Cozy Downtown Apartment", "Luxury Beach Villa", "Mountain Cabin Retreat",
            "Historic City Loft", "Modern Studio Flat", "Charming Countryside Cottage",
            "Beachfront Condo", "Urban Penthouse", "Rustic Log Cabin", "Elegant Townhouse",
            "Seaside Bungalow", "Metropolitan High-Rise", "Peaceful Garden House",
            "Designer Apartment", "Vintage Victorian Home", "Contemporary Loft Space",
            "Tropical Paradise Villa", "Ski Chalet", "Riverside Retreat", "City Center Suite"
        ]
        
        locations = [
            "New York, NY", "Los Angeles, CA", "Miami, FL", "San Francisco, CA",
            "Austin, TX", "Seattle, WA", "Boston, MA", "Chicago, IL",
            "Denver, CO", "Nashville, TN", "Portland, OR", "San Diego, CA",
            "Las Vegas, NV", "Phoenix, AZ", "Atlanta, GA", "Washington, DC",
            "Honolulu, HI", "Charleston, SC", "Savannah, GA", "Key West, FL"
        ]
        
        descriptions = [
            "Perfect for couples or solo travelers looking for comfort and convenience.",
            "Spacious accommodation with modern amenities and stunning views.",
            "Quiet retreat away from the hustle and bustle of city life.",
            "Located in the heart of the city with easy access to attractions.",
            "Beautifully decorated space with all the comforts of home.",
            "Ideal for families or groups seeking a memorable vacation experience.",
            "Recently renovated with high-end furnishings and appliances.",
            "Enjoy breathtaking sunrises and sunsets from your private balcony.",
            "Experience local culture and cuisine within walking distance.",
            "Perfect blend of luxury and comfort in a prime location."
        ]
        
        hosts = list(User.objects.filter(username__startswith='host'))
        
        if not hosts:
            raise CommandError("No host users found. Please create host users first.")
        
        created_count = 0
        for i in range(count):
            try:
                listing = Listing.objects.create(
                    title=random.choice(titles),
                    description=random.choice(descriptions),
                    location=random.choice(locations),
                    price_per_night=Decimal(str(random.randint(50, 500))),
                    number_of_bedrooms=random.randint(1, 4),
                    number_of_bathrooms=random.randint(1, 3),
                    max_guests=random.randint(2, 8),
                    host=random.choice(hosts),
                    is_available=random.choice([True, True, True, False])
                )
                created_count += 1
                
                if created_count % 5 == 0:
                    self.stdout.write(f'Created {created_count} listings...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Failed to create listing: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} listings.')
        )

    def create_bookings(self, count):
        
        available_listings = list(Listing.objects.filter(is_available=True))
        guests = list(User.objects.filter(username__startswith='guest'))
        
        if not available_listings:
            self.stdout.write(
                self.style.WARNING('No available listings found. Skipping booking creation.')
            )
            return
        
        if not guests:
            self.stdout.write(
                self.style.WARNING('No guest users found. Skipping booking creation.')
            )
            return
        
        statuses = ['pending', 'confirmed', 'cancelled', 'completed']
        status_weights = [10, 60, 15, 15]  # 60% confirmed, 15% each for cancelled/completed, 10% pending
        
        created_count = 0
        for i in range(count):
            try:
                listing = random.choice(available_listings)
                guest = random.choice(guests)
                
                # Generate random dates
                start_date = date.today() + timedelta(days=random.randint(-90, 365))
                duration = random.randint(1, 14)  # 1-14 nights
                end_date = start_date + timedelta(days=duration)
                
                # Ensure guest count doesn't exceed listing capacity
                num_guests = random.randint(1, min(listing.max_guests, 6))
                
                # Calculate total price
                total_price = listing.price_per_night * duration
                
                booking = Booking.objects.create(
                    listing=listing,
                    guest=guest,
                    check_in_date=start_date,
                    check_out_date=end_date,
                    number_of_guests=num_guests,
                    total_price=total_price,
                    status=random.choices(statuses, weights=status_weights)[0],
                    special_requests=random.choice([
                        '', 'Late check-in please', 'Extra towels needed',
                        'Ground floor preferred', 'Quiet room please',
                        'Early check-in if possible'
                    ])
                )
                created_count += 1
                
                if created_count % 10 == 0:
                    self.stdout.write(f'Created {created_count} bookings...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Failed to create booking: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} bookings.')
        )

    def create_reviews(self, count):
        
        # Get completed bookings for realistic reviews
        completed_bookings = list(Booking.objects.filter(status='completed'))
        
        if not completed_bookings:
            self.stdout.write(
                self.style.WARNING('No completed bookings found. Creating reviews without booking association.')
            )
            # Fall back to creating reviews for any listing
            listings = list(Listing.objects.all())
            guests = list(User.objects.filter(username__startswith='guest'))
            
            if not listings or not guests:
                self.stdout.write(
                    self.style.WARNING('Insufficient data for creating reviews.')
                )
                return
        
        review_comments = [
            "Amazing place! Exactly as described and the host was very helpful.",
            "Great location and clean accommodations. Would definitely stay again.",
            "Perfect for our weekend getaway. Beautiful views and comfortable beds.",
            "Host was responsive and the place had everything we needed.",
            "Lovely property in a quiet neighborhood. Highly recommend!",
            "Good value for money. The amenities were as advertised.",
            "Wonderful experience! The place was spotless and well-equipped.",
            "Great communication from the host. Check-in was smooth and easy.",
            "Beautiful property with stunning views. Perfect for relaxation.",
            "Comfortable stay with all necessary amenities. Would book again.",
            "Nice place but could use some updates. Overall decent stay.",
            "Location was perfect for exploring the area. Clean and tidy.",
            "Exceeded expectations! The photos don't do it justice.",
            "Peaceful and quiet. Exactly what we were looking for.",
            "Good experience overall. Minor issues but nothing major."
        ]
        
        created_count = 0
        existing_reviews = set()
        
        for i in range(count):
            try:
                if completed_bookings:
                    # Create review based on completed booking
                    booking = random.choice(completed_bookings)
                    listing = booking.listing
                    reviewer = booking.guest
                    
                    # Check if review already exists for this listing-reviewer combination
                    review_key = (listing.listing_id, reviewer.id)
                    if review_key in existing_reviews:
                        continue
                    existing_reviews.add(review_key)
                    
                    # Create review
                    rating = random.choices(
                        [1, 2, 3, 4, 5],
                        weights=[2, 3, 10, 35, 50]  # Most reviews are 4-5 stars
                    )[0]
                    
                    review = Review.objects.create(
                        listing=listing,
                        reviewer=reviewer,
                        booking=booking,
                        rating=rating,
                        comment=random.choice(review_comments)
                    )
                    
                else:
                    # Create review without booking association
                    listing = random.choice(listings)
                    reviewer = random.choice(guests)
                    
                    # Check if review already exists
                    review_key = (listing.listing_id, reviewer.id)
                    if review_key in existing_reviews:
                        continue
                    existing_reviews.add(review_key)
                    
                    rating = random.choices(
                        [1, 2, 3, 4, 5],
                        weights=[2, 3, 10, 35, 50]
                    )[0]
                    
                    review = Review.objects.create(
                        listing=listing,
                        reviewer=reviewer,
                        rating=rating,
                        comment=random.choice(review_comments)
                    )
                
                created_count += 1
                
                if created_count % 5 == 0:
                    self.stdout.write(f'Created {created_count} reviews...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Failed to create review: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} reviews.')
        )

    def get_random_date_range(self, days_from_now_min=1, days_from_now_max=365):
        start_offset = random.randint(days_from_now_min, days_from_now_max)
        duration = random.randint(1, 14)
        
        start_date = date.today() + timedelta(days=start_offset)
        end_date = start_date + timedelta(days=duration)
        
        return start_date, end_date