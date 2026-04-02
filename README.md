# BloodChain - Blood Tracking & Blockchain Integration System

A comprehensive blood tracking and management system with Ethereum blockchain integration for transparency and donor incentives.

## Features

- **Donor Management**: Register and manage blood donors with blood type tracking
- **Hospital Management**: Hospital registration, verification, and blood inventory tracking
- **Blood Tracking**: Donation and blood transfer tracking with blockchain support
- **Notifications**: User notifications with preference management
- **Rewards System**: Points, badges, and reward redemption for donors

## Project Structure

```
BloodChain/
├── manage.py
├── bloodchain/                 # Project configuration
│   ├── settings.py            # Django settings (PostgreSQL, Redis configured)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── donor/                      # Donor management app
├── hospital/                   # Hospital management app
├── blood_tracking/             # Blood donation and transfer tracking app
├── notifications/              # Notification system app
├── rewards/                    # Rewards and gamification app
├── requirements.txt
├── .gitignore
├── .env.example               # Environment variables template
└── README.md
```

## Requirements

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- pip

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BloodChain
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and configure:
   - PostgreSQL database credentials
   - Redis URL
   - Django secret key
   - Web3 provider (if using blockchain)

5. **Create PostgreSQL database**
   ```bash
   createdb bloodchain_db
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

## API Endpoints

### Donors
- `GET /api/donors/` - List all donors
- `POST /api/donors/` - Create a new donor
- `GET /api/donors/{id}/` - Get donor details
- `GET /api/donors/my_profile/` - Get current user's donor profile
- `GET /api/donors/by_blood_type/?blood_type=O+` - Get donors by blood type

### Hospitals
- `GET /api/hospitals/` - List all hospitals
- `POST /api/hospitals/` - Create a new hospital
- `GET /api/hospitals/{id}/` - Get hospital details
- `GET /api/hospitals/{id}/blood_availability/` - Get blood availability
- `GET /api/blood-inventory/` - Get blood inventory
- `GET /api/blood-inventory/available_inventory/` - Get available inventory

### Blood Tracking
- `GET /api/donations/` - List all donations
- `POST /api/donations/` - Create a new donation
- `GET /api/donations/my_donations/` - Get current user's donations
- `GET /api/transfers/` - List all transfers
- `POST /api/transfers/` - Create a new transfer
- `GET /api/transfers/pending_transfers/` - Get pending transfers

### Notifications
- `GET /api/notifications/` - List user's notifications
- `GET /api/notifications/unread/` - Get unread notifications
- `POST /api/notifications/mark_all_as_read/` - Mark all as read
- `GET /api/notification-preferences/` - Get notification preferences

### Rewards
- `GET /api/badges/` - List all badges
- `GET /api/donor-badges/` - Get user's earned badges
- `GET /api/points/my_points/` - Get current user's points
- `GET /api/rewards/` - List all available rewards
- `POST /api/reward-redemptions/redeem_reward/` - Redeem a reward

## Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/`

## Testing

Run the test suite:
```bash
python manage.py test
```

With coverage:
```bash
coverage run --source='.' manage.py test
coverage report
```

## Environment Variables

See `.env.example` for all available configuration options:

- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - PostgreSQL settings
- `REDIS_URL` - Redis connection URL
- `DJANGO_SECRET_KEY` - Django secret key (change in production)
- `DJANGO_DEBUG` - Debug mode (set to False in production)
- `WEB3_PROVIDER_URI` - Blockchain provider URL (e.g., for Ethereum)
- `WEB3_CONTRACT_ADDRESS` - Smart contract address for blockchain integration

## Key Dependencies

- **Django 4.2** - Web framework
- **Django REST Framework** - RESTful API development
- **django-cors-headers** - CORS support
- **psycopg2** - PostgreSQL adapter
- **django-redis** - Redis caching backend
- **redis** - Redis client
- **web3** - Ethereum/blockchain interaction
- **celery** - Task queue for async processing

## Database Models

### Donor App
- `Donor` - Blood donor information with blood type and donation history

### Hospital App
- `Hospital` - Hospital registration and details
- `BloodInventory` - Hospital blood stock management

### Blood Tracking App
- `BloodDonation` - Donation records with blockchain tracking
- `BloodTransfer` - Blood transfer tracking between hospitals/patients

### Notifications App
- `Notification` - User notifications
- `NotificationPreference` - User notification preferences

### Rewards App
- `Badge` - Achievement badges
- `DonorBadge` - Earned badges per donor
- `Points` - Donor points balance
- `PointTransaction` - Point transaction history
- `Reward` - Redeemable rewards
- `RewardRedemption` - Reward redemption history

## Production Deployment

1. Set `DJANGO_DEBUG = False` in `.env`
2. Set a strong `DJANGO_SECRET_KEY`
3. Configure allowed hosts in `settings.py`
4. Use a production-grade WSGI server (Gunicorn, uWSGI)
5. Use PostgreSQL with proper backups
6. Use Redis with persistence enabled
7. Enable HTTPS
8. Configure proper logging and monitoring

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn bloodchain.wsgi:application --bind 0.0.0.0:8000
```

## Contributing

Contributions are welcome! Please follow the existing code style and include tests for new features.

## License

[Your License Here]

## Support

For issues or questions, please open an issue on GitHub.
