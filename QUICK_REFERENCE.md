# BloodChain Quick Reference

Quick reference guide for common commands, endpoints, and workflows.

---

## Table of Contents

- [Setup Commands](#setup-commands)
- [Development Commands](#development-commands)
- [API Endpoints](#api-endpoints)
- [Common Workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)

---

## Setup Commands

### Initial Setup

```bash
# Clone repository
git clone https://github.com/yourorg/bloodchain.git
cd bloodchain

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Setup database
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Environment Variables

```bash
# .env file essentials
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
WEB3_PROVIDER_URI=https://sepolia.infura.io/v3/YOUR_KEY
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Development Commands

### Database

```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush

# View SQL for migrations
python manage.py sqlmigrate blood_tracking 0001
```

### Django Shell

```bash
# Open Django shell
python manage.py shell

# Create objects
from donor.models import Donor
donor = Donor.objects.create(name="John", blood_type="O+")

# Query objects
Donor.objects.all()
Donor.objects.filter(blood_type="O+")

# Update objects
donor.name = "Jane"
donor.save()

# Delete objects
donor.delete()
```

### Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test blood_tracking

# Run specific test class
python manage.py test blood_tracking.tests.BloodUnitTest

# Verbose output
python manage.py test --verbosity=2

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Admin Panel

```bash
# Create superuser
python manage.py createsuperuser

# Access admin
http://localhost:8000/admin
```

---

## API Endpoints

### Authentication

```bash
# Get token
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# Use token in requests
curl -X GET http://localhost:8000/api/blood-tracking/units/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Blood Unit Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/blood-tracking/units/register/` | Register new unit |
| GET | `/api/blood-tracking/units/` | List all units |
| GET | `/api/blood-tracking/units/{id}/` | Get unit details |
| PATCH | `/api/blood-tracking/units/{id}/update_blockchain_status/` | Update status |
| GET | `/api/blood-tracking/units/{id}/blockchain_history/` | Get blockchain history |
| GET | `/api/blood-tracking/units/lifecycle_history/?unit_id=UUID` | Get lifecycle |

### Donor Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/donors/` | Create donor |
| GET | `/api/donors/` | List donors |
| GET | `/api/donors/{id}/` | Get donor details |
| PATCH | `/api/donors/{id}/` | Update donor |
| DELETE | `/api/donors/{id}/` | Delete donor |

### Hospital Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/hospitals/` | Create hospital |
| GET | `/api/hospitals/` | List hospitals |
| GET | `/api/hospitals/{id}/` | Get hospital details |
| PATCH | `/api/hospitals/{id}/` | Update hospital |
| DELETE | `/api/hospitals/{id}/` | Delete hospital |

---

## Common Workflows

### Workflow 1: Create and Track Blood Unit

```bash
# 1. Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}' | jq -r '.token')

# 2. Create blood unit
RESPONSE=$(curl -s -X POST http://localhost:8000/api/blood-tracking/units/register/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "donor": 1,
    "blood_type": "O+",
    "collected_at": "2026-04-02T10:30:00Z",
    "expiry_date": "2026-05-02T10:30:00Z"
  }')

UNIT_ID=$(echo $RESPONSE | jq -r '.id')

# 3. Get unit details
curl -s -X GET http://localhost:8000/api/blood-tracking/units/$UNIT_ID/ \
  -H "Authorization: Token $TOKEN" | jq .

# 4. Update status
curl -s -X PATCH http://localhost:8000/api/blood-tracking/units/$UNIT_ID/update_blockchain_status/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "testing", "notes": "Lab testing"}' | jq .

# 5. Get blockchain history
curl -s -X GET http://localhost:8000/api/blood-tracking/units/$UNIT_ID/blockchain_history/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### Workflow 2: Query Available Blood Units

```bash
# List all O+ blood units in storage
curl -X GET "http://localhost:8000/api/blood-tracking/units/?blood_type=O%2B&status=storage" \
  -H "Authorization: Token $TOKEN" | jq .

# Get units by blood type
curl -X GET "http://localhost:8000/api/blood-tracking/units/by_blood_type/?blood_type=O%2B" \
  -H "Authorization: Token $TOKEN" | jq .

# Get units expiring soon
curl -X GET http://localhost:8000/api/blood-tracking/units/near_expiry/ \
  -H "Authorization: Token $TOKEN" | jq .

# Get units at specific location
curl -X GET "http://localhost:8000/api/blood-tracking/units/units_at_location/?location_id=1" \
  -H "Authorization: Token $TOKEN" | jq .
```

### Workflow 3: Manage Donors

```bash
# Create donor
curl -X POST http://localhost:8000/api/donors/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "blood_type": "O+",
    "phone": "+1234567890"
  }' | jq .

# List donors
curl -X GET http://localhost:8000/api/donors/ \
  -H "Authorization: Token $TOKEN" | jq .

# Search donors
curl -X GET "http://localhost:8000/api/donors/?search=John" \
  -H "Authorization: Token $TOKEN" | jq .

# Update donor
curl -X PATCH http://localhost:8000/api/donors/1/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}' | jq .
```

---

## Troubleshooting

### Database Issues

```bash
# Check database connection
python manage.py dbshell

# Show database migrations status
python manage.py showmigrations

# Create missing migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Clear database (development only)
python manage.py flush
```

### Blockchain Issues

```bash
# Test blockchain connection (Django shell)
python manage.py shell

# In shell:
from blood_tracking.blockchain_service import get_blockchain_service
service = get_blockchain_service()
print(service.is_connected)
print(service.web3.eth.get_block('latest'))
```

### Authentication Issues

```bash
# Create new token
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Reset user password (Django shell)
python manage.py shell

# In shell:
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
user.set_password('newpassword')
user.save()
```

### Port Already in Use

```bash
# Use different port
python manage.py runserver 8001

# Kill process on port 8000 (macOS/Linux)
lsof -ti:8000 | xargs kill -9

# Kill process on port 8000 (Windows PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

### ModuleNotFoundError

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate   # Windows PowerShell

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | GET request successful |
| 201 | Created | POST resource created |
| 204 | No Content | DELETE successful |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Server error |

---

## Blood Unit Statuses

| Status | Description |
|--------|-------------|
| `collected` | Initial collection |
| `testing` | Lab testing in progress |
| `storage` | In cold storage |
| `transfused` | Transfused to patient |
| `expired` | Past expiry date |

---

## Blood Type Compatibility

**O- (Universal Donor):** Can give to all
**O+:** Can give to O+, A+, B+, AB+
**A-:** Can give to A-, A+, AB-, AB+
**A+:** Can give to A+, AB+
**B-:** Can give to B-, B+, AB-, AB+
**B+:** Can give to B+, AB+
**AB-:** Can give to AB-, AB+
**AB+ (Universal Recipient):** Can receive from all

---

## Useful Links

- **Admin Panel:** http://localhost:8000/admin
- **API:** http://localhost:8000/api
- **Swagger Docs:** http://localhost:8000/api/schema/ (if installed)
- **Sepolia Etherscan:** https://sepolia.etherscan.io
- **Infura Dashboard:** https://infura.io/dashboard

---

## Environment Setup Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`requirements.txt`)
- [ ] `.env` file configured
- [ ] Database migrations applied
- [ ] Superuser created
- [ ] Development server running
- [ ] Authentication token obtained
- [ ] First API call successful
- [ ] Blockchain connection tested

---

## Performance Tips

```bash
# Use Django debug toolbar
pip install django-debug-toolbar

# Profile code execution
pip install django-extensions
python manage.py shell_plus

# Monitor database queries
LOGGING['loggers']['django.db.backends']

# Cache database queries
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

---

## Useful Commands

```bash
# List all URLs
python manage.py show_urls

# Check project health
python manage.py check

# Get Django version
python -c "import django; print(django.get_version())"

# Generate requirements.txt
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# View loaded apps
python manage.py shell -c "from django.apps import apps; print([app.name for app in apps.get_app_configs()])"
```

---

**Last Updated:** 2026-04-02

See full documentation in [SETUP_GUIDE.md](SETUP_GUIDE.md), [API_DOCUMENTATION.md](blood_tracking/API_DOCUMENTATION.md), [BLOCKCHAIN_INTEGRATION.md](blood_tracking/BLOCKCHAIN_INTEGRATION.md)
