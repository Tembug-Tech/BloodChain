# Hospital App API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Endpoints Overview

### Hospitals
- `POST /hospitals/` - Create a new hospital
- `GET /hospitals/` - List all hospitals
- `GET /hospitals/{id}/` - Get hospital details
- `PATCH /hospitals/{id}/` - Update hospital
- `DELETE /hospitals/{id}/` - Delete hospital
- `GET /hospitals/verified_hospitals/` - Get verified hospitals
- `GET /hospitals/{id}/blood_availability/` - Get hospital's blood inventory
- `GET /hospitals/{id}/blood_requests/` - Get hospital's blood requests

### Blood Requests
- `POST /blood-requests/` - Create a blood request
- `GET /blood-requests/` - List all blood requests
- `GET /blood-requests/{id}/` - Get blood request details
- `PATCH /blood-requests/{id}/update_status/` - Update request status
- `GET /blood-requests/open_requests/` - Get all open requests
- `GET /blood-requests/by_blood_type/` - Get open requests by blood type
- `GET /blood-requests/critical_requests/` - Get critical priority requests
- `GET /blood-requests/hospital_requests/` - Get requests for specific hospital

---

## 1. Create Hospital
**Endpoint:** `POST /api/hospitals/`

**Authentication:** Required

**Description:** Create a new hospital in the system.

**Request Body:**
```json
{
  "name": "City General Hospital",
  "address": "123 Main Street",
  "city": "Boston",
  "state": "MA",
  "country": "USA",
  "postal_code": "02101",
  "phone_number": "+1-617-555-0001",
  "email": "contact@cityhospital.com",
  "registration_number": "REG-MA-001",
  "website": "https://cityhospital.com"
}
```

**Field Details:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Hospital name (unique) |
| address | string | Yes | Street address |
| city | string | Yes | City name |
| state | string | Yes | State/Province |
| country | string | Yes | Country name |
| postal_code | string | Yes | Postal/Zip code |
| phone_number | string | Yes | Contact phone (max 15 chars) |
| email | string | Yes | Contact email |
| registration_number | string | Yes | Unique registration number |
| website | string | No | Hospital website URL |

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "City General Hospital",
  "address": "123 Main Street",
  "city": "Boston",
  "state": "MA",
  "country": "USA",
  "postal_code": "02101",
  "phone_number": "+1-617-555-0001",
  "email": "contact@cityhospital.com",
  "registration_number": "REG-MA-001",
  "website": "https://cityhospital.com",
  "is_verified": false,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## 2. Create Blood Request
**Endpoint:** `POST /api/blood-requests/`

**Authentication:** Required

**Description:** Create a new blood request for a hospital.

**Request Body:**
```json
{
  "hospital": 1,
  "blood_type": "O+",
  "units_needed": "10.00",
  "urgency_level": "critical",
  "description": "Emergency trauma surgery in progress"
}
```

**Field Details:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| hospital | integer | Yes | Hospital ID requesting blood |
| blood_type | string | Yes | Blood type needed |
| units_needed | decimal | Yes | Number of units needed (max 999.99) |
| urgency_level | string | Yes | critical, urgent, or normal |
| description | string | No | Additional details about the request |

**Blood Type Choices:**
- O+, O-, A+, A-, B+, B-, AB+, AB-

**Urgency Level Choices:**
- critical: Immediate need
- urgent: High priority
- normal: Routine request

**Response (201 Created):**
```json
{
  "message": "Blood request created successfully",
  "request": {
    "id": 5,
    "hospital": 1,
    "hospital_name": "City General Hospital",
    "blood_type": "O+",
    "units_needed": "10.00",
    "urgency_level": "critical",
    "status": "open",
    "description": "Emergency trauma surgery in progress",
    "created_at": "2024-01-15T11:45:00Z",
    "fulfilled_at": null
  }
}
```

---

## 3. List Open Blood Requests by Blood Type
**Endpoint:** `GET /api/blood-requests/by_blood_type/`

**Authentication:** Required

**Description:** Get all open blood requests filtered by blood type.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| blood_type | string | Yes | Blood type to filter by |

**Request Examples:**
```bash
# Get all O+ requests
curl -X GET "http://localhost:8000/api/blood-requests/by_blood_type/?blood_type=O+" \
  -H "Authorization: Token YOUR_TOKEN"

# Get all AB- requests
curl -X GET "http://localhost:8000/api/blood-requests/by_blood_type/?blood_type=AB-" \
  -H "Authorization: Token YOUR_TOKEN"
```

**Response (200 OK):**
```json
{
  "blood_type": "O+",
  "count": 3,
  "results": [
    {
      "id": 5,
      "hospital": 1,
      "hospital_name": "City General Hospital",
      "hospital_email": "contact@cityhospital.com",
      "hospital_phone": "+1-617-555-0001",
      "hospital_address": "123 Main Street",
      "blood_type": "O+",
      "units_needed": "10.00",
      "urgency_level": "critical",
      "status": "open",
      "description": "Emergency trauma surgery",
      "created_at": "2024-01-15T11:45:00Z",
      "fulfilled_at": null
    },
    {
      "id": 6,
      "hospital": 2,
      "hospital_name": "St. Mary's Hospital",
      "hospital_email": "contact@stmary.com",
      "hospital_phone": "+1-617-555-0002",
      "hospital_address": "456 Oak Ave",
      "blood_type": "O+",
      "units_needed": "5.00",
      "urgency_level": "urgent",
      "status": "open",
      "description": "Scheduled surgery",
      "created_at": "2024-01-15T10:30:00Z",
      "fulfilled_at": null
    }
  ]
}
```

---

## 4. Update Blood Request Status
**Endpoint:** `PATCH /api/blood-requests/{id}/update_status/`

**Authentication:** Required

**Description:** Update the status of a blood request.

**URL Parameters:**
- `id` (integer): Blood Request ID

**Request Body:**
```json
{
  "status": "fulfilled"
}
```

**Status Choices:**
- open: Request is still open
- fulfilled: Request has been fulfilled
- cancelled: Request has been cancelled

**Request Example:**
```bash
curl -X PATCH "http://localhost:8000/api/blood-requests/5/update_status/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "fulfilled"}'
```

**Response (200 OK):**
```json
{
  "message": "Status updated to fulfilled",
  "request": {
    "id": 5,
    "hospital": 1,
    "hospital_name": "City General Hospital",
    "hospital_email": "contact@cityhospital.com",
    "hospital_phone": "+1-617-555-0001",
    "hospital_address": "123 Main Street",
    "blood_type": "O+",
    "units_needed": "10.00",
    "urgency_level": "critical",
    "status": "fulfilled",
    "description": "Emergency trauma surgery",
    "created_at": "2024-01-15T11:45:00Z",
    "fulfilled_at": "2024-01-15T12:30:00Z"
  }
}
```

---

## Additional Blood Request Endpoints

### Get All Open Requests
**Endpoint:** `GET /api/blood-requests/open_requests/`

**Query Parameters:**
- blood_type (optional): Filter by blood type
- urgency_level (optional): Filter by urgency level
- hospital (optional): Filter by hospital ID

**Example:**
```bash
curl -X GET "http://localhost:8000/api/blood-requests/open_requests/?blood_type=O+&urgency_level=critical" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Get Critical Priority Requests
**Endpoint:** `GET /api/blood-requests/critical_requests/`

**Description:** Get all critical priority open blood requests.

**Example:**
```bash
curl -X GET "http://localhost:8000/api/blood-requests/critical_requests/" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Get Hospital-Specific Requests
**Endpoint:** `GET /api/blood-requests/hospital_requests/`

**Query Parameters:**
- hospital_id (required): Hospital ID
- status (optional): Filter by status (open, fulfilled, cancelled)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/blood-requests/hospital_requests/?hospital_id=1&status=open" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Hospital Endpoints

### Get Hospital Blood Availability
**Endpoint:** `GET /api/hospitals/{id}/blood_availability/`

**Description:** Get blood inventory for a specific hospital.

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/hospitals/1/blood_availability/" \
  -H "Authorization: Token YOUR_TOKEN"
```

**Response:**
```json
{
  "hospital": "City General Hospital",
  "inventory": [
    {
      "id": 10,
      "hospital": 1,
      "blood_type": "O+",
      "quantity": 45,
      "expiry_date": "2024-02-15",
      "last_updated": "2024-01-15T08:00:00Z"
    },
    {
      "id": 11,
      "hospital": 1,
      "blood_type": "A+",
      "quantity": 30,
      "expiry_date": "2024-02-20",
      "last_updated": "2024-01-15T08:00:00Z"
    }
  ]
}
```

### Get Hospital Blood Requests
**Endpoint:** `GET /api/hospitals/{id}/blood_requests/`

**Query Parameters:**
- status (optional): Filter by status (open, fulfilled, cancelled)

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/hospitals/1/blood_requests/?status=open" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Get Verified Hospitals
**Endpoint:** `GET /api/hospitals/verified_hospitals/`

**Description:** Get all verified hospitals in the system.

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/hospitals/verified_hospitals/" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "blood_type parameter is required"
}
```

### 404 Not Found
```json
{
  "error": "Hospital not found"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - No permission to perform action |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |

---

## Examples with Python

```python
import requests

BASE_URL = "http://localhost:8000/api"
TOKEN = "your_token_here"
HEADERS = {"Authorization": f"Token {TOKEN}"}

# Create a hospital
hospital_data = {
    "name": "Central Hospital",
    "address": "789 Park Ave",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "postal_code": "10001",
    "phone_number": "+1-212-555-0001",
    "email": "contact@central.com",
    "registration_number": "REG-NY-001"
}
response = requests.post(f"{BASE_URL}/hospitals/", json=hospital_data, headers=HEADERS)
print(response.json())

# Create a blood request
request_data = {
    "hospital": 1,
    "blood_type": "O+",
    "units_needed": "8.00",
    "urgency_level": "urgent",
    "description": "Scheduled surgery"
}
response = requests.post(f"{BASE_URL}/blood-requests/", json=request_data, headers=HEADERS)
print(response.json())

# Get open O+ requests
response = requests.get(
    f"{BASE_URL}/blood-requests/by_blood_type/?blood_type=O+",
    headers=HEADERS
)
print(response.json())

# Update request status
update_data = {"status": "fulfilled"}
response = requests.patch(
    f"{BASE_URL}/blood-requests/1/update_status/",
    json=update_data,
    headers=HEADERS
)
print(response.json())

# Get critical requests
response = requests.get(f"{BASE_URL}/blood-requests/critical_requests/", headers=HEADERS)
print(response.json())
```

---

## Examples with JavaScript/Fetch

```javascript
const BASE_URL = "http://localhost:8000/api";
const TOKEN = "your_token_here";
const headers = {
  "Authorization": `Token ${TOKEN}`,
  "Content-Type": "application/json"
};

// Create hospital
fetch(`${BASE_URL}/hospitals/`, {
  method: "POST",
  headers: headers,
  body: JSON.stringify({
    name: "Memorial Hospital",
    address: "999 Health Lane",
    city: "Los Angeles",
    state: "CA",
    country: "USA",
    postal_code: "90001",
    phone_number: "+1-213-555-0001",
    email: "contact@memorial.com",
    registration_number: "REG-CA-001"
  })
})
  .then(res => res.json())
  .then(data => console.log(data));

// Create blood request
fetch(`${BASE_URL}/blood-requests/`, {
  method: "POST",
  headers: headers,
  body: JSON.stringify({
    hospital: 1,
    blood_type: "AB-",
    units_needed: "5.00",
    urgency_level: "critical",
    description: "Rare blood type emergency"
  })
})
  .then(res => res.json())
  .then(data => console.log(data));

// Get O+ blood requests
fetch(`${BASE_URL}/blood-requests/by_blood_type/?blood_type=O+`, { headers })
  .then(res => res.json())
  .then(data => console.log(data));

// Update request status
fetch(`${BASE_URL}/blood-requests/1/update_status/`, {
  method: "PATCH",
  headers: headers,
  body: JSON.stringify({ status: "fulfilled" })
})
  .then(res => res.json())
  .then(data => console.log(data));
```
