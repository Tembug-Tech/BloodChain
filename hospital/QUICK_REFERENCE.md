# Hospital App - Quick Reference

## Models

### Hospital
```python
- id: AutoField
- name: CharField (unique)
- address: TextField
- city: CharField
- state: CharField
- country: CharField
- postal_code: CharField
- phone_number: CharField
- email: EmailField
- registration_number: CharField (unique)
- website: URLField (optional)
- is_verified: BooleanField (default: False)
- is_active: BooleanField (default: True)
- admin: ForeignKey(User, optional)
- created_at: DateTimeField (auto)
- updated_at: DateTimeField (auto)
```

### BloodRequest
```python
- id: AutoField
- hospital: ForeignKey(Hospital)
- blood_type: CharField (8 blood type choices)
- units_needed: DecimalField (0-999.99)
- urgency_level: CharField (critical, urgent, normal)
- status: CharField (open, fulfilled, cancelled)
- description: TextField (optional)
- created_at: DateTimeField (auto)
- fulfilled_at: DateTimeField (optional, set on fulfillment)
```

## API Endpoints Summary

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | `/hospitals/` | Create hospital | Yes |
| GET | `/hospitals/` | List hospitals | Yes |
| PATCH | `/hospitals/{id}/` | Update hospital | Yes |
| GET | `/hospitals/verified_hospitals/` | Get verified hospitals | Yes |
| GET | `/hospitals/{id}/blood_availability/` | Get hospital inventory | Yes |
| GET | `/hospitals/{id}/blood_requests/` | Get hospital requests | Yes |
| POST | `/blood-requests/` | Create blood request | Yes |
| GET | `/blood-requests/` | List all requests | Yes |
| GET | `/blood-requests/by_blood_type/` | Get by blood type | Yes |
| GET | `/blood-requests/open_requests/` | Get open requests | Yes |
| GET | `/blood-requests/critical_requests/` | Get critical requests | Yes |
| PATCH | `/blood-requests/{id}/update_status/` | Update status | Yes |
| GET | `/blood-requests/hospital_requests/` | Get hospital requests | Yes |

## Quick Code Examples

### Create Hospital
```bash
curl -X POST http://localhost:8000/api/hospitals/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "City Hospital",
    "address": "123 Main St",
    "city": "Boston",
    "state": "MA",
    "country": "USA",
    "postal_code": "02101",
    "phone_number": "+1-555-0001",
    "email": "contact@cityhospital.com",
    "registration_number": "REG-001"
  }'
```

### Create Blood Request
```bash
curl -X POST http://localhost:8000/api/blood-requests/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hospital": 1,
    "blood_type": "O+",
    "units_needed": "10.00",
    "urgency_level": "critical",
    "description": "Emergency surgery"
  }'
```

### Get O+ Requests
```bash
curl -X GET "http://localhost:8000/api/blood-requests/by_blood_type/?blood_type=O+" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Get Critical Requests
```bash
curl -X GET "http://localhost:8000/api/blood-requests/critical_requests/" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Update Status to Fulfilled
```bash
curl -X PATCH "http://localhost:8000/api/blood-requests/1/update_status/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "fulfilled"}'
```

## Python Queries

### Create Hospital
```python
from hospital.models import Hospital

hospital = Hospital.objects.create(
    name='Test Hospital',
    address='123 Main St',
    city='Boston',
    state='MA',
    country='USA',
    postal_code='02101',
    phone_number='+1-555-0001',
    email='test@test.com',
    registration_number='REG-001'
)
```

### Create Blood Request
```python
from hospital.models import Hospital, BloodRequest

hospital = Hospital.objects.get(id=1)
request = BloodRequest.objects.create(
    hospital=hospital,
    blood_type='O+',
    units_needed=10.00,
    urgency_level='critical',
    description='Emergency'
)
```

### Query Open Requests
```python
# All open requests
open_requests = BloodRequest.objects.filter(status='open')

# By blood type
o_plus = BloodRequest.objects.filter(blood_type='O+', status='open')

# Critical priority
critical = BloodRequest.objects.filter(urgency_level='critical', status='open')

# For specific hospital
hospital_requests = BloodRequest.objects.filter(hospital_id=1, status='open')

# Count open requests
count = BloodRequest.objects.filter(status='open').count()
```

### Update Status
```python
request = BloodRequest.objects.get(id=1)
request.status = 'fulfilled'
request.save()

# With auto fulfilled_at timestamp (in view)
from django.utils import timezone
request.fulfilled_at = timezone.now()
request.save()
```

## Blood Type Choices
```
'O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'
```

## Urgency Levels
```
'critical' → Immediate need
'urgent'   → High priority
'normal'   → Routine
```

## Status Choices
```
'open'      → Request is open
'fulfilled' → Request fulfilled
'cancelled' → Request cancelled
```

## Admin Interface Features

### Hospital Admin
- List: name, city, is_verified, is_active, created_at
- Search: name, email, phone, registration_number
- Filter: is_verified, is_active, created_at
- Actions: Edit, Delete

### BloodRequest Admin
- List: hospital, blood_type, units_needed, urgency_level, status, created_at
- Search: hospital name, blood_type, description
- Filter: status, blood_type, urgency_level, created_at
- Actions: Edit, Delete

## Serializers

| Serializer | Use Case |
|-----------|----------|
| HospitalSerializer | Full hospital data |
| HospitalCreateSerializer | Creating hospitals |
| BloodRequestSerializer | Basic request data |
| BloodRequestDetailSerializer | Detailed request with hospital info |
| BloodInventorySerializer | Blood inventory |

## Common Patterns

### Filter Open Requests by Blood Type
```python
BloodRequest.objects.filter(status='open', blood_type='O+')
```

### Get Latest Requests
```python
BloodRequest.objects.filter(status='open').order_by('-created_at')[:5]
```

### Get Urgent/Critical Requests
```python
BloodRequest.objects.filter(
    status='open',
    urgency_level__in=['urgent', 'critical']
).order_by('-urgency_level')
```

### Get Unfulfilled Requests
```python
BloodRequest.objects.filter(status__in=['open', 'pending'])
```

### Health Check Queries
```python
# Total requests
BloodRequest.objects.count()

# Open requests percentage
open_count = BloodRequest.objects.filter(status='open').count()
total_count = BloodRequest.objects.count()
percentage = (open_count / total_count) * 100

# Average units needed
from django.db.models import Avg
avg_units = BloodRequest.objects.filter(status='open').aggregate(Avg('units_needed'))
```

## Error Handling

### Missing Required Field
```json
{
  "status": ["This field is required."]
}
```

### Invalid Status
```json
{
  "error": "status must be one of: open, fulfilled, cancelled"
}
```

### Hospital Not Found
```json
{
  "error": "Hospital not found"
}
```

## Testing Workflow

1. Create hospital via POST /api/hospitals/
2. Create blood request via POST /api/blood-requests/
3. List open requests via GET /api/blood-requests/open_requests/
4. Filter by blood type via GET /api/blood-requests/by_blood_type/?blood_type=O+
5. Update status via PATCH /api/blood-requests/{id}/update_status/
6. Verify fulfilled_at timestamp is set

## Useful Django Shell Commands

```bash
python manage.py shell
```

```python
# Import models
from hospital.models import Hospital, BloodRequest

# Create test data
h = Hospital.objects.create(name='Test', address='Test', city='Test', 
                           state='Test', country='Test', postal_code='Test',
                           phone_number='1234567890', email='test@test.com',
                           registration_number='REG-TEST')

b = BloodRequest.objects.create(hospital=h, blood_type='O+', 
                               units_needed=5, urgency_level='critical')

# Query
BloodRequest.objects.all()
BloodRequest.objects.filter(status='open')
BloodRequest.objects.filter(blood_type='O+', status='open')
```

## Next Steps

1. ✅ Apply migrations: `python manage.py migrate hospital`
2. ✅ Test endpoints using provided curl examples
3. ⏳ Integrate with donor matching system
4. ⏳ Add notifications on request creation
5. ⏳ Create request fulfillment matching algorithm
6. ⏳ Add request expiry/timeout logic

## Documentation Files

- **API_DOCUMENTATION.md** - Complete API reference
- **QUICK_REFERENCE.md** - This file
- **IMPLEMENTATION_SUMMARY.md** - Technical details (coming soon)

## Related Models in BloodChain

- **Donor** - blood donor profiles
- **BloodDonation** - donation records
- **BloodTransfer** - transfer tracking
- **BloodInventory** - hospital blood stock
- **BloodRequest** - hospital blood needs (new)

All models share common blood type choices for consistency.
