# BloodChain Setup Guide

## Quick Start

This guide will help you set up and run the BloodChain blood tracking system with blockchain integration.

---

## Prerequisites

- **Python 3.9+**
- **PostgreSQL 12+** (or SQLite for development)
- **Node.js 16+** (for frontend)
- **Git**
- **Pip** (Python package manager)

---

## Step 1: Clone and Install

### 1.1 Clone the Repository

```bash
git clone https://github.com/yourorg/bloodchain.git
cd bloodchain
```

### 1.2 Create Python Virtual Environment

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### On Windows (CMD):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### 1.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 2: Database Setup

### 2.1 Configure Database

Copy the sample environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure your database:

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/bloodchain

# OR SQLite (for development)
DATABASE_URL=sqlite:///db.sqlite3
```

### 2.2 Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2.3 Verify Database Setup

```bash
python manage.py dbshell
```

---

## Step 3: Blockchain Configuration

### 3.1 Set Up Ethereum Testnet Access

#### Get Infura API Key:
1. Visit https://infura.io
2. Sign up for a free account
3. Create new project
4. Choose "Sepolia" network
5. Copy your RPC URL

#### Update `.env`:

```bash
# Ethereum RPC Provider for Sepolia testnet
WEB3_PROVIDER_URI=https://sepolia.infura.io/v3/YOUR_PROJECT_ID

# (Optional) If deploying smart contract
BLOOD_UNIT_CONTRACT_ADDRESS=0x...
BLOOD_UNIT_CONTRACT_ABI='[...]'
```

### 3.2 Test Blockchain Connection

```bash
python manage.py shell

# In the Python shell:
from blood_tracking.blockchain_service import get_blockchain_service
service = get_blockchain_service()

# Check connection
if service.is_connected:
    print("✓ Connected to Sepolia testnet")
else:
    print("✗ Failed to connect")
```

### 3.3 Deploy Smart Contract (Optional)

If you want to enable actual smart contract interactions:

1. **Using Remix IDE:**
   - Go to https://remix.ethereum.org
   - Paste contract code from `smart_contracts/BloodUnitRegistry.sol`
   - Select "Sepolia" network in MetaMask
   - Deploy and copy contract address
   - Update `BLOOD_UNIT_CONTRACT_ADDRESS` in `.env`

2. **Using Hardhat (Manual Deployment):**
   ```bash
   cd smart_contracts
   npm install
   npx hardhat compile
   npx hardhat run scripts/deploy.js --network sepolia
   ```

---

## Step 4: Create Superuser and Initial Data

### 4.1 Create Admin User

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 4.2 Load Sample Data (Optional)

```bash
python manage.py loaddata fixtures/initial_data.json
```

---

## Step 5: Run Development Server

### 5.1 Start Django Development Server

```bash
python manage.py runserver
```

The server will start at `http://localhost:8000`

### 5.2 Access Admin Panel

Navigate to: `http://localhost:8000/admin`

- Login with your superuser credentials
- Create hospitals, donors, and blood units

### 5.3 Get Authentication Token

```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "yourusername",
    "password": "yourpassword"
  }'
```

Store the returned token for API testing.

---

## Step 6: Test the API

### 6.1 Test Blood Unit Registration

```bash
TOKEN="your_token_here"

curl -X POST http://localhost:8000/api/blood-tracking/units/register/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "donor": 1,
    "blood_type": "O+",
    "collected_at": "2026-04-02T10:30:00Z",
    "expiry_date": "2026-05-02T10:30:00Z"
  }' | jq .
```

**Expected Response:**
- `blockchain_record.success`: `true` (if blockchain is enabled)
- `blockchain_record.tx_hash`: Transaction hash (if blockchain is enabled)

### 6.2 Test Blockchain History Retrieval

```bash
curl -X GET http://localhost:8000/api/blood-tracking/units/1/blockchain_history/ \
  -H "Authorization: Token $TOKEN" | jq .
```

---

## Step 7: Frontend Setup (Optional)

If using a React/Vue frontend:

```bash
cd frontend
npm install
npm start
```

Frontend will run at `http://localhost:3000`

---

## Project Structure

```
bloodchain/
├── manage.py                          # Django management
├── requirements.txt                   # Python dependencies
├── .env.example                      # Environment template
│
├── bloodchain/                        # Main project directory
│   ├── settings.py                   # Django settings
│   ├── urls.py                       # URL routing
│   └── wsgi.py                       # WSGI application
│
├── blood_tracking/                    # Blood tracking app
│   ├── models.py                     # Data models
│   ├── views.py                      # API views
│   ├── serializers.py                # DRF serializers
│   ├── urls.py                       # App URL routing
│   └── blockchain_service.py         # Blockchain integration
│
├── donor/                             # Donor management app
│   ├── models.py                     # Donor models
│   ├── views.py                      # Donor views
│   └── serializers.py                # Donor serializers
│
├── hospital/                          # Hospital management app
│   ├── models.py                     # Hospital models
│   ├── views.py                      # Hospital views
│   └── serializers.py                # Hospital serializers
│
├── smart_contracts/                   # Smart contracts
│   ├── contracts/
│   │   └── BloodUnitRegistry.sol     # Smart contract
│   └── scripts/
│       └── deploy.js                 # Deployment script
│
├── frontend/                          # Frontend (if applicable)
│   ├── src/
│   └── package.json
│
└── docs/                              # Documentation
    ├── API_DOCUMENTATION.md
    ├── BLOCKCHAIN_INTEGRATION.md
    └── SETUP_GUIDE.md
```

---

## Environment Variables

### Required Variables

```bash
# Django
SECRET_KEY=your_secret_key_here
DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Blockchain
WEB3_PROVIDER_URI=https://sepolia.infura.io/v3/YOUR_INFURA_KEY

# Email (for notifications)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Optional Variables

```bash
# Smart Contract
BLOOD_UNIT_CONTRACT_ADDRESS=0x...
BLOOD_UNIT_CONTRACT_ABI='[...]'

# Allowed Origins (CORS)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# API Rate Limiting
API_RATE_LIMIT=100/hour
```

---

## Troubleshooting

### Issue: Database Connection Error

**Solution:**
```bash
# Check database URL in .env
# For PostgreSQL, ensure it's running:
psql -U username -d bloodchain

# For SQLite, file should exist
ls -la db.sqlite3
```

### Issue: Blockchain Connection Failed

**Solution:**
```bash
# Verify Infura API key
curl https://sepolia.infura.io/v3/YOUR_KEY

# Check WEB3_PROVIDER_URI in .env
# Should be: https://sepolia.infura.io/v3/YOUR_PROJECT_ID
```

### Issue: Port 8000 Already in Use

**Solution:**
```bash
# Use different port
python manage.py runserver 8001

# Or kill process on port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```

### Issue: ModuleNotFoundError

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Migrate Errors

**Solution:**
```bash
# Reset migrations (development only)
python manage.py migrate blood_tracking zero
python manage.py migrate

# Or delete migrations and restart
rm blood_tracking/migrations/00*.py
python manage.py makemigrations
python manage.py migrate
```

---

## Useful Commands

```bash
# Run tests
python manage.py test

# Create admin user
python manage.py createsuperuser

# Load sample data
python manage.py loaddata fixtures/initial_data.json

# Django shell
python manage.py shell

# Check for database issues
python manage.py check

# Collect static files (production)
python manage.py collectstatic

# Create new migration
python manage.py makemigrations <app_name>

# Apply migrations
python manage.py migrate

# Reset all databases (development only)
python manage.py flush
```

---

## Production Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for:
- Docker setup
- Gunicorn/uWSGI configuration
- Nginx reverse proxy
- PostgreSQL setup
- SSL/TLS configuration
- Environment security

---

## Testing

### Run Unit Tests

```bash
python manage.py test blood_tracking
python manage.py test donor
python manage.py test hospital
```

### Run API Tests

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing procedures.

---

## Next Steps

1. **Review API Documentation:** See [API_DOCUMENTATION.md](blood_tracking/API_DOCUMENTATION.md)
2. **Blockchain Integration:** See [BLOCKCHAIN_INTEGRATION.md](blood_tracking/BLOCKCHAIN_INTEGRATION.md)
3. **Running in Production:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
4. **Test the System:** See [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

## Support & Help

- **Django Documentation:** https://docs.djangoproject.com/
- **Django REST Framework:** https://www.django-rest-framework.org/
- **Web3.py Documentation:** https://web3py.readthedocs.io/
- **Ethereum Documentation:** https://ethereum.org/developers
- **Issues/Bug Reports:** Create an issue on GitHub

---

**Last Updated:** 2026-04-02
