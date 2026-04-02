# Blood Tracking App - Getting Started Guide

## Quick Setup (5 Minutes)

### Step 1: Run Migrations
```bash
python manage.py makemigrations blood_tracking
python manage.py migrate blood_tracking
```

### Step 2: Test the API
```bash
curl -X GET http://localhost:8000/api/blood-tracking/units/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Step 3: Access Django Admin
```
http://localhost:8000/admin/blood-tracking/bloodunit/
```

---

## First Blood Unit (10 Minutes)

### 1. Get Your Token
```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

Save the token returned in the response.

### 2. Create a Blood Unit
```bash
curl -X POST http://localhost:8000/api/blood-tracking/units/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "donor": 1,
    "blood_type": "O+",
    "collection_date": "2026-04-02T10:30:00Z",
    "expiry_date": "2026-05-02T10:30:00Z",
    "hiv_test": false,
    "hepatitis_test": false
  }'
```

You'll receive:
```json
{
  "id": 1,
  "unit_id": "550e8400-e29b-41d4-a716-446655440000",
  "donor": 1,
  "blood_type": "O+",
  "status": "collected",
  ...
}
```

Save the `unit_id` for next steps.

### 3. List Available Units by Blood Type
```bash
curl -X GET "http://localhost:8000/api/blood-tracking/units/by_blood_type/?blood_type=O+" \
  -H "Authorization: Token YOUR_TOKEN"
```

Response:
```json
{
  "blood_type": "O+",
  "count": 1,
  "results": [
    {
      "unit_id": "550e8400-e29b-41d4-a716-446655440000",
      "donor": 1,
      "donor_name": "John Doe",
      "status": "storage",
      ...
    }
  ]
}
```

### 4. Send to Testing
```bash
curl -X PATCH "http://localhost:8000/api/blood-tracking/units/1/update_status/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "testing",
    "notes": "Lab testing initiated"
  }'
```

Response:
```json
{
  "message": "Blood unit status updated from collected to testing",
  "unit": {
    "id": 1,
    "status": "testing",
    "status_history": [
      {
        "previous_status": "collected",
        "new_status": "testing",
        "timestamp": "2026-04-02T11:00:00Z",
        "notes": "Lab testing initiated"
      }
    ]
  }
}
```

### 5. Move to Storage
```bash
curl -X PATCH "http://localhost:8000/api/blood-tracking/units/1/update_status/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "storage",
    "current_location": 1,
    "notes": "Tests passed, moved to cold storage at Central Hospital"
  }'
```

### 6. View Complete Lifecycle
```bash
curl -X GET "http://localhost:8000/api/blood-tracking/units/1/lifecycle_history/" \
  -H "Authorization: Token YOUR_TOKEN"
```

Shows complete history:
```json
{
  "status_transitions": {
    "from_status": "storage",
    "history": [
      {
        "previous_status": "collected",
        "new_status": "testing",
        "timestamp": "2026-04-02T11:00:00Z",
        "notes": "Lab testing initiated"
      },
      {
        "previous_status": "testing",
        "new_status": "storage",
        "timestamp": "2026-04-02T12:00:00Z",
        "notes": "Tests passed, moved to cold storage"
      }
    ]
  }
}
```

---

## Using Python Client

### Install requests
```bash
pip install requests
```

### Example Script
```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/blood-tracking"
TOKEN = "YOUR_TOKEN_HERE"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# 1. Create a blood unit
unit_data = {
    "donor": 1,
    "blood_type": "O+",
    "collection_date": datetime.now().isoformat() + "Z",
    "expiry_date": (datetime.now() + timedelta(days=35)).isoformat() + "Z",
    "hiv_test": False,
    "hepatitis_test": False
}

response = requests.post(f"{BASE_URL}/units/", headers=headers, json=unit_data)
unit = response.json()
unit_id = unit['id']
print(f"Created unit: {unit['unit_id']}")

# 2. List available O+ units
response = requests.get(
    f"{BASE_URL}/units/by_blood_type/",
    params={"blood_type": "O+"},
    headers=headers
)
data = response.json()
print(f"Available O+ units: {data['count']}")
for unit in data['results']:
    print(f"  - {unit['unit_id']}: {unit['donor_name']}")

# 3. Update status to testing
response = requests.patch(
    f"{BASE_URL}/units/{unit_id}/update_status/",
    headers=headers,
    json={
        "status": "testing",
        "notes": "Lab testing initiated"
    }
)
print(f"Status: {response.json()['message']}")

# 4. Update status to storage
response = requests.patch(
    f"{BASE_URL}/units/{unit_id}/update_status/",
    headers=headers,
    json={
        "status": "storage",
        "current_location": 1,
        "notes": "Tests passed"
    }
)

# 5. Get lifecycle history
response = requests.get(
    f"{BASE_URL}/units/{unit_id}/lifecycle_history/",
    headers=headers
)
lifecycle = response.json()
print(f"\nLifecycle for {lifecycle['unit_id']}:")
for change in lifecycle['status_transitions']['history']:
    print(f"  {change['timestamp']}: {change['previous_status']} → {change['new_status']}")
    if change['notes']:
        print(f"    Notes: {change['notes']}")
```

---

## Using Django Admin

### 1. Navigate to Admin
```
http://localhost:8000/admin/
```

### 2. Login with Superuser
Use your admin credentials

### 3. Create Blood Unit
- Click "Blood Units" in left sidebar
- Click "Add Blood Unit"
- Fill required fields:
  - Donor (select from dropdown)
  - Blood Type (8 options)
  - Collection Date
  - Expiry Date
- Optional fields:
  - Current Location (hospital)
  - Test Results (HIV, Hepatitis)
- Click Save

### 4. Manage Units
- View all units with status, dates, location
- Search by: unit_id, donor name, blood type
- Filter by: status, blood type, test results, date
- Click unit to edit
- Update status and add notes
- Status history appears in lifecycle field

### 5. View Lifecycle
- Click on unit
- Scroll to "Lifecycle History" section
- Expand to see all status changes
- Each change shows: timestamp, previous status, new status, notes

---

## Common Workflows

### Workflow 1: New Donation → Testing → Storage

```bash
# 1. Create unit after donation
curl -X POST http://localhost:8000/api/blood-tracking/units/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "donor": 1,
    "blood_type": "O+",
    "collection_date": "2026-04-02T10:30:00Z",
    "expiry_date": "2026-05-07T10:30:00Z"
  }'

# 2. Send to testing
curl -X PATCH "http://localhost:8000/api/blood-tracking/units/1/update_status/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "testing",
    "notes": "Routine lab testing"
  }'

# 3. Move to storage after tests pass
curl -X PATCH "http://localhost:8000/api/blood-tracking/units/1/update_status/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "storage",
    "current_location": 1,
    "notes": "All tests passed"
  }'
```

### Workflow 2: Find Available Units & Transfuse

```bash
# 1. Find available O+ units
curl -X GET "http://localhost:8000/api/blood-tracking/units/by_blood_type/?blood_type=O+" \
  -H "Authorization: Token $TOKEN"

# 2. Select unit and transfuse
curl -X PATCH "http://localhost:8000/api/blood-tracking/units/1/update_status/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "transfused",
    "current_location": 2,
    "notes": "Transfused to patient ID 12345"
  }'
```

### Workflow 3: Check Inventory at Hospital

```bash
# Get all units at a specific hospital
curl -X GET "http://localhost:8000/api/blood-tracking/units/units_at_location/?location_id=1" \
  -H "Authorization: Token $TOKEN"
```

### Workflow 4: Monitor Expiring Units

```bash
# Get units expiring in next 7 days
curl -X GET "http://localhost:8000/api/blood-tracking/units/near_expiry/" \
  -H "Authorization: Token $TOKEN"

# Then transfuse or mark as expired
curl -X PATCH "http://localhost:8000/api/blood-tracking/units/1/update_status/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "expired",
    "notes": "Expired, ready for disposal"
  }'
```

---

## Blood Type Reference

```
O+ (O Positive)     - Most common, universal donor
O- (O Negative)     - Universal donor, rare
A+ (A Positive)     - Can receive O+, A+
A- (A Negative)     - Can receive O-, A-
B+ (B Positive)     - Can receive O+, B+
B- (B Negative)     - Can receive O-, B-
AB+ (AB Positive)   - Can receive all types
AB- (AB Negative)   - Can receive O-, A-, B-, AB-
```

---

## Status Reference

```
collected  → Unit just drawn from donor
testing    → Unit in lab for blood type & disease tests
storage    → Tests passed, unit in cold storage
transfused → Unit given to patient
expired    → Unit passed expiry date
```

---

## Troubleshooting

### 401 Unauthorized Error
**Problem:** "Authentication credentials were not provided"
**Solution:**
```bash
# Get token first
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token in header
curl -X GET http://localhost:8000/api/blood-tracking/units/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### 400 Bad Request - Missing Parameter
**Problem:** "blood_type parameter is required"
**Solution:** Add the missing query parameter
```bash
# Wrong:
curl http://localhost:8000/api/blood-tracking/units/by_blood_type/

# Right:
curl "http://localhost:8000/api/blood-tracking/units/by_blood_type/?blood_type=O+"
```

### 400 Bad Request - Invalid Date
**Problem:** "Expiry date must be after collection date"
**Solution:** Ensure expiry date is in future
```python
# Wrong:
{
  "collection_date": "2026-05-02T10:30:00Z",
  "expiry_date": "2026-04-02T10:30:00Z"  # Before collection!
}

# Right:
{
  "collection_date": "2026-04-02T10:30:00Z",
  "expiry_date": "2026-05-02T10:30:00Z"  # 30 days later
}
```

### 404 Not Found Error
**Problem:** Unit doesn't exist
**Solution:** Verify unit ID exists
```bash
# List all units first
curl -X GET http://localhost:8000/api/blood-tracking/units/ \
  -H "Authorization: Token $TOKEN"

# Then use correct ID
curl -X GET http://localhost:8000/api/blood-tracking/units/1/ \
  -H "Authorization: Token $TOKEN"
```

### No Units in by_blood_type
**Problem:** by_blood_type returns empty even though units exist
**Cause:** by_blood_type only returns units with status='storage'
**Solution:** Check unit status
```bash
# Get all units (any status)
curl -X GET http://localhost:8000/api/blood-tracking/units/ \
  -H "Authorization: Token $TOKEN"

# Units must be in 'storage' state for by_blood_type
```

---

## Data Model

### BloodUnit Fields

```python
{
  "id": 1,                              # Database ID
  "unit_id": "550e8400-...",           # Unique UUID
  "donor": 1,                          # Donor ID (FK)
  "donor_name": "John Doe",            # Read-only
  "blood_type": "O+",                  # One of 8 types
  "collection_date": "2026-04-02...",  # ISO format
  "expiry_date": "2026-05-02...",      # ISO format
  "current_location": 1,               # Hospital ID (FK, nullable)
  "hospital_name": "Central Hospital", # Read-only
  "status": "storage",                 # One of 5 statuses
  "hiv_test": true,                    # Boolean
  "hepatitis_test": true,              # Boolean
  "blockchain_tx_hash": "0x...",       # Optional
  "status_history": [...],             # JSON (read-only)
  "created_at": "2026-04-02...",       # Auto
  "updated_at": "2026-04-02...",       # Auto
}
```

---

## Performance Tips

1. **Use `by_blood_type` for quick filtering**
   - Returns only storage units (fastest)
   - Filter at API level, not application

2. **Use `near_expiry` for urgent inventory**
   - Identifies units needing action
   - 7-day threshold (optimal window)

3. **Use `units_at_location` for hospital inventory**
   - Fast location-based lookup
   - Useful for hospital admin dashboard

4. **List endpoint pagination**
   - Use ?page=2 for next page
   - Avoids loading all units in memory

---

## Next Steps

1. ✅ Complete this getting started guide
2. Create test data (multiple donors, units)
3. Test all endpoints with your data
4. Set up automated alerts for expiring units
5. Integrate with hospital blood request app
6. Create mobile app interface
7. Add blockchain verification

---

## Links & Resources

- **API Documentation:** See `API_DOCUMENTATION.md`
- **Quick Reference:** See `QUICK_REFERENCE.md`  
- **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md`
- **Django Docs:** https://docs.djangoproject.com/
- **DRF Docs:** https://www.django-rest-framework.org/

---

## Support

For issues or questions:
1. Check this guide's Troubleshooting section
2. Review API_DOCUMENTATION.md for endpoint details
3. Check QUICK_REFERENCE.md for code examples
4. Review Django admin interface
5. Check server logs for errors

---

**Happy Blood Tracking! 🩸❤️**

Start by running migrations and creating your first blood unit!
