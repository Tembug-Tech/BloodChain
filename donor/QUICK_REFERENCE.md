# Donor App Quick Reference

## Model

```python
from donor.models import Donor

# Create a donor (user must exist first)
donor = Donor.objects.create(
    user=user,
    blood_type='O+',
    phone_number='+1-555-0123',
    location='New York, NY',
    date_of_birth='1990-01-15',
    is_available=True,
    wallet_address='0x742d35Cc6634C0532925a3b844Bc9e7595f42bE'
)

# Access donor from user
donor = user.donor_profile

# blood types
'O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'

# Query examples
available_donors = Donor.objects.filter(is_available=True)
o_positive = Donor.objects.filter(blood_type='O+', is_available=True)
ny_donors = Donor.objects.filter(location__icontains='New York', is_available=True)
```

## Serializers

```python
from donor.serializers import DonorSerializer, DonorRegistrationSerializer

# Serialize donor profile
donor = Donor.objects.get(id=1)
serializer = DonorSerializer(donor)
data = serializer.data

# Deserialize for updates
data = {'is_available': False}
serializer = DonorSerializer(donor, data=data, partial=True)
if serializer.is_valid():
    serializer.save()

# Registration
reg_data = {
    'username': 'newdonor',
    'email': 'donor@example.com',
    'password': 'secure123',
    'blood_type': 'O+',
    'phone_number': '+1-555-0123',
    'location': 'Boston, MA',
    'date_of_birth': '1992-07-22'
}
serializer = DonorRegistrationSerializer(data=reg_data)
if serializer.is_valid():
    donor = serializer.save()
```

## API Endpoints Quick Guide

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | `/api/donors/register/` | Register new donor | No |
| GET | `/api/donors/` | List all donors | Yes |
| GET | `/api/donors/{id}/` | Get specific donor | Yes |
| PATCH | `/api/donors/{id}/` | Update donor | Yes |
| DELETE | `/api/donors/{id}/` | Delete donor | Yes |
| GET | `/api/donors/my_profile/` | Get my profile | Yes |
| PATCH | `/api/donors/{id}/update_availability/` | Toggle availability | Yes |
| GET | `/api/donors/available/` | List available donors | Yes |
| GET | `/api/donors/by_blood_type/` | Get by blood type | Yes |

## Common Code Snippets

### Get donor for authenticated user
```python
# In a view
donor = request.user.donor_profile

# With error handling
try:
    donor = request.user.donor_profile
except Donor.DoesNotExist:
    return Response({'error': 'No donor profile'}, status=404)
```

### Get available donors with filters
```python
# All available donors
donors = Donor.objects.filter(is_available=True)

# By blood type
donors = Donor.objects.filter(blood_type='O+', is_available=True)

# By location
donors = Donor.objects.filter(
    location__icontains='New York',
    is_available=True
)

# Combined
donors = Donor.objects.filter(
    blood_type='A+',
    location__icontains='California',
    is_available=True
)
```

### Check if user has donor profile
```python
has_profile = hasattr(request.user, 'donor_profile')
```

### Create donor from command line
```bash
# Python shell
python manage.py shell

# Inside shell
from django.contrib.auth.models import User
from donor.models import Donor
from datetime import date

user = User.objects.create_user(
    username='donor1',
    email='donor1@example.com',
    password='secure123'
)

donor = Donor.objects.create(
    user=user,
    blood_type='O+',
    phone_number='+1-555-0123',
    location='New York, NY',
    date_of_birth=date(1990, 1, 15),
    is_available=True
)
```

## Field Choices

```python
# Blood Type Choices
BLOOD_TYPE_CHOICES = [
    ('O+', 'O+'),
    ('O-', 'O-'),
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
]
```

## Admin Commands

```bash
# Create superuser
python manage.py createsuperuser
# Access admin: http://localhost:8000/admin

# Make migrations
python manage.py makemigrations donor

# Apply migrations
python manage.py migrate donor

# Load test data
python manage.py loaddata donor_fixture.json

# Export data
python manage.py dumpdata donor > donor_data.json
```

## Testing Examples

```bash
# Register donor
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

# Get token
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test_donor", "password": "testpass123"}'

# Get profile (replace TOKEN)
curl -X GET http://localhost:8000/api/donors/my_profile/ \
  -H "Authorization: Token TOKEN"

# Get available donors
curl -X GET "http://localhost:8000/api/donors/available/?blood_type=O+" \
  -H "Authorization: Token TOKEN"

# Update availability
curl -X PATCH http://localhost:8000/api/donors/1/update_availability/ \
  -H "Authorization: Token TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_available": false}'
```

## Django Admin Features

- **List Display:** user, blood_type, location, is_available, created_at
- **Filters:** blood_type, is_available, location, created_at
- **Search:** First/Last name, email, phone number, location
- **Read-only:** created_at, updated_at
- **Fieldsets:** Organized by category (User, Blood, Personal, Donation, Blockchain, Timestamps)

## Related Objects

```python
# Access user from donor
donor.user  # User object

# Access donor from user
user.donor_profile  # Donor object

# User fields accessible
donor.user.username
donor.user.email
donor.user.get_full_name()

# Check if user has profile
if hasattr(user, 'donor_profile'):
    print(user.donor_profile.blood_type)
```

## Common Queries

```python
# Count available donors
count = Donor.objects.filter(is_available=True).count()

# Get first available O+ donor
donor = Donor.objects.filter(
    blood_type='O+',
    is_available=True
).first()

# Get donors with no donation history
new_donors = Donor.objects.filter(last_donation_date__isnull=True)

# Get recent donors
from django.utils import timezone
from datetime import timedelta

recent = Donor.objects.filter(
    last_donation_date__gte=timezone.now() - timedelta(days=30)
)

# Get by location (starts with)
donors = Donor.objects.filter(location__startswith='New')

# Count by blood type
from django.db.models import Count
stats = Donor.objects.values('blood_type').annotate(count=Count('id'))
```

## Signals (if implemented)

```python
# Potential signal usage
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Donor)
def donor_created(sender, instance, created, **kwargs):
    if created:
        # Send welcome notification
        # Assign wallet address
        pass
```

## Permissions Check

```python
# In views
from rest_framework.permissions import IsAuthenticated

permission_classes = [IsAuthenticated]

# Check in code
if request.user.is_authenticated:
    donor = request.user.donor_profile
```

## Error Handling

```python
# Handle missing donor profile
try:
    donor = request.user.donor_profile
except Donor.DoesNotExist:
    return Response(
        {'error': 'Donor profile not found'},
        status=status.HTTP_404_NOT_FOUND
    )

# Handle integrity errors
try:
    donor = Donor.objects.create(**data)
except IntegrityError:
    return Response(
        {'error': 'Donor already exists for this user'},
        status=status.HTTP_400_BAD_REQUEST
    )
```

## Performance Tips

1. **Use select_related for User:**
   ```python
   donors = Donor.objects.select_related('user').filter(is_available=True)
   ```

2. **Use prefetch_related for many-to-many (if added later):**
   ```python
   donors = Donor.objects.prefetch_related('donations').all()
   ```

3. **Use only/defer for large querysets:**
   ```python
   donors = Donor.objects.only('id', 'blood_type', 'location').all()
   ```

4. **Index frequently filtered fields:** Already done on blood_type, is_available, location

## Documentation Links

- Full API Documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Migration Guide: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- Implementation Summary: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
