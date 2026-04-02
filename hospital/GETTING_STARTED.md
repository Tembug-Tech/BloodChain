# Hospital App - Getting Started Guide

## Quick Setup (5 Minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Migrations
```bash
python manage.py makemigrations hospital
python manage.py migrate hospital
```

### Step 3: Create a Hospital Admin Account
```bash
python manage.py createsuperuser
# Follow the prompts to create admin account
```

### Step 4: Start the Server
```bash
python manage.py runserver
```

### Step 5: Access the API
- API Base URL: `http://localhost:8000/api/`
- Admin Panel: `http://localhost:8000/admin/`

---

## First Blood Request (10 Minutes)

### 1. Get Admin Token
```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

You'll receive:
```json
{
  "token": "YOUR_TOKEN_HERE"
}
```

### 2. Create a Hospital
```bash
curl -X POST http://localhost:8000/api/hospitals/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "City Hospital",
    "address": "456 Hospital Ave",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "postal_code": "10001",
    "phone_number": "+1-212-555-0100",
    "email": "admin@cityhospital.com",
    "registration_number": "REG-NY-2024-001",
    "website": "https://cityhospital.com"
  }'
```

Response:
```json
{
  "id": 1,
  "name": "City Hospital",
  "registration_number": "REG-NY-2024-001",
  "email": "admin@cityhospital.com",
  ...
}
```

### 3. Post a Blood Request
```bash
curl -X POST http://localhost:8000/api/blood-requests/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "hospital": 1,
    "blood_type": "O+",
    "units_needed": "15.00",
    "urgency_level": "critical",
    "description": "Emergency blood transfusion needed"
  }'
```

Response:
```json
{
  "id": 1,
  "hospital": 1,
  "hospital_name": "City Hospital",
  "blood_type": "O+",
  "units_needed": "15.00",
  "urgency_level": "critical",
  "status": "open",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 4. Check Open Requests
```bash
curl -X GET "http://localhost:8000/api/blood-requests/open_requests/" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### 5. Find Critical Requests
```bash
curl -X GET "http://localhost:8000/api/blood-requests/critical_requests/" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### 6. Get by Blood Type
```bash
curl -X GET "http://localhost:8000/api/blood-requests/by_blood_type/?blood_type=O+" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### 7. Mark as Fulfilled
```bash
curl -X PATCH "http://localhost:8000/api/blood-requests/1/update_status/" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"status": "fulfilled"}'
```

Response:
```json
{
  "message": "Blood request status updated successfully",
  "request": {
    "id": 1,
    "status": "fulfilled",
    "fulfilled_at": "2024-01-15T10:35:00Z"
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
import json

BASE_URL = "http://localhost:8000/api"
TOKEN = "YOUR_TOKEN_HERE"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Create hospital
hospital_data = {
    "name": "Emergency Hospital",
    "address": "789 Emergency Ln",
    "city": "Los Angeles",
    "state": "CA",
    "country": "USA",
    "postal_code": "90001",
    "phone_number": "+1-213-555-0001",
    "email": "contact@emergency.com",
    "registration_number": "REG-CA-2024-001"
}

response = requests.post(
    f"{BASE_URL}/hospitals/",
    headers=headers,
    json=hospital_data
)

hospital = response.json()
hospital_id = hospital['id']
print(f"Created hospital: {hospital['name']}")

# Create blood request
request_data = {
    "hospital": hospital_id,
    "blood_type": "AB-",
    "units_needed": "5.00",
    "urgency_level": "urgent",
    "description": "Pre-operative blood supply"
}

response = requests.post(
    f"{BASE_URL}/blood-requests/",
    headers=headers,
    json=request_data
)

blood_request = response.json()
request_id = blood_request['id']
print(f"Created request: {blood_request['id']}")

# Get open requests
response = requests.get(
    f"{BASE_URL}/blood-requests/open_requests/",
    headers=headers
)

open_requests = response.json()
print(f"Open requests: {len(open_requests['results'])}")

# Update status
response = requests.patch(
    f"{BASE_URL}/blood-requests/{request_id}/update_status/",
    headers=headers,
    json={"status": "fulfilled"}
)

print(f"Updated status: {response.json()['message']}")
```

---

## Using Django Admin

### 1. Navigate to Admin
```
http://localhost:8000/admin/
```

### 2. Login with Superuser Credentials
Use the credentials you created with `createsuperuser`

### 3. Hospital Management
- Click "Hospitals" in left sidebar
- Click "Add Hospital" to create new
- Fill in all required fields
- Save

### 4. Blood Request Management
- Click "Blood Requests" in left sidebar
- See all requests with status, urgency, blood type
- Search by hospital name or blood type
- Filter by status, blood type, urgency level, date
- Click request to view/edit details
- Update status to "fulfilled" when blood obtained
- Timestamp automatically recorded

### 5. View Hospital Inventory
- Click on Hospital name
- Scroll to "Blood Requests" section
- See all requests for that hospital

---

## Common Tasks

### Find All Critical O+ Requests
```bash
curl -X GET "http://localhost:8000/api/blood-requests/critical_requests/?blood_type=O+" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Find All Urgent Requests for Specific Hospital
```bash
curl -X GET "http://localhost:8000/api/blood-requests/hospital_requests/?hospital_id=1&urgency_level=urgent" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Get Hospital Details with Requests
```bash
curl -X GET "http://localhost:8000/api/hospitals/1/" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Cancel a Request
```bash
curl -X PATCH "http://localhost:8000/api/blood-requests/1/update_status/" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"status": "cancelled"}'
```

---

## Models Overview

### Hospital
```
- ID (auto)
- Name (unique, required)
- Registration Number (unique, required)
- Address Details (address, city, state, country, postal_code)
- Contact (phone_number, email, website)
- Status (is_verified, is_active)
- Admin (User FK)
- Timestamps (created_at, updated_at)
```

### BloodRequest
```
- ID (auto)
- Hospital (FK to Hospital)
- Blood Type (O+, O-, A+, A-, B+, B-, AB+, AB-, required)
- Units Needed (decimal, 0.01-999.99, required)
- Urgency Level (critical, urgent, normal, required)
- Status (open, fulfilled, cancelled, default=open)
- Description (optional)
- Created At (auto timestamp)
- Fulfilled At (auto timestamp when status=fulfilled)
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

## Troubleshooting

### 401 Unauthorized Error
**Problem:** "Authentication credentials were not provided"
**Solution:** Add the Authorization header with valid token
```bash
# Get token first
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token in requests
curl -X GET http://localhost:8000/api/blood-requests/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### 400 Bad Request Error
**Problem:** "Invalid blood_type" or other field validation
**Solution:** Check field values match allowed choices
```python
# Valid urgency_level values
"critical", "urgent", "normal"

# Valid status values
"open", "fulfilled", "cancelled"

# Valid blood_type values
"O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"

# units_needed must be decimal
"10.00", "5.50", "20.25"
```

### 404 Not Found Error
**Problem:** Hospital or request not found
**Solution:** Verify ID exists
```bash
# List all to find correct ID
curl -X GET http://localhost:8000/api/hospitals/ \
  -H "Authorization: Token YOUR_TOKEN"

curl -X GET http://localhost:8000/api/blood-requests/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### 500 Internal Server Error
**Problem:** Server error
**Solution:** Check server logs
```bash
# Terminal where runserver is running shows error details
# Or check Django error logs
tail -f logs/error.log
```

---

## Database & Migrations

### View All Migrations
```bash
python manage.py showmigrations hospital
```

### Rollback Last Migration
```bash
python manage.py migrate hospital 0002
# (replace with previous migration number)
```

### Fresh Database Setup
```bash
python manage.py migrate hospital zero      # Remove all migrations
python manage.py makemigrations hospital    # Create fresh migrations
python manage.py migrate hospital           # Apply migrations
python manage.py createsuperuser            # Create admin
```

---

## Performance Tips

1. **Use Filters Effectively**
   - Filter by urgency_level to find critical cases quickly
   - Use blood_type filter to find specific needs
   - Combine filters for precise results

2. **Pagination**
   - API returns 10 items per page
   - Use `?page=2` for next page
   - Results include pagination info

3. **Search**
   - Search hospital names via API
   - Use admin search for quick lookups
   - Works on: name, blood_type, description

---

## Next Steps

1. ✅ Complete this getting started guide
2. Create hospital accounts for each facility
3. Register blood requests
4. Connect with donor app for matching
5. Set up notifications for urgent requests
6. Add request expiry logic
7. Create analytics dashboard

---

## Links & Resources

- **API Documentation:** See `API_DOCUMENTATION.md`
- **Quick Reference:** See `QUICK_REFERENCE.md`
- **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md`
- **Django Docs:** https://docs.djangoproject.com/
- **DRF Docs:** https://www.django-rest-framework.org/

---

**Happy Blood Banking! 🩸❤️**

For more help, check the API_DOCUMENTATION.md file.
