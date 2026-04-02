# Donor App - Getting Started

## Quick Start (5 minutes)

### 1. Apply Database Migrations
```bash
python manage.py makemigrations donor
python manage.py migrate
```

### 2. Create Test Donor
```bash
# Via API
curl -X POST http://localhost:8000/api/donors/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_donor",
    "email": "test@example.com",
    "password": "testpass123",
    "blood_type": "O+",
    "phone_number": "+1-555-0001",
    "location": "Test City",
    "date_of_birth": "1995-05-15"
  }'
```

### 3. Test Endpoints
```bash
# Get token
TOKEN=$(curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test_donor", "password": "testpass123"}' | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# Get available donors
curl -X GET "http://localhost:8000/api/donors/available/" \
  -H "Authorization: Token $TOKEN"
```

## Model at a Glance

```python
Donor Model:
├── user (OneToOne with User, related_name='donor_profile')
├── blood_type (8 choices: O+, O-, A+, A-, B+, B-, AB+, AB-)
├── phone_number (string)
├── location (string) # NEW: City/Region
├── date_of_birth (date)
├── is_available (boolean) # NEW: replaces is_active_donor
├── last_donation_date (datetime, optional)
├── wallet_address (string, optional) # NEW: for blockchain
├── created_at (auto)
└── updated_at (auto)
```

## 5 Main Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/donors/register/` | Register new donor |
| GET | `/api/donors/my_profile/` | Get my profile |
| PATCH | `/api/donors/{id}/update_availability/` | Toggle availability |
| GET | `/api/donors/available/` | List available donors |
| GET | `/api/donors/by_blood_type/` | Get by blood type |

## Key Changes from Previous Version

| Before | After |
|--------|-------|
| `is_active_donor` ❌ | `is_available` ✅ |
| `address, city, state, country, postal_code` ❌ | `location` ✅ |
| `total_donations` ❌ | (tracked via BloodDonation model) ✅ |
| `wallet_address` ❌ | `wallet_address` ✅ |
| `user.donor` ❌ | `user.donor_profile` ✅ |

## Documentation by Use Case

### "I want to understand the API"
→ Read: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

### "I'm migrating from the old schema"
→ Read: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

### "I need code examples"
→ Read: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### "I want the full technical overview"
→ Read: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

### "Tell me what changed"
→ Read: [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md)

## Python/Django Examples

### Register donor programmatically
```python
from django.contrib.auth.models import User
from donor.models import Donor

user = User.objects.create_user(
    username='donor1',
    email='donor@example.com',
    password='secure123'
)

donor = Donor.objects.create(
    user=user,
    blood_type='O+',
    phone_number='+1-555-0001',
    location='New York, NY',
    date_of_birth='1990-01-15',
    is_available=True
)
```

### Query available donors
```python
# All available
available = Donor.objects.filter(is_available=True)

# By blood type
o_plus = Donor.objects.filter(blood_type='O+', is_available=True)

# By location
ny_donors = Donor.objects.filter(
    location__icontains='New York',
    is_available=True
)

# Get count
count = Donor.objects.filter(is_available=True).count()
```

### Access from user
```python
# Get donor from user
donor = user.donor_profile

# Check if has profile
if hasattr(user, 'donor_profile'):
    print(user.donor_profile.blood_type)
```

## Admin Interface

1. Go to: http://localhost:8000/admin
2. Click "Donors"
3. Features:
   - ✅ Search by: First/Last name, Email, Phone, Location
   - ✅ Filter by: Blood Type, Availability, Location, Date Created
   - ✅ Edit all fields
   - ✅ Create new donors
   - ✅ Delete donors

## Testing with cURL

### Register
```bash
curl -X POST http://localhost:8000/api/donors/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newdonor",
    "email": "new@example.com",
    "password": "secure123",
    "blood_type": "A+",
    "phone_number": "+1-555-0002",
    "location": "Boston, MA",
    "date_of_birth": "1992-07-20"
  }'
```

### Get token
```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "newdonor", "password": "secure123"}'
```

### Get my profile
```bash
curl -X GET http://localhost:8000/api/donors/my_profile/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Get available donors
```bash
curl -X GET "http://localhost:8000/api/donors/available/?blood_type=O+" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Update availability
```bash
curl -X PATCH http://localhost:8000/api/donors/1/update_availability/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"is_available": false}'
```

## Troubleshooting

### "Donor profile not found"
```python
# Make sure user has donor created
try:
    donor = user.donor_profile
except Donor.DoesNotExist:
    # Create donor first
    donor = Donor.objects.create(
        user=user,
        blood_type='O+',
        phone_number='+1-555-0001',
        location='Test',
        date_of_birth='1990-01-01'
    )
```

### Migration conflicts
```bash
# Reset migrations (dev only)
python manage.py migrate donor zero
python manage.py migrate
```

### AttributeError: 'User' object has no attribute 'donor'
```python
# Old code: user.donor ❌
# New code: user.donor_profile ✅

# Check if related_name is set correctly in model
# Should be: related_name='donor_profile'
```

## File Structure

```
donor/
├── __init__.py
├── admin.py                    # Admin interface
├── apps.py                     # App config
├── models.py                   # Donor model ⭐
├── serializers.py              # DRF serializers ⭐
├── views.py                    # API ViewSet ⭐
├── urls.py                     # URL routing
├── tests.py                    # Tests
├── COMPLETION_SUMMARY.md       # What was done (this file)
├── API_DOCUMENTATION.md        # Full API docs
├── MIGRATION_GUIDE.md          # Database migration guide
├── QUICK_REFERENCE.md          # Code snippets & examples
├── IMPLEMENTATION_SUMMARY.md   # Technical details
└── Getting_Started.md          # This file
```

## Common Commands

```bash
# View database
python manage.py shell < donor/

# Create migrations
python manage.py makemigrations donor

# Apply migrations
python manage.py migrate donor

# Admin interface
python manage.py runserver
# Visit: http://localhost:8000/admin

# Run tests
python manage.py test donor

# Load test data
python manage.py loaddata donor_sample.json
```

## What's Next?

1. ✅ Run migrations
2. ✅ Test registration endpoint
3. ✅ Test filtering endpoints
4. ⏳ Write unit tests
5. ⏳ Update frontend
6. ⏳ Add more blood donation tracking
7. ⏳ Integrate wallet functionality

## Need Help?

1. **API questions** → [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. **Code examples** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. **Migration issues** → [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
4. **Technical details** → [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
5. **What changed** → [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md)

---

**Status:** ✅ Ready to use
**Last Updated:** 2024
**Version:** 2.0 (Refactored)
