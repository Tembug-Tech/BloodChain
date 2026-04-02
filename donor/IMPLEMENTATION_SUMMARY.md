# Donor App Implementation Summary

## Overview
The Donor app has been completely refactored with a new model schema, updated serializers, and comprehensive API endpoints for blood donor management with blockchain wallet support.

## Files Modified

### 1. **donor/models.py** ✓
- Simplified the Donor model with focused fields
- Removed: `address`, `city`, `state`, `country`, `postal_code`, `is_active_donor`, `total_donations`
- Added: `location` (single field for city/region), `is_available` (boolean), `wallet_address` (blockchain), `related_name='donor_profile'`
- Added database indexes on: `blood_type`, `is_available`, `location`

**Model Fields:**
```python
- user: OneToOneField(User, related_name='donor_profile')
- blood_type: CharField with 8 blood type choices
- phone_number: CharField (max 15)
- location: CharField (max 255)
- date_of_birth: DateField
- last_donation_date: DateTimeField (nullable)
- is_available: BooleanField (default=True)
- wallet_address: CharField (max 255, optional)
- created_at: DateTimeField (auto_now_add)
- updated_at: DateTimeField (auto_now)
```

### 2. **donor/serializers.py** ✓
- Updated `DonorSerializer` with new fields
- Created `DonorRegistrationSerializer` with validation for user registration
- Built-in validation for duplicate usernames and emails

**Serializers:**
- `UserSerializer` - Nested user data
- `DonorSerializer` - Full donor profile (read/write)
- `DonorRegistrationSerializer` - Registration with user account creation

### 3. **donor/views.py** ✓
- Enhanced `DonorViewSet` with 5 main endpoints:
  1. **register** (POST) - Register new donor with user account
  2. **my_profile** (GET) - Get authenticated user's profile
  3. **update_availability** (PATCH) - Update donor availability
  4. **available** (GET) - List available donors with filters
  5. **by_blood_type** (GET) - Get donors by blood type

**Key Features:**
- Proper permission handling (AllowAny for registration, IsAuthenticated for others)
- Input validation with detailed error responses
- Query parameter filtering
- Comprehensive docstrings with examples

### 4. **donor/admin.py** ✓
- Updated Django admin interface
- New list display: `user`, `blood_type`, `location`, `is_available`, `created_at`
- Updated search fields to include `location`
- Reorganized admin fieldsets for better UX
- Removed obsolete fields from display

### 5. **donor/urls.py** ✓
- Already configured with DefaultRouter
- Routes automatically generated from ViewSet actions

### 6. **bloodchain/settings.py** ✓
- Donor app already listed in INSTALLED_APPS
- No changes needed

### 7. **blood_tracking/views.py** ✓
- Updated reference: `request.user.donor` → `request.user.donor_profile`

### 8. **rewards/views.py** ✓
- Updated 5 references: `request.user.donor` → `request.user.donor_profile`

## New Documentation Files

### 1. **donor/MIGRATION_GUIDE.md**
Comprehensive guide for database migrations including:
- List of changed fields
- Migration creation steps
- Data migration examples for existing data
- New API endpoints reference
- Testing instructions

### 2. **donor/API_DOCUMENTATION.md**
Complete API reference including:
- All 5 endpoints with detailed descriptions
- Request/response examples in JSON
- Query parameter documentation
- Authentication methods (Token & Session)
- cURL, Python, and JavaScript examples
- HTTP status codes reference
- Common errors and their solutions

## API Endpoints Summary

### Public Endpoints (No Authentication)
```
POST   /api/donors/register/                 - Register new donor
```

### Protected Endpoints (Authentication Required)
```
GET    /api/donors/                          - List all donors
GET    /api/donors/{id}/                     - Get specific donor
PUT    /api/donors/{id}/                     - Update donor (full)
PATCH  /api/donors/{id}/                     - Update donor (partial)
DELETE /api/donors/{id}/                     - Delete donor
GET    /api/donors/my_profile/               - Get current user's profile
GET    /api/donors/available/                - List available donors (with filters)
GET    /api/donors/by_blood_type/            - Get donors by blood type
PATCH  /api/donors/{id}/update_availability/ - Update availability status
```

## Implementation Details

### Authentication
- Token-based authentication for API calls
- AllowAny permission for registration endpoint
- IsAuthenticated for all other endpoints

### Filtering & Search
- `available/` endpoint supports:
  - `?blood_type=O+` - Filter by blood type
  - `?location=New York` - Filter by location (case-insensitive)
  - `?blood_type=A+&location=California` - Combined filters

### Validation
- Email uniqueness validation
- Username uniqueness validation
- Blood type choice validation
- Required field validation
- Password requirements (Django default)

### Relationships
- One-to-One relationship with Django User model
- Related name: `donor_profile` (access via `user.donor_profile`)
- Automatic deletion of Donor when User is deleted

### Blockchain Integration
- `wallet_address` field stores Ethereum-compatible wallet addresses
- Optional field - donors can update it later
- Ready for token reward distribution via smart contracts

## Data Migration Path

### For New Databases
1. `python manage.py makemigrations donor`
2. `python manage.py migrate donor`
3. `python manage.py migrate` (all apps)

### For Existing Databases with Data
1. Create initial migration: `python manage.py makemigrations donor`
2. Create data migration: `python manage.py makemigrations donor --empty --name migrate_location_data`
3. Edit migration to transform old address fields to location
4. Apply migrations: `python manage.py migrate`

## Usage Examples

### Register a New Donor
```bash
curl -X POST http://localhost:8000/api/donors/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure123",
    "blood_type": "O+",
    "phone_number": "+1-555-0123",
    "location": "New York, NY",
    "date_of_birth": "1990-01-15",
    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f42bE"
  }'
```

### Get Available Donors by Blood Type
```bash
curl -X GET "http://localhost:8000/api/donors/available/?blood_type=O+" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Update Donor Availability
```bash
curl -X PATCH http://localhost:8000/api/donors/1/update_availability/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_available": false}'
```

## Next Steps

### 1. Database Migrations
- [ ] Run `python manage.py makemigrations donor`
- [ ] Review the generated migration file
- [ ] Run `python manage.py migrate donor`
- [ ] Run `python manage.py migrate` for all apps

### 2. Testing
- [ ] Register a new donor via API
- [ ] Get donor profile
- [ ] Update availability status
- [ ] Filter available donors by blood type
- [ ] Filter available donors by location
- [ ] Test permissions (unauthenticated access should fail for protected endpoints)

### 3. Admin Interface
- [ ] Login to admin at http://localhost:8000/admin
- [ ] View donor list with new columns
- [ ] Test search by location, name, email, phone
- [ ] Test filtering by blood type and availability

### 4. Frontend Integration
- [ ] Update frontend donor registration form
- [ ] Update donor profile display
- [ ] Implement availability toggle
- [ ] Add blood type/location filtering

### 5. Optional Enhancements
- [ ] Add donor search distance calculation
- [ ] Implement automated wallet address generation
- [ ] Add donation history tracking
- [ ] Create donor badge/achievement system
- [ ] Add notification preferences

## Backward Compatibility

⚠️ **Breaking Changes:**
- Field `is_active_donor` → `is_available`
- Field `address`, `city`, `state`, `country`, `postal_code` → `location`
- Related name change: `user.donor` → `user.donor_profile`

These changes require:
1. Database migration
2. Updating any external code that references old field names
3. Updating frontend code to use new field names

## Performance Considerations

1. **Indexes:** Added indexes on frequently queried fields:
   - `blood_type` - For blood type filtering
   - `is_available` - For available donor queries
   - `location` - For location-based filtering

2. **Query Optimization:** ViewSet uses default queryset without N+1 queries
   - User data is fetched via OneToOne relationship (efficient)

3. **Caching Opportunities:**
   - Cache available donors list (updates less frequently)
   - Cache donor by location/blood type combinations

## Security Considerations

1. **Authentication:** All sensitive endpoints protected with IsAuthenticated
2. **Authorization:** Users can only update their own donor record
3. **Password:** Uses Django's built-in password hashing
4. **Email Validation:** Built-in email field validation
5. **Wallet Addresses:** Stored as-is (no validation - app responsibility)

## Files Structure

```
donor/
├── __init__.py
├── admin.py                          # Updated
├── apps.py
├── models.py                         # Updated
├── serializers.py                    # Updated
├── views.py                          # Updated
├── tests.py
├── urls.py
├── API_DOCUMENTATION.md              # New
└── MIGRATION_GUIDE.md                # New
```

## Related Files Updated

- `bloodchain/settings.py` - No changes needed (donor already registered)
- `bloodchain/urls.py` - No changes needed (donor already included)
- `blood_tracking/views.py` - Updated related name reference
- `rewards/views.py` - Updated 5 related name references

## Testing Checklist

- [ ] Registration endpoint creates user and donor
- [ ] Registration validates duplicate email/username
- [ ] Registration validates required fields
- [ ] my_profile endpoint returns current user's profile
- [ ] available endpoint returns only is_available=True donors
- [ ] available endpoint filters by blood_type
- [ ] available endpoint filters by location (case-insensitive)
- [ ] available endpoint supports combined filters
- [ ] by_blood_type endpoint requires blood_type parameter
- [ ] update_availability only allows updating own profile
- [ ] update_availability persists changes
- [ ] Unauthenticated access returns 401
- [ ] Admin interface displays new fields correctly
- [ ] Search in admin works with location field

## Support & Troubleshooting

### Common Issues

**Q: Migration fails with "column does not exist"**
- A: Run `python manage.py migrate donor` first, then create new migrations

**Q: ImportError: cannot import name 'DonorRegistrationSerializer'**
- A: Make sure you've updated serializers.py correctly

**Q: 404 when accessing /api/donors/register/**
- A: Check that donor/urls.py is properly included in bloodchain/urls.py

**Q: Wallet address not saving**
- A: wallet_address is optional and nullable - ensure field is optional in your form

For more issues, check API_DOCUMENTATION.md or MIGRATION_GUIDE.md
