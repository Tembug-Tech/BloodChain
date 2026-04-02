# BloodChain API Documentation

## Table of Contents
1. [Authentication](#authentication)
2. [Base URL](#base-url)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [Endpoints](#endpoints)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)

---

## Authentication

All API endpoints (except login/token generation) require authentication using a Bearer token.

### Get Authentication Token

**Endpoint:** `POST /api-token-auth/`

Request:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Response (200 OK):
```json
{
  "token": "abc123def456..."
}
```

### Using the Token

Include the token in the `Authorization` header:

```bash
Authorization: Token abc123def456...
```

Or with Bearer prefix:
```bash
Authorization: Bearer abc123def456...
```

---

## Base URL

```
http://localhost:8000/api
```

For production:
```
https://your-domain.com/api
```

---

## Response Format

All responses are in JSON format.

### Success Response (2xx)
```json
{
  "data": { ... },
  "message": "Operation successful",
  "status": 200
}
```

### Error Response (4xx, 5xx)
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "status": 400
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created |
| 204 | No Content | Successful deletion |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Server error |

### Common Error Codes

- `INVALID_TOKEN`: Authentication token is invalid or expired
- `REQUIRED_FIELD_MISSING`: Required field is missing in request
- `INVALID_DATA`: Data validation failed
- `RESOURCE_NOT_FOUND`: Requested resource does not exist
- `BLOCKCHAIN_ERROR`: Blockchain operation failed
- `NETWORK_ERROR`: Network connectivity issue

---

## Endpoints

---

## Blood Unit Endpoints

### 1. Create Blood Unit
**POST** `/api/blood-tracking/units/`

Creates a new blood unit record in the system.

**Authentication:** Required (Token)

**Request Body:**
```json
{
  "donor": 1,
  "blood_type": "O+",
  "collection_date": "2026-04-02T10:30:00Z",
  "expiry_date": "2026-05-02T10:30:00Z",
  "current_location": null,
  "hiv_test": false,
  "hepatitis_test": false
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "unit_id": "550e8400-e29b-41d4-a716-446655440000",
  "donor": 1,
  "donor_name": "John Doe",
  "blood_type": "O+",
  "donor_blood_type": "O+",
  "collection_date": "2026-04-02T10:30:00Z",
  "expiry_date": "2026-05-02T10:30:00Z",
  "current_location": null,
  "hospital_name": null,
  "status": "collected",
  "hiv_test": false,
  "hepatitis_test": false,
  "blockchain_tx_hash": null,
  "created_at": "2026-04-02T10:30:00Z",
  "updated_at": "2026-04-02T10:30:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "expiry_date": ["Expiry date must be after collection date"]
}
```

---

### 2. List All Blood Units
**GET** `/api/blood-tracking/units/`

Retrieves all blood units with pagination and filtering options.

**Authentication:** Required (Token)

**Query Parameters:**
- `search` - Search by unit_id, donor name, or blood type
- `ordering` - Order by: `collection_date`, `expiry_date`, `-collection_date`, `-expiry_date`
- `page` - Page number (default: 1)

**Example:**
```bash
GET /api/blood-tracking/units/?blood_type=O+&ordering=-collection_date&page=1
```

**Response (200 OK):**
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/blood-tracking/units/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "unit_id": "550e8400-e29b-41d4-a716-446655440000",
      "donor": 1,
      "donor_name": "John Doe",
      "blood_type": "O+",
      "collection_date": "2026-04-02T10:30:00Z",
      "expiry_date": "2026-05-02T10:30:00Z",
      "current_location": null,
      "status": "collected",
      "created_at": "2026-04-02T10:30:00Z",
      "updated_at": "2026-04-02T10:30:00Z"
    }
  ]
}
```

---

### 3. Get Blood Unit Details
**GET** `/api/blood-tracking/units/{id}/`

Retrieves detailed information about a specific blood unit including full lifecycle history.

**Authentication:** Required (Token)

**Response (200 OK):**
```json
{
  "id": 1,
  "unit_id": "550e8400-e29b-41d4-a716-446655440000",
  "donor": 1,
  "donor_info": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "blood_type": "O+",
    "location": "Boston, MA",
    "phone": "+1-617-555-0001"
  },
  "blood_type": "O+",
  "collection_date": "2026-04-02T10:30:00Z",
  "expiry_date": "2026-05-02T10:30:00Z",
  "current_location": 1,
  "location_info": {
    "id": 1,
    "name": "Central Hospital",
    "email": "admin@central.com",
    "phone": "+1-617-555-0100",
    "address": "123 Hospital Ave",
    "city": "Boston",
    "state": "MA"
  },
  "status": "storage",
  "hiv_test": true,
  "hepatitis_test": true,
  "blockchain_tx_hash": "0x1234567890abcdef...",
  "status_history": [
    {
      "previous_status": "collected",
      "new_status": "testing",
      "timestamp": "2026-04-02T11:00:00Z",
      "notes": "Lab testing initiated"
    },
    {
      "previous_status": "testing",
      "new_status": "storage",
      "timestamp": "2026-04-03T09:00:00Z",
      "notes": "Tests passed, moved to storage"
    }
  ],
  "lifecycle_summary": {
    "initial_status": "collected",
    "current_status": "storage",
    "status_changes": [
      {
        "previous_status": "collected",
        "new_status": "testing",
        "timestamp": "2026-04-02T11:00:00Z",
        "notes": "Lab testing initiated"
      },
      {
        "previous_status": "testing",
        "new_status": "storage",
        "timestamp": "2026-04-03T09:00:00Z",
        "notes": "Tests passed, moved to storage"
      }
    ],
    "total_changes": 2,
    "days_in_storage": 30,
    "is_expired": false
  },
  "created_at": "2026-04-02T10:30:00Z",
  "updated_at": "2026-04-03T09:00:00Z"
}
```

---

### 4. Update Blood Unit Status
**PATCH** `/api/blood-tracking/units/{id}/update_status/`

Updates the status of a blood unit and records the status change in history.

**Authentication:** Required (Token)

**Request Body:**
```json
{
  "status": "storage",
  "current_location": 1,
  "blockchain_tx_hash": "0x...",
  "notes": "Tests completed, unit ready for storage"
}
```

**Response (200 OK):**
```json
{
  "message": "Blood unit status updated from testing to storage",
  "unit": {
    "id": 1,
    "unit_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "storage",
    "status_history": [
      {
        "previous_status": "testing",
        "new_status": "storage",
        "timestamp": "2026-04-03T09:00:00Z",
        "notes": "Tests completed, unit ready for storage"
      }
    ],
    "current_location": 1,
    "blockchain_tx_hash": "0x...",
    "updated_at": "2026-04-03T09:00:00Z"
  }
}
```

**Error (400 Bad Request):**
```json
{
  "error": "Invalid status value"
}
```

---

### 5. Get Blood Unit Lifecycle History
**GET** `/api/blood-tracking/units/{id}/lifecycle_history/`

Retrieves the complete lifecycle history of a specific blood unit.

**Authentication:** Required (Token)

**Response (200 OK):**
```json
{
  "unit_id": "550e8400-e29b-41d4-a716-446655440000",
  "donor": "John Doe",
  "blood_type": "O+",
  "collection_date": "2026-04-02T10:30:00Z",
  "expiry_date": "2026-05-02T10:30:00Z",
  "lifecycle_history": {
    "initial_status": "collected",
    "current_status": "storage",
    "status_changes": [
      {
        "previous_status": "collected",
        "new_status": "testing",
        "timestamp": "2026-04-02T11:00:00Z",
        "notes": "Lab testing initiated"
      },
      {
        "previous_status": "testing",
        "new_status": "storage",
        "timestamp": "2026-04-03T09:00:00Z",
        "notes": "Tests passed, moved to storage"
      }
    ],
    "total_changes": 2,
    "days_in_storage": 30,
    "is_expired": false
  },
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
        "timestamp": "2026-04-03T09:00:00Z",
        "notes": "Tests passed, moved to storage"
      }
    ]
  },
  "tests": {
    "hiv_test": true,
    "hepatitis_test": true
  },
  "blockchain_tx_hash": "0x1234567890abcdef...",
  "created_at": "2026-04-02T10:30:00Z",
  "updated_at": "2026-04-03T09:00:00Z"
}
```

---

### 6. List Available Units by Blood Type
**GET** `/api/blood-tracking/units/by_blood_type/`

Retrieves available blood units filtered by blood type (only units in storage).

**Authentication:** Required (Token)

**Query Parameters:**
- `blood_type` (required) - Blood type: O+, O-, A+, A-, B+, B-, AB+, AB-

**Example:**
```bash
GET /api/blood-tracking/units/by_blood_type/?blood_type=O+
```

**Response (200 OK):**
```json
{
  "blood_type": "O+",
  "count": 15,
  "results": [
    {
      "id": 1,
      "unit_id": "550e8400-e29b-41d4-a716-446655440000",
      "donor": 1,
      "donor_name": "John Doe",
      "blood_type": "O+",
      "collection_date": "2026-04-02T10:30:00Z",
      "expiry_date": "2026-05-02T10:30:00Z",
      "current_location": 1,
      "hospital_name": "Central Hospital",
      "status": "storage",
      "created_at": "2026-04-02T10:30:00Z",
      "updated_at": "2026-04-03T09:00:00Z"
    },
    {
      "id": 2,
      "unit_id": "660e8400-e29b-41d4-a716-446655440001",
      "donor": 2,
      "donor_name": "Jane Smith",
      "blood_type": "O+",
      "collection_date": "2026-03-30T14:20:00Z",
      "expiry_date": "2026-04-29T14:20:00Z",
      "current_location": 1,
      "hospital_name": "Central Hospital",
      "status": "storage",
      "created_at": "2026-03-30T14:20:00Z",
      "updated_at": "2026-03-31T10:00:00Z"
    }
  ]
}
```

**Error (400 Bad Request):**
```json
{
  "error": "blood_type parameter is required"
}
```

---

### 7. Get All Available Units in Storage
**GET** `/api/blood-tracking/units/available_units/`

Retrieves all blood units currently in storage status.

**Authentication:** Required (Token)

**Response (200 OK):**
```json
{
  "count": 42,
  "results": [
    {
      "id": 1,
      "unit_id": "550e8400-e29b-41d4-a716-446655440000",
      "donor": 1,
      "donor_name": "John Doe",
      "blood_type": "O+",
      "collection_date": "2026-04-02T10:30:00Z",
      "expiry_date": "2026-05-02T10:30:00Z",
      "current_location": 1,
      "hospital_name": "Central Hospital",
      "status": "storage",
      "hiv_test": true,
      "hepatitis_test": true,
      "created_at": "2026-04-02T10:30:00Z",
      "updated_at": "2026-04-03T09:00:00Z"
    }
  ]
}
```

---

### 8. Get Units at Specific Location
**GET** `/api/blood-tracking/units/units_at_location/`

Retrieves blood units stored at a specific hospital location.

**Authentication:** Required (Token)

**Query Parameters:**
- `location_id` (required) - Hospital ID

**Example:**
```bash
GET /api/blood-tracking/units/units_at_location/?location_id=1
```

**Response (200 OK):**
```json
{
  "location_id": "1",
  "count": 28,
  "results": [
    {
      "id": 1,
      "unit_id": "550e8400-e29b-41d4-a716-446655440000",
      "donor": 1,
      "donor_name": "John Doe",
      "blood_type": "O+",
      "collection_date": "2026-04-02T10:30:00Z",
      "expiry_date": "2026-05-02T10:30:00Z",
      "current_location": 1,
      "hospital_name": "Central Hospital",
      "status": "storage",
      "created_at": "2026-04-02T10:30:00Z",
      "updated_at": "2026-04-03T09:00:00Z"
    }
  ]
}
```

---

### 9. Get Units Expiring Soon
**GET** `/api/blood-tracking/units/near_expiry/`

Retrieves blood units that are expiring within 7 days.

**Authentication:** Required (Token)

**Response (200 OK):**
```json
{
  "threshold_days": 7,
  "count": 5,
  "results": [
    {
      "id": 15,
      "unit_id": "770e8400-e29b-41d4-a716-446655440005",
      "donor": 5,
      "donor_name": "Alice Johnson",
      "blood_type": "A+",
      "collection_date": "2026-03-06T08:30:00Z",
      "expiry_date": "2026-04-05T08:30:00Z",
      "current_location": 1,
      "hospital_name": "Central Hospital",
      "status": "storage",
      "created_at": "2026-03-06T08:30:00Z",
      "updated_at": "2026-03-07T10:00:00Z"
    }
  ]
}
```

---

### 10. Update Blood Unit (Partial)
**PATCH** `/api/blood-tracking/units/{id}/`

Updates one or more fields of a blood unit.

**Authentication:** Required (Token)

**Request Body:**
```json
{
  "current_location": 2,
  "status": "transfused"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "unit_id": "550e8400-e29b-41d4-a716-446655440000",
  "donor": 1,
  "donor_name": "John Doe",
  "blood_type": "O+",
  "collection_date": "2026-04-02T10:30:00Z",
  "expiry_date": "2026-05-02T10:30:00Z",
  "current_location": 2,
  "hospital_name": "Emergency Hospital",
  "status": "transfused",
  "hiv_test": true,
  "hepatitis_test": true,
  "blockchain_tx_hash": null,
  "created_at": "2026-04-02T10:30:00Z",
  "updated_at": "2026-04-03T14:30:00Z"
}
```

---

### 11. Delete Blood Unit
**DELETE** `/api/blood-tracking/units/{id}/`

Deletes a blood unit record.

**Authentication:** Required (Token)

**Response (204 No Content)**

---

## Blood Donation Endpoints

### List Blood Donations
**GET** `/api/blood-tracking/donations/`

Retrieves all blood donation records.

**Query Parameters:**
- `search` - Search by donor name or hospital name
- `ordering` - Order by: `donation_date`, `-donation_date`, `created_at`

**Response (200 OK):**
```json
{
  "count": 30,
  "results": [
    {
      "id": 1,
      "donor": 1,
      "donor_name": "John Doe",
      "blood_type": "O+",
      "hospital": 1,
      "hospital_name": "Central Hospital",
      "donation_date": "2026-04-02T10:30:00Z",
      "status": "completed",
      "blood_units": "0.45",
      "blockchain_hash": null,
      "notes": "",
      "created_at": "2026-04-02T10:30:00Z",
      "updated_at": "2026-04-02T10:30:00Z"
    }
  ]
}
```

---

### Get My Donations
**GET** `/api/blood-tracking/donations/my_donations/`

Retrieves all donations for the authenticated donor.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "donor": 1,
    "donor_name": "John Doe",
    "blood_type": "O+",
    "hospital": 1,
    "hospital_name": "Central Hospital",
    "donation_date": "2026-04-02T10:30:00Z",
    "status": "completed",
    "blood_units": "0.45",
    "created_at": "2026-04-02T10:30:00Z"
  }
]
```

---

## Blood Transfer Endpoints

### List Blood Transfers
**GET** `/api/blood-tracking/transfers/`

Retrieves all blood transfer records.

**Query Parameters:**
- `search` - Search by hospital names
- `ordering` - Order by: `transfer_date`, `created_at`

**Response (200 OK):**
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "donation": 1,
      "donation_info": {...},
      "from_hospital": 1,
      "from_hospital_name": "Central Hospital",
      "to_hospital": 2,
      "to_hospital_name": "Emergency Hospital",
      "transfer_type": "hospital_to_hospital",
      "status": "received",
      "transfer_date": "2026-04-02T10:30:00Z",
      "received_date": "2026-04-02T11:30:00Z",
      "blockchain_hash": null,
      "notes": "",
      "created_at": "2026-04-02T10:30:00Z",
      "updated_at": "2026-04-02T11:30:00Z"
    }
  ]
}
```

---

### Get Pending Transfers
**GET** `/api/blood-tracking/transfers/pending_transfers/`

Retrieves all pending blood transfer records.

**Response (200 OK):**
```json
[
  {
    "id": 5,
    "donation": 5,
    "from_hospital": 1,
    "from_hospital_name": "Central Hospital",
    "to_hospital": 3,
    "to_hospital_name": "City Hospital",
    "transfer_type": "hospital_to_hospital",
    "status": "pending",
    "transfer_date": "2026-04-02T15:00:00Z",
    "received_date": null,
    "created_at": "2026-04-02T15:00:00Z"
  }
]
```

---

### Mark Transfer as Received
**POST** `/api/blood-tracking/transfers/{id}/mark_received/`

Marks a pending transfer as received.

**Response (200 OK):**
```json
{
  "id": 5,
  "status": "received",
  "received_date": "2026-04-02T15:30:00Z",
  "updated_at": "2026-04-02T15:30:00Z"
}
```

---

## Error Handling

### Common Errors

**401 Unauthorized - Missing Authentication:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**400 Bad Request - Missing Required Parameter:**
```json
{
  "error": "blood_type parameter is required"
}
```

**404 Not Found - Resource Not Found:**
```json
{
  "detail": "Not found."
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Status Codes Reference

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 204 | No Content - Successful delete |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error - Unexpected error |

---

## Blood Unit Status Reference

| Status | Description |
|--------|-------------|
| `collected` | Blood unit initially collected from donor |
| `testing` | Unit undergoing laboratory testing |
| `storage` | Unit passed tests, in cold storage |
| `transfused` | Blood transfused to patient |
| `expired` | Unit has expired (past expiry date) |

---

## Authentication

All endpoints require token-based authentication. Include the token in the Authorization header:

```bash
Authorization: Token YOUR_TOKEN_HERE
```

**Get Token:**
```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

---

## Rate Limiting

Currently no rate limiting is implemented. This may be added in future versions.

---

## Pagination

List endpoints return paginated results with 10 items per page:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/blood-tracking/units/?page=2",
  "previous": null,
  "results": [...]
}
```

Use `?page=N` to navigate pages.

---

## Examples

### Create a Blood Unit

**cURL:**
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

**Python:**
```python
import requests

url = "http://localhost:8000/api/blood-tracking/units/"
token = "your_token_here"
headers = {"Authorization": f"Token {token}"}

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

**JavaScript:**
```javascript
const token = "your_token_here";
const unit_data = {
  donor: 1,
  blood_type: "O+",
  collection_date: "2026-04-02T10:30:00Z",
  expiry_date: "2026-05-02T10:30:00Z",
  hiv_test: false,
  hepatitis_test: false
};

fetch('http://localhost:8000/api/blood-tracking/units/', {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(unit_data)
})
.then(res => res.json())
.then(data => console.log(data));
```

---

### List Available O+ Units

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/blood-tracking/units/by_blood_type/?blood_type=O+" \
  -H "Authorization: Token YOUR_TOKEN"
```

**Python:**
```python
import requests

url = "http://localhost:8000/api/blood-tracking/units/by_blood_type/"
params = {"blood_type": "O+"}
token = "your_token_here"
headers = {"Authorization": f"Token {token}"}

response = requests.get(url, params=params, headers=headers)
units = response.json()
print(f"Available O+ units: {units['count']}")
for unit in units['results']:
    print(f"  - {unit['unit_id']}: {unit['donor_name']}")
```

---

### Update Blood Unit Status to Storage

**cURL:**
```bash
curl -X PATCH "http://localhost:8000/api/blood-tracking/units/1/update_status/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "storage",
    "current_location": 1,
    "notes": "Tests passed, moved to cold storage"
  }'
```

---

### Get Blood Unit Lifecycle History

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/blood-tracking/units/1/lifecycle_history/" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Filtering & Search

### Filter By Blood Type
```bash
GET /api/blood-tracking/units/?search=O+
```

### Order By Collection Date (Newest First)
```bash
GET /api/blood-tracking/units/?ordering=-collection_date
```

### Search By Donor Name
```bash
GET /api/blood-tracking/units/?search=John
```

---

## Webhooks

Webhooks are not currently implemented but are planned for future versions to notify external systems of:
- New blood unit created
- Blood unit status changed
- Blood unit expiring soon
- Blood transfusion completed

---

**API Version:** 1.0  
**Last Updated:** 2026-04-02

For more help, see QUICK_REFERENCE.md
