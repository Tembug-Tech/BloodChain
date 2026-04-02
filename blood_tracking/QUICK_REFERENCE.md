# Blood Tracking App - Quick Reference

## Model Overview

### BloodUnit
Individual blood unit tracking with lifecycle management.

**Fields:**
```python
unit_id           # UUIDField (unique)
donor             # ForeignKey(Donor)
blood_type        # CharField ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-')
collection_date   # DateTimeField
expiry_date       # DateTimeField
current_location  # ForeignKey(Hospital, nullable)
status            # CharField ('collected', 'testing', 'storage', 'transfused', 'expired')
hiv_test          # BooleanField (default: False)
hepatitis_test    # BooleanField (default: False)
blockchain_tx_hash # CharField (nullable)
status_history    # JSONField (stores status changes)
created_at        # DateTimeField (auto)
updated_at        # DateTimeField (auto)
```

---

## API Endpoints Quick Reference

### Blood Units

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/units/` | GET | List all blood units |
| `/units/` | POST | Create new blood unit |
| `/units/{id}/` | GET | Get unit details with lifecycle |
| `/units/{id}/` | PATCH | Update unit fields |
| `/units/{id}/` | DELETE | Delete blood unit |
| `/units/{id}/update_status/` | PATCH | Update status + record history |
| `/units/{id}/lifecycle_history/` | GET | Get complete lifecycle |
| `/units/by_blood_type/` | GET | List by blood type (storage only) |
| `/units/available_units/` | GET | List all storage units |
| `/units/units_at_location/` | GET | List units at hospital |
| `/units/near_expiry/` | GET | List units expiring in 7 days |

### Blood Donations

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/donations/` | GET | List all donations |
| `/donations/{id}/` | GET | Get donation details |
| `/donations/my_donations/` | GET | Get authenticated donor's donations |
| `/donations/by_status/` | GET | Filter by status |

### Blood Transfers

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/transfers/` | GET | List all transfers |
| `/transfers/{id}/` | GET | Get transfer details |
| `/transfers/pending_transfers/` | GET | List pending transfers |
| `/transfers/{id}/mark_received/` | POST | Mark transfer received |

---

## Common Tasks

### Create a Blood Unit

```python
import requests

url = "http://localhost:8000/api/blood-tracking/units/"
headers = {"Authorization": "Token YOUR_TOKEN"}

data = {
    "donor": 1,
    "blood_type": "O+",
    "collection_date": "2026-04-02T10:30:00Z",
    "expiry_date": "2026-05-02T10:30:00Z",
    "hiv_test": False,
    "hepatitis_test": False
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### List Available O+ Units

```python
url = "http://localhost:8000/api/blood-tracking/units/by_blood_type/"
params = {"blood_type": "O+"}
headers = {"Authorization": "Token YOUR_TOKEN"}

response = requests.get(url, params=params, headers=headers)
for unit in response.json()['results']:
    print(f"{unit['unit_id']}: {unit['donor_name']}")
```

### Update Blood Unit Status

```python
url = "http://localhost:8000/api/blood-tracking/units/1/update_status/"
headers = {"Authorization": "Token YOUR_TOKEN"}

data = {
    "status": "storage",
    "current_location": 1,
    "notes": "Tests passed"
}

response = requests.patch(url, json=data, headers=headers)
print(response.json()['message'])
# Output: "Blood unit status updated from testing to storage"
```

### Get Lifecycle History

```python
url = "http://localhost:8000/api/blood-tracking/units/1/lifecycle_history/"
headers = {"Authorization": "Token YOUR_TOKEN"}

response = requests.get(url, headers=headers)
data = response.json()

print(f"Unit: {data['unit_id']}")
print(f"Status: {data['status_transitions']['from_status']}")
for change in data['status_transitions']['history']:
    print(f"  {change['previous_status']} → {change['new_status']}")
```

### Get Units Expiring Soon

```python
url = "http://localhost:8000/api/blood-tracking/units/near_expiry/"
headers = {"Authorization": "Token YOUR_TOKEN"}

response = requests.get(url, headers=headers)
data = response.json()

print(f"Units expiring in 7 days: {data['count']}")
for unit in data['results']:
    print(f"  {unit['unit_id']}: expires {unit['expiry_date']}")
```

---

## Database Queries

### Get All O+ Units in Storage
```python
from blood_tracking.models import BloodUnit

units = BloodUnit.objects.filter(
    blood_type='O+',
    status='storage'
).select_related('donor', 'current_location')

for unit in units:
    print(f"{unit.unit_id}: {unit.donor.user.get_full_name()}")
```

### Get Units at Specific Hospital
```python
from blood_tracking.models import BloodUnit

units = BloodUnit.objects.filter(
    current_location_id=1,
    status='storage'
).values('blood_type').annotate(count=Count('id'))

for item in units:
    print(f"{item['blood_type']}: {item['count']} units")
```

### Get Units Expiring Within 7 Days
```python
from blood_tracking.models import BloodUnit
from django.utils import timezone
from datetime import timedelta

near_expiry = timezone.now() + timedelta(days=7)

units = BloodUnit.objects.filter(
    status='storage',
    expiry_date__lte=near_expiry,
    expiry_date__gt=timezone.now()
).order_by('expiry_date')

for unit in units:
    days_left = (unit.expiry_date - timezone.now()).days
    print(f"{unit.unit_id}: {days_left} days left")
```

### Get Status Change History for Unit
```python
from blood_tracking.models import BloodUnit

unit = BloodUnit.objects.get(unit_id='550e8400-e29b-41d4-a716-446655440000')

for change in unit.status_history:
    print(f"{change['timestamp']}: {change['previous_status']} → {change['new_status']}")
    if change['notes']:
        print(f"  Notes: {change['notes']}")
```

### Count Available Units by Blood Type
```python
from blood_tracking.models import BloodUnit
from django.db.models import Count

inventory = BloodUnit.objects.filter(
    status='storage'
).values('blood_type').annotate(
    count=Count('id')
).order_by('-count')

for item in inventory:
    print(f"{item['blood_type']}: {item['count']} units")
```

### Get All Transfused Units by Donor
```python
from blood_tracking.models import BloodUnit

donor_id = 1
transfused = BloodUnit.objects.filter(
    donor_id=donor_id,
    status='transfused'
).order_by('-updated_at')

print(f"Donor {donor_id} has {transfused.count()} transfused units")
for unit in transfused:
    print(f"  {unit.unit_id}: transfused on {unit.updated_at}")
```

---

## Serializers

### BloodUnitSerializer (Basic)
Used for: List endpoints
Includes: Basic unit info, donor name, hospital name

### BloodUnitDetailSerializer (Full)
Used for: Detail endpoints, lifecycle history
Includes: Full donor info, hospital info, complete lifecycle summary

### BloodUnitCreateSerializer (Create-only)
Used for: POST requests
Validates: Expiry date > collection date

### BloodUnitStatusUpdateSerializer (Update-only)
Used for: PATCH update_status action
Fields: status, current_location, blockchain_tx_hash

---

## Admin Interface

Access at: `http://localhost:8000/admin/blood-tracking/bloodunit/`

**Features:**
- List view: unit_id, donor, blood_type, status, dates, location
- Search: by unit_id, donor name, blood type
- Filters: status, blood_type, hiv_test, hepatitis_test, collection_date
- Read-only: unit_id, created_at, updated_at, status_history
- Quick edit: status, location, test results

---

## Status Transition Flow

```
collected → testing → storage → transfused
                   ↓
                 expired
            (if past expiry date)
```

**Transitions:**
- `collected`: Unit just drawn from donor
- `testing`: Unit in lab for blood type & disease tests
- `storage`: Tests passed, unit in cold storage
- `transfused`: Unit given to patient
- `expired`: Unit passed expiry date

---

## Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | blood_type parameter is required | Missing query param |
| 400 | Expiry date must be after collection date | Invalid dates |
| 401 | Authentication credentials not provided | Missing token |
| 404 | Not found | Unit doesn't exist |
| 500 | Internal server error | Server issue |

---

## cURL Examples

### Create Unit
```bash
curl -X POST http://localhost:8000/api/blood-tracking/units/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "donor": 1,
    "blood_type": "O+",
    "collection_date": "2026-04-02T10:30:00Z",
    "expiry_date": "2026-05-02T10:30:00Z"
  }'
```

### List by Blood Type
```bash
curl -X GET "http://localhost:8000/api/blood-tracking/units/by_blood_type/?blood_type=O+" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Update Status
```bash
curl -X PATCH "http://localhost:8000/api/blood-tracking/units/1/update_status/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "storage", "current_location": 1}'
```

### Get Lifecycle
```bash
curl -X GET "http://localhost:8000/api/blood-tracking/units/1/lifecycle_history/" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Get Expiring Soon
```bash
curl -X GET "http://localhost:8000/api/blood-tracking/units/near_expiry/" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Performance Tips

1. **Use `by_blood_type` for quick filtering**
   - Only returns units in storage (available)
   - Faster than general list + filter

2. **Check `near_expiry` regularly**
   - Identifies units needing transfusion urgently
   - Uses 7-day threshold (configurable)

3. **Use `units_at_location` for inventory checks**
   - Get hospital-specific inventory quickly
   - Combined query with status filter

4. **Leverage `lifecycle_history` endpoint**
   - Complete history in one call
   - No need to query status_history JSONField

---

## Testing

### Test Create Unit
```bash
# 1. Get token
TOKEN=$(curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | jq -r '.token')

# 2. Create unit
curl -X POST http://localhost:8000/api/blood-tracking/units/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "donor": 1,
    "blood_type": "O+",
    "collection_date": "2026-04-02T10:30:00Z",
    "expiry_date": "2026-05-02T10:30:00Z"
  }' | jq .
```

### Test Lifecycle
```bash
curl -X GET "http://localhost:8000/api/blood-tracking/units/1/lifecycle_history/" \
  -H "Authorization: Token $TOKEN" | jq '.lifecycle_history'
```

---

## Settings & Configuration

**In settings.py:**
```python
# Blood Tracking App
INSTALLED_APPS = [
    ...
    'blood_tracking',
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

---

## Integration Notes

### With Donor App
```python
# Access donor info from unit
unit = BloodUnit.objects.get(id=1)
donor_name = unit.donor.user.get_full_name()
donor_blood_type = unit.donor.blood_type
```

### With Hospital App
```python
# Access hospital info from unit
unit = BloodUnit.objects.get(id=1)
hospital_name = unit.current_location.name
hospital_address = unit.current_location.address
```

### With BloodDonation
```python
# Connect unit to donation later via donation.blood_units
donation = BloodDonation.objects.get(id=1)
# Then create units from this donation
unit = BloodUnit.objects.create(
    donor=donation.donor,
    blood_type=donation.donor.blood_type,
    collection_date=donation.donation_date,
    expiry_date=donation.donation_date + timedelta(days=35)
)
```

---

## Troubleshooting

### Units Not Appearing by Blood Type
- Ensure units have `status='storage'`
- Check blood_type is exact match (case-sensitive)
- Verify units are not filtered out

### Status Updates Not Recording
- Ensure new_status is different from current
- Check permissions (IsAuthenticated required)
- Verify status value is in CHOICES

### Expiry Check Not Working
- Verify timezone settings in settings.py
- Check that expiry_date is in future
- Note: Uses 7-day threshold

---

**Version:** 1.0  
**Last Updated:** 2026-04-02

See API_DOCUMENTATION.md for detailed endpoint documentation.
