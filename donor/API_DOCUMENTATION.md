# Donor API Documentation

## Base URL
```
http://localhost:8000/api/donors/
```

## Endpoints

### 1. Register a New Donor
**Endpoint:** `POST /api/donors/register/`

**Authentication:** Not required

**Description:** Register a new donor with user account creation.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "blood_type": "O+",
  "phone_number": "+1-555-0123",
  "location": "New York, NY",
  "date_of_birth": "1990-01-15",
  "is_available": true,
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f42bE"
}
```

**Field Details:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | Unique username (max 150 chars) |
| email | email | Yes | Valid email address |
| password | string | Yes | Secure password (min 8 chars recommended) |
| first_name | string | No | User's first name |
| last_name | string | No | User's last name |
| blood_type | string | Yes | Blood type: A+, A-, B+, B-, AB+, AB-, O+, O- |
| phone_number | string | Yes | Contact phone (max 15 chars) |
| location | string | Yes | Location (city, state/region) |
| date_of_birth | date | Yes | Date of birth (YYYY-MM-DD format) |
| is_available | boolean | No | Availability status (default: true) |
| wallet_address | string | No | Ethereum wallet address for rewards |

**Response (201 Created):**
```json
{
  "message": "Donor registered successfully",
  "donor": {
    "id": 1,
    "user": {
      "id": 5,
      "username": "john_doe",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com"
    },
    "blood_type": "O+",
    "phone_number": "+1-555-0123",
    "location": "New York, NY",
    "date_of_birth": "1990-01-15",
    "is_available": true,
    "last_donation_date": null,
    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f42bE",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses:**
- 400 Bad Request: Invalid data or username/email already exists
- 400 Bad Request: Missing required fields

---

### 2. Get My Donor Profile
**Endpoint:** `GET /api/donors/my_profile/`

**Authentication:** Required (JWT Token or Session)

**Description:** Retrieve the authenticated user's donor profile.

**Request:**
```bash
curl -X GET http://localhost:8000/api/donors/my_profile/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user": {
    "id": 5,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  },
  "blood_type": "O+",
  "phone_number": "+1-555-0123",
  "location": "New York, NY",
  "date_of_birth": "1990-01-15",
  "is_available": true,
  "last_donation_date": null,
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f42bE",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- 404 Not Found: Donor profile not found
- 401 Unauthorized: Missing or invalid authentication

---

### 3. Update Donor Availability
**Endpoint:** `PATCH /api/donors/{id}/update_availability/`

**Authentication:** Required

**Description:** Update the availability status of a donor. Users can only update their own availability.

**URL Parameters:**
- `id` (integer): Donor ID

**Request Body:**
```json
{
  "is_available": false
}
```

**Request Example:**
```bash
curl -X PATCH http://localhost:8000/api/donors/1/update_availability/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"is_available": false}'
```

**Response (200 OK):**
```json
{
  "message": "Availability updated to false",
  "donor": {
    "id": 1,
    "user": {
      "id": 5,
      "username": "john_doe",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com"
    },
    "blood_type": "O+",
    "phone_number": "+1-555-0123",
    "location": "New York, NY",
    "date_of_birth": "1990-01-15",
    "is_available": false,
    "last_donation_date": null,
    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f42bE",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```

**Error Responses:**
- 400 Bad Request: Missing is_available parameter
- 403 Forbidden: Cannot update another user's availability
- 404 Not Found: Donor not found
- 401 Unauthorized: Missing or invalid authentication

---

### 4. List Available Donors
**Endpoint:** `GET /api/donors/available/`

**Authentication:** Required

**Description:** List all available donors with optional filtering by blood type and location.

**Query Parameters:**

| Parameter | Type | Optional | Description |
|-----------|------|----------|-------------|
| blood_type | string | Yes | Filter by blood type (A+, A-, B+, B-, AB+, AB-, O+, O-) |
| location | string | Yes | Filter by location (case-insensitive partial match) |

**Request Examples:**
```bash
# Get all available donors
curl -X GET http://localhost:8000/api/donors/available/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Filter by blood type
curl -X GET "http://localhost:8000/api/donors/available/?blood_type=O+" \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Filter by location
curl -X GET "http://localhost:8000/api/donors/available/?location=New York" \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Filter by both blood type and location
curl -X GET "http://localhost:8000/api/donors/available/?blood_type=A%2B&location=California" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Response (200 OK):**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 5,
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
      },
      "blood_type": "O+",
      "phone_number": "+1-555-0123",
      "location": "New York, NY",
      "date_of_birth": "1990-01-15",
      "is_available": true,
      "last_donation_date": null,
      "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f42bE",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "user": {
        "id": 6,
        "username": "jane_smith",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com"
      },
      "blood_type": "O+",
      "phone_number": "+1-555-0124",
      "location": "New York, NY",
      "date_of_birth": "1985-05-20",
      "is_available": true,
      "last_donation_date": "2023-12-10T14:00:00Z",
      "wallet_address": "0x8ba1f109551bD432803012645Ac136ddd64DBA72",
      "created_at": "2024-01-10T08:15:00Z",
      "updated_at": "2024-01-10T08:15:00Z"
    }
  ]
}
```

---

### 5. Get Available Donors by Blood Type
**Endpoint:** `GET /api/donors/by_blood_type/`

**Authentication:** Required

**Description:** Get all available donors filtering by blood type.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| blood_type | string | Yes | Blood type filter (A+, A-, B+, B-, AB+, AB-, O+, O-) |

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/donors/by_blood_type/?blood_type=AB-" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Response (200 OK):**
```json
{
  "blood_type": "AB-",
  "count": 1,
  "results": [
    {
      "id": 3,
      "user": {
        "id": 7,
        "username": "michael_brown",
        "first_name": "Michael",
        "last_name": "Brown",
        "email": "michael@example.com"
      },
      "blood_type": "AB-",
      "phone_number": "+1-555-0125",
      "location": "Los Angeles, CA",
      "date_of_birth": "1988-03-12",
      "is_available": true,
      "last_donation_date": "2024-01-05T09:30:00Z",
      "wallet_address": "0x9F8F72aA9304c8B593d555F12eF6589cC3A579A2",
      "created_at": "2024-01-12T11:45:00Z",
      "updated_at": "2024-01-12T11:45:00Z"
    }
  ]
}
```

**Error Responses:**
- 400 Bad Request: Missing blood_type parameter

---

## Authentication

All protected endpoints require authentication via:

### Token Authentication
```bash
curl -X GET http://localhost:8000/api/donors/my_profile/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Session Authentication
Include credentials when making requests:
```bash
curl -X GET http://localhost:8000/api/donors/my_profile/ \
  -b "sessionid=YOUR_SESSION_ID"
```

### Obtaining a Token
```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "securepassword123"}'
```

Response:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

---

## Common HTTP Status Codes

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

BASE_URL = "http://localhost:8000/api/donors"
TOKEN = "your_token_here"
HEADERS = {"Authorization": f"Token {TOKEN}"}

# Get my profile
response = requests.get(f"{BASE_URL}/my_profile/", headers=HEADERS)
print(response.json())

# Get available donors by blood type
response = requests.get(
    f"{BASE_URL}/available/",
    params={"blood_type": "O+", "location": "New York"},
    headers=HEADERS
)
print(response.json())

# Update availability
response = requests.patch(
    f"{BASE_URL}/1/update_availability/",
    json={"is_available": False},
    headers=HEADERS
)
print(response.json())
```

---

## Examples with JavaScript/Fetch

```javascript
const BASE_URL = "http://localhost:8000/api/donors";
const TOKEN = "your_token_here";
const headers = {
  "Authorization": `Token ${TOKEN}`,
  "Content-Type": "application/json"
};

// Get my profile
fetch(`${BASE_URL}/my_profile/`, { headers })
  .then(res => res.json())
  .then(data => console.log(data));

// Register new donor
fetch(`${BASE_URL}/register/`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "new_donor",
    email: "donor@example.com",
    password: "secure123",
    blood_type: "O+",
    phone_number: "+1-555-0126",
    location: "Boston, MA",
    date_of_birth: "1992-07-22"
  })
})
  .then(res => res.json())
  .then(data => console.log(data));

// Get available donors
fetch(`${BASE_URL}/available/?blood_type=AB-`, { headers })
  .then(res => res.json())
  .then(data => console.log(data));
```
