# BloodChain Architecture Overview

Comprehensive overview of the BloodChain system architecture, design patterns, and technical decisions.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Design Patterns](#design-patterns)
5. [Data Models](#data-models)
6. [API Design](#api-design)
7. [Blockchain Integration](#blockchain-integration)
8. [Security Architecture](#security-architecture)
9. [Scalability](#scalability)
10. [Deployment Architecture](#deployment-architecture)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Applications                     │
│              (Web UI, Mobile, Third-party APIs)              │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway / Nginx                        │
│          (Load Balancing, SSL/TLS, CORS, Caching)            │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐┌─────────────┐┌─────────────┐
    │  Django     ││  Django     ││  Django     │ (Replicated)
    │  Workers    ││  Workers    ││  Workers    │
    │  (Gunicorn) ││  (Gunicorn) ││  (Gunicorn) │
    └──────┬──────┘└──────┬──────┘└──────┬──────┘
           │              │              │
           └──────────────┼──────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
    ┌─────────┐      ┌─────────┐      ┌─────────┐
    │PostgreSQL   │Redis      │Blockchain │
    │Database  │  │Cache     │  │Provider │
    │(Primary) │  │(Sessions)│  │(RPC)    │
    └─────────┘  └─────────┘  └─────────┘
         │                           │
         ▼                           ▼
    ┌─────────┐              ┌──────────────┐
    │PostgreSQL   │          │Ethereum      │
    │Replica  │          │Sepolia/Mainnet│
    └─────────┘          └──────────────┘
```

### Key Components

1. **API Layer:** Django REST Framework providing RESTful endpoints
2. **Business Logic:** Service classes handling blood tracking operations
3. **Data Layer:** PostgreSQL database with Django ORM
4. **Cache Layer:** Redis for session management and caching
5. **Blockchain Layer:** Web3.py for Ethereum integration
6. **Authentication:** Token-based authentication (DRF TokenAuthentication)
7. **API Gateway:** Nginx for reverse proxy, load balancing, SSL/TLS

---

## Technology Stack

### Backend

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Django | 4.2+ |
| REST API | Django REST Framework | 3.14+ |
| Database | PostgreSQL | 12+ |
| ORM | Django ORM | Built-in |
| Task Queue | Celery (Optional) | 5.2+ |
| Cache | Redis | 6.0+ |
| Blockchain | Web3.py | 6.0+ |
| Server | Gunicorn | 20.1+ |
| Reverse Proxy | Nginx | 1.18+ |
| Container | Docker | 20.10+ |

### Frontend

| Component | Technology |
|-----------|------------|
| Framework | React/Vue (if applicable) |
| HTTP Client | Axios/Fetch API |
| Authentication | JWT Tokens |
| Styling | Tailwind CSS (if applicable) |

### Development Tools

| Tool | Purpose |
|------|---------|
| Git | Version control |
| Docker/Compose | Containerization |
| Postman | API testing |
| pytest | Testing framework |
| Black | Code formatting |
| Flake8 | Linting |
| Coverage.py | Code coverage |

---

## Project Structure

```
bloodchain/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── README.md                         # Project README
├── .env.example                      # Environment template
├── .gitignore                        # Git ignore rules
│
├── bloodchain/                        # Main project configuration
│   ├── __init__.py
│   ├── settings.py                   # Django settings
│   │   ├── BASE_DIR                  # Project root
│   │   ├── SECRET_KEY                # Security key
│   │   ├── INSTALLED_APPS            # Installed apps
│   │   ├── MIDDLEWARE                # Middleware stack
│   │   ├── DATABASES                 # Database config
│   │   ├── REST_FRAMEWORK            # DRF settings
│   │   ├── CORS_ALLOWED_ORIGINS      # CORS config
│   │   └── LOGGING                   # Logging config
│   ├── urls.py                       # Root URL configuration
│   ├── asgi.py                       # ASGI config for async
│   └── wsgi.py                       # WSGI config
│
├── blood_tracking/                    # Blood tracking app
│   ├── migrations/                    # Database migrations
│   ├── models.py                      # Data models
│   │   ├── BloodUnit                  # Blood unit model
│   │   ├── BloodStatusHistory         # Status tracking
│   │   ├── BloodTransfer              # Transfer records
│   │   └── BloodDonation              # Donation records
│   ├── views.py                       # API viewsets
│   │   ├── BloodUnitViewSet           # Unit endpoints
│   │   ├── BloodDonationViewSet       # Donation endpoints
│   │   └── BloodTransferViewSet       # Transfer endpoints
│   ├── serializers.py                 # DRF serializers
│   │   ├── BloodUnitSerializer        # Unit serializer
│   │   ├── BloodStatusHistorySerializer
│   │   └── BloodTransferSerializer    # Transfer serializer
│   ├── urls.py                        # App URL routing
│   ├── blockchain_service.py          # Blockchain integration
│   │   ├── BlockchainService          # Main service class
│   │   ├── record_blood_unit_on_chain()
│   │   ├── get_unit_from_chain()
│   │   └── verify_tx_on_chain()
│   ├── tests.py                       # Unit/integration tests
│   └── admin.py                       # Django admin config
│
├── donor/                             # Donor management app
│   ├── models.py                      # Donor model
│   ├── views.py                       # Donor endpoints
│   ├── serializers.py                 # Donor serializers
│   ├── urls.py                        # URL routing
│   └── admin.py                       # Admin config
│
├── hospital/                          # Hospital management app
│   ├── models.py                      # Hospital model
│   ├── views.py                       # Hospital endpoints
│   ├── serializers.py                 # Hospital serializers
│   ├── urls.py                        # URL routing
│   └── admin.py                       # Admin config
│
├── smart_contracts/                   # Smart contracts
│   ├── contracts/
│   │   └── BloodUnitRegistry.sol      # Ethereum smart contract
│   ├── scripts/
│   │   └── deploy.js                  # Deployment script
│   └── package.json                   # Node dependencies
│
├── frontend/                          # Frontend application (if separate)
│   ├── src/
│   ├── package.json
│   └── README.md
│
├── docs/                              # Documentation
│   ├── API_DOCUMENTATION.md           # API reference
│   ├── BLOCKCHAIN_INTEGRATION.md      # Blockchain guide
│   ├── SETUP_GUIDE.md                 # Setup instructions
│   ├── DEPLOYMENT_GUIDE.md            # Deployment guide
│   ├── TESTING_GUIDE.md               # Testing guide
│   ├── QUICK_REFERENCE.md             # Quick reference
│   └── ARCHITECTURE_OVERVIEW.md       # This file
│
├── tests/                             # Test suite
│   ├── test_api.py                    # API tests
│   ├── test_blockchain.py             # Blockchain tests
│   ├── test_models.py                 # Model tests
│   └── fixtures/                      # Test data
│
├── logs/                              # Application logs
│   ├── django.log
│   ├── error.log
│   └── access.log
│
├── staticfiles/                       # Collected static files
├── media/                             # User-uploaded files
│
└── Docker/                            # Docker files
    ├── Dockerfile                     # Application Docker image
    ├── docker-compose.yml             # Docker Compose config
    └── nginx.conf                     # Nginx configuration
```

---

## Design Patterns

### 1. Service Layer Pattern

The blockchain integration uses a service layer pattern:

```python
# blockchain_service.py
class BlockchainService:
    """Service layer for blockchain operations"""
    
    def __init__(self, provider_uri):
        self.web3 = Web3(Web3.HTTPProvider(provider_uri))
        self.contract = self._load_contract()
    
    def record_blood_unit_on_chain(self, unit_id, blood_type, donor_wallet):
        """Encapsulates blockchain recording logic"""
        pass
    
    def get_unit_from_chain(self, unit_id):
        """Encapsulates blockchain retrieval logic"""
        pass

# In views
def register_blood_unit(request):
    blockchain_service = get_blockchain_service()
    result = blockchain_service.record_blood_unit_on_chain(...)
```

**Benefits:**
- Separation of concerns
- Reusable business logic
- Easy to mock for testing
- Centralized error handling

### 2. Repository Pattern (Django ORM)

```python
# models.py
class BloodUnit(models.Model):
    """Data model acting as repository"""
    unit_id = models.UUIDField(unique=True)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES)
    blockchain_tx_hash = models.CharField(blank=True)
    
    # Custom queryset methods
    @classmethod
    def get_available_units(cls):
        return cls.objects.filter(status='storage')
    
    @classmethod
    def get_by_blood_type(cls, blood_type):
        return cls.objects.filter(blood_type=blood_type, status='storage')
```

### 3. Observer Pattern (Django Signals)

```python
# signals.py
from django.db.models.signals import post_save

@receiver(post_save, sender=BloodUnit)
def record_on_blockchain(sender, instance, created, **kwargs):
    """Observer: automatically records new units on blockchain"""
    if created:
        blockchain_service = get_blockchain_service()
        blockchain_service.record_blood_unit_on_chain(
            unit_id=str(instance.unit_id),
            blood_type=instance.blood_type,
            donor_wallet=instance.donor.wallet_address
        )
```

### 4. Singleton Pattern (Blockchain Service)

```python
# Ensure single blockchain service instance
_blockchain_service = None

def get_blockchain_service():
    global _blockchain_service
    if _blockchain_service is None:
        _blockchain_service = BlockchainService(
            os.getenv('WEB3_PROVIDER_URI')
        )
    return _blockchain_service
```

### 5. Factory Pattern (DRF Serializers)

```python
# serializers.py
class BloodUnitSerializer(serializers.ModelSerializer):
    """Factory for blood unit serialization"""
    donor_name = serializers.CharField(source='donor.name', read_only=True)
    status_history = BloodStatusHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = BloodUnit
        fields = ['id', 'unit_id', 'donor', 'donor_name', 'blood_type', 
                  'status', 'status_history', 'blockchain_tx_hash']
```

---

## Data Models

### Entity Relationship Diagram

```
┌─────────────┐
│   Donor     │
├─────────────┤
│ id (PK)     │
│ name        │
│ email       │
│ blood_type  │
│ wallet_addr │
└──────┬──────┘
       │
       │ 1:N
       │
       ▼
┌─────────────┐      ┌──────────────┐
│ BloodUnit   │◄────►│ BloodTransfer│
├─────────────┤      ├──────────────┤
│ id (PK)     │      │ id (PK)      │
│ unit_id (U) │      │ unit_id (FK) │
│ donor_id(FK)│      │ from_hosp(FK)│
│ blood_type  │      │ to_hosp (FK) │
│ status      │      │ status       │
│ tx_hash     │      │ tx_hash      │
│ created_at  │      └──────────────┘
└─────┬───────┘
      │
      │ 1:N
      │
      ▼
┌──────────────────┐
│ BloodStatusHist  │
├──────────────────┤
│ id (PK)          │
│ unit_id (FK)     │
│ prev_status      │
│ new_status       │
│ timestamp        │
│ tx_hash          │
└──────────────────┘

                   ┌─────────────┐
                   │  Hospital   │
                   ├─────────────┤
                   │ id (PK)     │
                   │ name        │
                   │ location    │
                   │ email       │
                   │ capacity    │
                   └─────────────┘
```

### Key Models

**BloodUnit**
- Represents a blood collection unit
- Tracks lifecycle from collection to transfusion/expiry
- Links to blockchain transaction
- Status: collected → testing → storage → transfused/expired

**BloodStatusHistory**
- Immutable log of all status changes
- Records blockchain transaction hash for each change
- Enables complete audit trail

**Donor**
- Represents blood donor
- Stores health information
- Linked to wallet address for incentives

**Hospital**
- Blood storage/transfusion facility
- Tracks inventory and capacity
- Manages transfers

---

## API Design

### RESTful Principles

1. **Resource-Based URLs**
   ```
   GET    /api/blood-tracking/units/          # List
   POST   /api/blood-tracking/units/          # Create
   GET    /api/blood-tracking/units/{id}/     # Retrieve
   PATCH  /api/blood-tracking/units/{id}/     # Partial Update
   PUT    /api/blood-tracking/units/{id}/     # Full Update
   DELETE /api/blood-tracking/units/{id}/     # Delete
   ```

2. **Status Codes**
   - 200 OK, 201 Created, 204 No Content
   - 400 Bad Request, 401 Unauthorized, 403 Forbidden
   - 404 Not Found, 500 Server Error

3. **Error Format**
   ```json
   {
     "error": "Error message",
     "error_code": "ERROR_CODE",
     "status": 400
   }
   ```

### Authentication & Authorization

```
Request → Middleware → Authentication → Authorization → View
           (CORS)      (Token Check)   (Permissions)
```

1. **Token Authentication**
   - Each request includes `Authorization: Token xxx`
   - Tokens stored in database
   - Stateless (no session needed)

2. **Permissions**
   - IsAuthenticated: User must be logged in
   - Custom permissions for specific operations

3. **Rate Limiting**
   - 100 requests per hour (user)
   - 1000 requests per hour (staff)

---

## Blockchain Integration

### Flow Diagram

```
Blood Unit Creation
       │
       ▼
┌─────────────────────────────────┐
│ Create BloodUnit Record         │
│ in Django Database              │
└────────────┬────────────────────┘
             │
             ├─ Signal Triggered
             │
             ▼
┌─────────────────────────────────┐
│ BlockchainService               │
│ .record_blood_unit_on_chain()   │
└────────────┬────────────────────┘
             │
             ├─ Validate Input
             │
             ├─ Connect to Web3
             │
             ├─ Call Smart Contract
             │
             ├─ Monitor Transaction
             │
             ▼
┌─────────────────────────────────┐
│ Ethereum Sepolia Testnet        │
│ Smart Contract Execution        │
└────────────┬────────────────────┘
             │
             ├─ Transaction Mined
             │
             ▼
┌─────────────────────────────────┐
│ Update BloodUnit with           │
│ Transaction Hash                │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Return Success to Client        │
│ Include tx_hash                 │
└─────────────────────────────────┘
```

### Smart Contract Architecture

```solidity
// Ethereum Smart Contract
contract BloodUnitRegistry {
    
    // State: Persistent data on blockchain
    mapping(bytes32 => BloodUnit) public units;
    
    // Events: Trigger off-chain notifications
    event BloodUnitRecorded(bytes32 indexed unitId, uint256 timestamp);
    event StatusUpdated(bytes32 indexed unitId, uint8 newStatus);
    
    // Functions: Callable by external actors
    function recordBloodUnit(...) public { ... }
    function updateStatus(...) public { ... }
    function getBloodUnit(...) public view returns (...) { ... }
}
```

---

## Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────────┐
│ Client Request                          │
│ Authorization: Token abc123def456       │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ TokenAuthentication Middleware          │
│ Validates token against database        │
└────────┬────────────────────────────────┘
         │
         ├─ Valid?
         │
         ├─ YES ─► Set request.user
         │         Continue to view
         │
         └─ NO ─► Return 401 Unauthorized
```

### Data Protection

1. **In Transit**
   - HTTPS/TLS for all communications
   - CSP headers for XSS prevention

2. **At Rest**
   - Database encryption for sensitive fields
   - Hashed passwords using Django's hasher

3. **Access Control**
   - Role-based access (Admin, Staff, User)
   - Field-level permissions via serializers

### Audit Trail

```python
# BloodStatusHistory maintains immutable log
class BloodStatusHistory(models.Model):
    unit = models.ForeignKey(BloodUnit, on_delete=models.CASCADE)
    previous_status = models.CharField()
    new_status = models.CharField()
    timestamp = models.DateTimeField(auto_now_add=True)
    blockchain_tx_hash = models.CharField()  # Links to blockchain
    
    class Meta:
        ordering = ['-timestamp']  # Latest first
```

---

## Scalability

### Horizontal Scaling

```
                    ┌─── Load Balancer (Nginx/HAProxy) ───┐
                    │                                       │
        ┌───────────┴──────────────┬──────────────┬────────────────┐
        ▼                          ▼              ▼                ▼
    ┌─────────┐              ┌─────────┐    ┌─────────┐     ┌─────────┐
    │ Django  │              │ Django  │    │ Django  │     │ Django  │
    │ 8000    │              │ 8001    │    │ 8002    │     │ 8003    │
    └────┬────┘              └────┬────┘    └────┬────┘     └────┬────┘
         │                        │              │               │
         └────────────────────────┼──────────────┴───────────────┘
                                  │
                          ┌───────▼────────┐
                          │ PostgreSQL     │
                          │ Primary        │
                          │ (Read/Write)   │
                          └────────┬───────┘
                                   │
                          ┌────────┴────────┐
                          │                 │
                    ┌─────▼────┐   ┌────▼──────┐
                    │PostgreSQL │   │PostgreSQL │
                    │Replica 1  │   │Replica 2  │
                    │(Read Only)│   │(Read Only)│
                    └───────────┘   └───────────┘
```

### Caching Strategy

```python
# Cache database queries at multiple levels
1. Database layer: PostgreSQL query cache
2. ORM layer: Django ORM query caching
3. Application: Redis cache for frequent queries
4. HTTP: Browser caching, CDN for static files

# Cache hierarchy
@cached_property
def get_available_units():
    # Cache computed properties
    pass

@cache_result(timeout=300)
def get_inventory_stats():
    # Cache function results
    pass

# Cache invalidation on updates
@receiver(post_save, sender=BloodUnit)
def invalidate_cache(sender, instance, **kwargs):
    cache.delete(f'inventory_stats')
```

---

## Deployment Architecture

### Development Environment

```
Developer Machine
├── Python venv
├── PostgreSQL (local)
├── Redis (local)
├── Django dev server (http://localhost:8000)
└── Blockchain testnet (Sepolia)
```

### Production Environment

```
┌─────────────────────────────────────────────────────┐
│                   Internet                          │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │ CDN (Static Files)   │
           └──────────────────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │ WAF / DDoS Protection│
           └──────────────┬───────┘
                          │
                          ▼
                ┌─────────────────────┐
                │ Load Balancer       │
                │ (Health Checks)     │
                └──────┬──────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        │              │              │              │
        ▼              ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │Nginx   │    │Nginx   │    │Nginx   │    │Nginx   │
    │+ Django│    │+ Django│    │+ Django│    │+ Django│
    │Container   │Container   │Container   │Container
    └───┬────┘    └───┬────┘    └───┬────┘    └───┬────┘
        │             │             │             │
        └─────────────┼─────────────┴─────────────┘
                      │
        ┌─────────────┴──────────────┬───────────────┐
        ▼                            ▼               ▼
    ┌─────────┐              ┌─────────────┐   ┌─────────┐
    │PostgreSQL   │              │ Redis       │   │ Backup  │
    │Primary  │              │ Cache       │   │ Storage │
    └────┬────┘              └─────────────┘   └─────────┘
         │
         ├─ Replication ──┐
         │                │
         ▼                ▼
    ┌─────────┐  ┌──────────────┐
    │PostgreSQL   │ Standby      │
    │Replica  │  │ Server       │
    └─────────┘  └──────────────┘

                     │
                     │ (Blockchain RPC)
                     │
                     ▼
            ┌───────────────────┐
            │ Ethereum Network  │
            │ Sepolia/Mainnet   │
            └───────────────────┘

┌─────────────────────────────────────────┐
│ Monitoring & Observability              │
├─────────────────────────────────────────┤
│ ├─ Prometheus (Metrics)                 │
│ ├─ Grafana (Dashboards)                 │
│ ├─ ELK Stack (Logs)                     │
│ └─ Sentry (Error Tracking)              │
└─────────────────────────────────────────┘
```

---

## Technology Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| **Django** | Mature, batteries-included, excellent ORM |
| **PostgreSQL** | ACID compliance, supports JSON, great for relational data |
| **DRF** | Industry standard for REST APIs in Django |
| **Web3.py** | Official Python library for Ethereum interaction |
| **Ethereum** | Mature blockchain, extensive tooling, smart contract support |
| **Redis** | Fast caching, session storage, pub/sub capabilities |
| **Docker** | Consistent environments, easy deployment scaling |
| **Nginx** | Lightweight, fast reverse proxy, load balancing |

---

## Performance Considerations

### Database Optimization

```python
# Use select_related() for ForeignKey lookups
units = BloodUnit.objects.select_related('donor').all()

# Use prefetch_related() for reverse relations
units = BloodUnit.objects.prefetch_related('status_history').all()

# Use only() to limit fields
units = BloodUnit.objects.only('id', 'unit_id', 'blood_type')

# Index frequently queried fields
class BloodUnit(models.Model):
    blood_type = models.CharField(db_index=True)
    status = models.CharField(db_index=True)
    created_at = models.DateTimeField(db_index=True)
```

### API Response Optimization

```python
# Pagination
class BloodUnitViewSet(viewsets.Modelset):
    pagination_class = PageNumberPagination
    paginate_by = 20

# Filtering
filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
filterset_fields = ['blood_type', 'status']
search_fields = ['unit_id', 'donor__name']

# Caching
@action(detail=False)
@cache_page(60 * 5)  # Cache for 5 minutes
def available_units(self, request):
    return Response(...)
```

---

**Last Updated:** 2026-04-02

For implementation details, see:
- [SETUP_GUIDE.md](SETUP_GUIDE.md)
- [API_DOCUMENTATION.md](blood_tracking/API_DOCUMENTATION.md)
- [BLOCKCHAIN_INTEGRATION.md](blood_tracking/BLOCKCHAIN_INTEGRATION.md)
