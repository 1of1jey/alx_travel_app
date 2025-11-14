# ALX Travel App

A Django REST API application for managing travel listings, bookings, and reviews. This application allows users to create property listings, make bookings, and leave reviews for accommodations.

## Features

- **Property Listings**: Create and manage travel property listings with detailed information
- **Booking System**: Handle bookings with date validation and availability checking
- **Review System**: Allow guests to leave ratings and comments for properties
- **RESTful API**: Comprehensive API with Django REST Framework
- **Database Seeding**: Management command to populate the database with sample data

## Models

### Listing

- **Fields**: title, description, location, price_per_night, bedrooms, bathrooms, max_guests, host, availability status
- **Relationships**: Belongs to a host (User), has many bookings and reviews
- **Features**: UUID primary key, automatic timestamps, average rating calculation

### Booking

- **Fields**: check-in/out dates, number of guests, total price, status, special requests
- **Relationships**: Belongs to a listing and guest (User)
- **Features**: UUID primary key, date validation, overlapping booking prevention, status tracking

### Review

- **Fields**: rating (1-5), comment, timestamps
- **Relationships**: Belongs to a listing, reviewer (User), and optionally a booking
- **Features**: UUID primary key, unique constraint per user per listing

## API Endpoints

The application provides RESTful API endpoints for:

- Listing management (CRUD operations)
- Booking management with validation
- Review system with rating calculations
- User authentication and management

## Project Structure

```
alx_travel_app/
├── manage.py
├── alx_travel_app/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── listings/
│       ├── models.py          # Database models
│       ├── serializers.py     # API serializers
│       ├── views.py           # API views
│       ├── urls.py           # URL routing
│       ├── admin.py          # Django admin config
│       └── management/
│           └── commands/
│               └── seed.py    # Database seeding command
└── travel/                    # Virtual environment
```

## Installation and Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment support

### 1. Clone the Repository

```bash
git clone https://github.com/1of1jey/alx_travel_app_0x00.git
cd alx_travel_app_0x00/alx_travel_app
```

### 2. Activate Virtual Environment

```bash
# On Windows
../travel/Scripts/activate

# On macOS/Linux
source ../travel/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r alx_travel_app/requirement.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (Optional - defaults to SQLite)
DB_ENGINE=django.db.backends.sqlite3
# For MySQL (uncomment and configure):
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=alx_travel_db
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=3306
```

### 5. Database Setup

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser
```

### 6. Seed the Database

```bash
# Run the seed command to populate with sample data
python manage.py seed

# Options:
python manage.py seed --listings 30 --bookings 60 --reviews 40
python manage.py seed --clear  # Clear existing data first
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Database Seeding

The application includes a management command to populate the database with sample data:

### Command Usage

```bash
python manage.py seed [options]
```

### Available Options

- `--listings N`: Number of listings to create (default: 20)
- `--bookings N`: Number of bookings to create (default: 50)
- `--reviews N`: Number of reviews to create (default: 30)
- `--clear`: Clear existing data before seeding

### What the Seeder Creates

1. **Sample Users**: Creates host and guest users with default passwords
2. **Property Listings**: Various types of accommodations with realistic data
3. **Bookings**: Bookings with different statuses and date ranges
4. **Reviews**: Ratings and comments for completed bookings

### Example Usage

```bash
# Basic seeding
python manage.py seed

# Custom quantities
python manage.py seed --listings 50 --bookings 100 --reviews 75

# Clear existing data and reseed
python manage.py seed --clear --listings 25
```

## API Documentation

### Authentication

The API uses Django's built-in authentication system. Users need to be authenticated to create bookings and reviews.

### Serializers

- **ListingSerializer**: Full listing data with host information and ratings
- **ListingCreateSerializer**: Simplified serializer for creating listings
- **BookingSerializer**: Complete booking data with validation
- **BookingCreateSerializer**: Simplified booking creation
- **ReviewSerializer**: Review data with listing and reviewer information
- **ReviewCreateSerializer**: Simplified review creation

### Key Features

- **Validation**: Comprehensive validation for dates, capacity, and business rules
- **Relationships**: Proper handling of foreign key relationships
- **Error Handling**: Detailed error messages for validation failures
- **Permissions**: User-based permissions for creating and modifying data

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Django Admin

Access the admin interface at `http://127.0.0.1:8000/admin/` using your superuser credentials.

## Dependencies

Key packages used in this project:

- **Django 5.2.7**: Web framework
- **Django REST Framework**: API development
- **django-cors-headers**: CORS handling
- **drf-yasg**: API documentation
- **django-environ**: Environment variable management
- **PyMySQL**: MySQL database connector (optional)

## Database Configuration

The application supports both SQLite (default) and MySQL databases:

### SQLite (Default)

No additional configuration needed. The database file will be created automatically.

### MySQL

1. Install MySQL server
2. Create a database for the application
3. Update the `.env` file with MySQL credentials
4. Ensure PyMySQL is installed: `pip install pymysql`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **Migration Errors**: Run `python manage.py makemigrations` before `migrate`
2. **Permission Errors**: Ensure the virtual environment is activated
3. **Database Connection**: Check database credentials in `.env` file
4. **Port Already in Use**: Use `python manage.py runserver 8001` for different port

### Seed Command Issues

- Ensure migrations are applied before running seed command
- Use `--clear` flag to reset data if needed
- Check that required packages are installed

## License

This project is developed as part of the ALX Software Engineering program.

## Contact

For questions or support, please refer to the project documentation or create an issue in the repository.
