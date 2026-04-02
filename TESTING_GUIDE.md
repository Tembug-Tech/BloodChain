# BloodChain Testing Guide

Comprehensive guide for testing the BloodChain API and blockchain integration.

---

## Table of Contents

1. [Unit Tests](#unit-tests)
2. [Integration Tests](#integration-tests)
3. [API Testing](#api-testing)
4. [Blockchain Testing](#blockchain-testing)
5. [Load Testing](#load-testing)
6. [Security Testing](#security-testing)
7. [Automation](#automation)

---

## Unit Tests

### Running Unit Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test blood_tracking
python manage.py test donor
python manage.py test hospital

# Run specific test class
python manage.py test blood_tracking.tests.BloodUnitModelTest

# Run specific test method
python manage.py test blood_tracking.tests.BloodUnitModelTest.test_unit_creation

# Verbose output
python manage.py test --verbosity=2

# Keep test database
python manage.py test --keepdb
```

### Example Unit Test

Create `blood_tracking/tests.py`:

```python
from django.test import TestCase
from blood_tracking.models import BloodUnit
from donor.models import Donor
from datetime import datetime, timedelta

class BloodUnitModelTest(TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.donor = Donor.objects.create(
            name="Test Donor",
            email="donor@test.com",
            blood_type="O+",
            phone="+1234567890"
        )
    
    def test_unit_creation(self):
        """Test creating a blood unit"""
        unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type="O+",
            collected_at=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=35)
        )
        self.assertEqual(unit.blood_type, "O+")
        self.assertEqual(unit.status, "collected")
    
    def test_unit_status_update(self):
        """Test updating unit status"""
        unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type="O+",
            collected_at=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=35)
        )
        unit.status = "testing"
        unit.save()
        
        unit.refresh_from_db()
        self.assertEqual(unit.status, "testing")
    
    def test_unit_expiry(self):
        """Test unit expiry logic"""
        yesterday = datetime.now() - timedelta(days=1)
        unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type="O+",
            collected_at=yesterday,
            expiry_date=yesterday
        )
        self.assertTrue(unit.is_expired)
    
    def test_unit_str(self):
        """Test unit string representation"""
        unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type="O+",
            collected_at=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=35)
        )
        self.assertIn("O+", str(unit))
```

---

## Integration Tests

### API Integration Tests

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from blood_tracking.models import BloodUnit
from donor.models import Donor
from datetime import datetime, timedelta
import json

class BloodTrackingAPITest(TestCase):
    
    def setUp(self):
        """Set up test client and fixtures"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Get token
        response = self.client.post(
            '/api-token-auth/',
            {'username': 'testuser', 'password': 'testpass123'},
            content_type='application/json'
        )
        self.token = response.json()['token']
        self.headers = {'HTTP_AUTHORIZATION': f'Token {self.token}'}
        
        # Create test donor
        self.donor = Donor.objects.create(
            name="Test Donor",
            email="donor@test.com",
            blood_type="O+",
            phone="+1234567890"
        )
    
    def test_register_blood_unit(self):
        """Test registering a blood unit via API"""
        data = {
            'donor': self.donor.id,
            'blood_type': 'O+',
            'collected_at': datetime.now().isoformat() + 'Z',
            'expiry_date': (datetime.now() + timedelta(days=35)).isoformat() + 'Z',
        }
        
        response = self.client.post(
            '/api/blood-tracking/units/register/',
            json.dumps(data),
            content_type='application/json',
            **self.headers
        )
        
        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertEqual(result['blood_type'], 'O+')
    
    def test_get_blood_unit(self):
        """Test retrieving a blood unit"""
        unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type="O+",
            collected_at=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=35)
        )
        
        response = self.client.get(
            f'/api/blood-tracking/units/{unit.id}/',
            **self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['unit_id'], str(unit.unit_id))
    
    def test_list_blood_units(self):
        """Test listing blood units"""
        BloodUnit.objects.create(
            donor=self.donor,
            blood_type="O+",
            collected_at=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=35)
        )
        
        response = self.client.get(
            '/api/blood-tracking/units/',
            **self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertGreater(result['count'], 0)
    
    def test_update_unit_status(self):
        """Test updating blood unit status"""
        unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type="O+",
            collected_at=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=35)
        )
        
        data = {'status': 'testing', 'notes': 'Lab testing'}
        
        response = self.client.patch(
            f'/api/blood-tracking/units/{unit.id}/update_blockchain_status/',
            json.dumps(data),
            content_type='application/json',
            **self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['unit']['status'], 'testing')
```

### Run Integration Tests

```bash
# Run integration tests only
python manage.py test blood_tracking.tests.BloodTrackingAPITest

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

---

## API Testing

### Using Postman

1. **Import API Collection:**
   - Download collection from `docs/postman_collection.json`
   - Import into Postman
   - Set base URL and token in variables

2. **Test Authentication:**

```bash
POST {{base_url}}/api-token-auth/
Content-Type: application/json

{
  "username": "testuser",
  "password": "testpass123"
}
```

3. **Test Blood Unit Registration:**

```bash
POST {{base_url}}/api/blood-tracking/units/register/
Authorization: Token {{token}}
Content-Type: application/json

{
  "donor": 1,
  "blood_type": "O+",
  "collected_at": "{{timestamp}}",
  "expiry_date": "{{timestamp_plus_35_days}}"
}
```

### Using cURL

Create test script `test_api.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# Get token
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/api-token-auth/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }')

TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.token')
echo "Token: $TOKEN"

# Create blood unit
UNIT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/blood-tracking/units/register/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "donor": 1,
    "blood_type": "O+",
    "collected_at": "2026-04-02T10:30:00Z",
    "expiry_date": "2026-05-02T10:30:00Z"
  }')

UNIT_ID=$(echo $UNIT_RESPONSE | jq -r '.id')
echo "Created unit: $UNIT_ID"

# Get unit details
curl -s -X GET "$BASE_URL/api/blood-tracking/units/$UNIT_ID/" \
  -H "Authorization: Token $TOKEN" | jq .

# Update status
curl -s -X PATCH "$BASE_URL/api/blood-tracking/units/$UNIT_ID/update_blockchain_status/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "testing",
    "notes": "Lab testing"
  }' | jq .

# Get blockchain history
curl -s -X GET "$BASE_URL/api/blood-tracking/units/$UNIT_ID/blockchain_history/" \
  -H "Authorization: Token $TOKEN" | jq .
```

Run tests:

```bash
chmod +x test_api.sh
./test_api.sh
```

### Using Python Requests

Create `test_api.py`:

```python
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_authentication():
    """Test getting auth token"""
    response = requests.post(
        f"{BASE_URL}/api-token-auth/",
        json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    return response.json()['token']

def test_create_blood_unit(token):
    """Test creating a blood unit"""
    headers = {"Authorization": f"Token {token}"}
    
    data = {
        "donor": 1,
        "blood_type": "O+",
        "collected_at": datetime.now().isoformat() + "Z",
        "expiry_date": (datetime.now() + timedelta(days=35)).isoformat() + "Z"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/blood-tracking/units/register/",
        headers=headers,
        json=data
    )
    
    assert response.status_code == 201
    return response.json()

def test_get_blood_unit(token, unit_id):
    """Test retrieving a blood unit"""
    headers = {"Authorization": f"Token {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/blood-tracking/units/{unit_id}/",
        headers=headers
    )
    
    assert response.status_code == 200
    return response.json()

def test_workflow(token):
    """Test complete workflow"""
    print("1. Creating blood unit...")
    unit = test_create_blood_unit(token)
    print(f"✓ Created unit: {unit['unit_id']}")
    
    print("2. Getting unit details...")
    details = test_get_blood_unit(token, unit['id'])
    print(f"✓ Unit status: {details['status']}")
    
    print("3. Updating status...")
    headers = {"Authorization": f"Token {token}"}
    response = requests.patch(
        f"{BASE_URL}/api/blood-tracking/units/{unit['id']}/update_blockchain_status/",
        headers=headers,
        json={"status": "testing", "notes": "Testing"}
    )
    assert response.status_code == 200
    print("✓ Status updated")
    
    print("4. Getting blockchain history...")
    response = requests.get(
        f"{BASE_URL}/api/blood-tracking/units/{unit['id']}/blockchain_history/",
        headers=headers
    )
    assert response.status_code == 200
    print("✓ Blockchain data retrieved")

if __name__ == "__main__":
    token = test_authentication()
    print("✓ Authenticated")
    test_workflow(token)
    print("\n✓ All tests passed!")
```

Run:

```bash
python test_api.py
```

---

## Blockchain Testing

### Test Blockchain Connection

```python
from blood_tracking.blockchain_service import get_blockchain_service

def test_blockchain_connection():
    """Test blockchain connectivity"""
    service = get_blockchain_service()
    
    if service.is_connected:
        print("✓ Connected to Sepolia testnet")
        
        # Get chain info
        chain_id = service.web3.eth.chain_id
        print(f"✓ Chain ID: {chain_id}")
        
        # Get latest block
        block = service.web3.eth.get_block('latest')
        print(f"✓ Latest block: {block['number']}")
    else:
        print("✗ Failed to connect to testnet")

# Run in Django shell
python manage.py shell < test_blockchain.py
```

### Test Blockchain Transactions

```python
from blood_tracking.blockchain_service import get_blockchain_service

def test_record_blood_unit():
    """Test recording blood unit on blockchain"""
    service = get_blockchain_service()
    
    result = service.record_blood_unit_on_chain(
        unit_id="550e8400-e29b-41d4-a716-446655440000",
        blood_type="O+",
        donor_wallet="0x742d35Cc6634C0532925a3b844Bc9e7595f36bEd"
    )
    
    if result['success']:
        print(f"✓ Unit recorded: {result['tx_hash']}")
        print(f"  Network: {result['network']}")
        print(f"  Timestamp: {result['timestamp']}")
    else:
        print(f"✗ Failed: {result['error']}")

def test_verify_transaction():
    """Test verifying a transaction"""
    service = get_blockchain_service()
    
    tx_hash = "0x..."  # Use actual hash
    is_valid = service.verify_tx_on_chain(tx_hash)
    
    if is_valid:
        print(f"✓ Transaction verified: {tx_hash}")
    else:
        print(f"✗ Transaction not found: {tx_hash}")

# Run tests
test_record_blood_unit()
test_verify_transaction()
```

### Verify on Etherscan

Check transactions on Sepolia Etherscan:

```
https://sepolia.etherscan.io/tx/{tx_hash}
```

---

## Load Testing

### Using Locust

Install Locust:

```bash
pip install locust
```

Create `locustfile.py`:

```python
from locust import HttpUser, task, between
from datetime import datetime, timedelta
import json

class BloodChainUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Authenticate before starting tests"""
        response = self.client.post(
            "/api-token-auth/",
            json={"username": "testuser", "password": "testpass123"}
        )
        self.token = response.json()['token']
    
    @task
    def create_blood_unit(self):
        """Task: Create blood unit"""
        headers = {"Authorization": f"Token {self.token}"}
        
        data = {
            "donor": 1,
            "blood_type": "O+",
            "collected_at": datetime.now().isoformat() + "Z",
            "expiry_date": (datetime.now() + timedelta(days=35)).isoformat() + "Z"
        }
        
        self.client.post(
            "/api/blood-tracking/units/register/",
            json=data,
            headers=headers
        )
    
    @task
    def list_blood_units(self):
        """Task: List blood units"""
        headers = {"Authorization": f"Token {self.token}"}
        self.client.get("/api/blood-tracking/units/", headers=headers)
    
    @task
    def get_blood_unit(self):
        """Task: Get blood unit details"""
        headers = {"Authorization": f"Token {self.token}"}
        self.client.get("/api/blood-tracking/units/1/", headers=headers)
```

Run load test:

```bash
# Start Locust UI
locust -f locustfile.py --host=http://localhost:8000

# Run from command line
locust -f locustfile.py --host=http://localhost:8000 -u 100 -r 10 -t 5m --headless
```

---

## Security Testing

### SQL Injection Testing

```bash
# Test parameter injection
curl -X GET "http://localhost:8000/api/blood-tracking/units/?search=%27 OR %271%27=%271"

# Should return 400 or no results, not error
```

### CSRF Testing

```python
def test_csrf_protection():
    """Test CSRF token requirement"""
    client = Client(enforce_csrf_checks=True)
    
    # POST without CSRF token should fail
    response = client.post(
        '/api/blood-tracking/units/register/',
        json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 403  # Forbidden
```

### Authentication Testing

```python
def test_auth_required():
    """Test endpoints require authentication"""
    client = Client()
    
    # Request without token
    response = client.get('/api/blood-tracking/units/')
    assert response.status_code == 401  # Unauthorized
    
    # Request with invalid token  
    response = client.get(
        '/api/blood-tracking/units/',
        HTTP_AUTHORIZATION='Token invalid_token'
    )
    assert response.status_code == 401  # Unauthorized
```

---

## Automation

### GitHub Actions CI/CD

Create `.github/workflows/tests.yml`:

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: bloodchain_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://test:test@localhost:5432/bloodchain_test
      run: |
        python manage.py test --verbosity=2
    
    - name: Run coverage
      run: |
        pip install coverage
        coverage run --source='.' manage.py test
        coverage report
```

---

**Last Updated:** 2026-04-02

For more help, see [SETUP_GUIDE.md](SETUP_GUIDE.md) and [BLOCKCHAIN_INTEGRATION.md](blood_tracking/BLOCKCHAIN_INTEGRATION.md)
