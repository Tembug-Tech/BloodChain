"""
Donor App Migration Guide
=========================

This document describes the changes made to the Donor app and the required database migrations.

Changed Model Fields
====================

Old Fields (removed):
- address (TextField)
- city (CharField)
- state (CharField)
- country (CharField)
- postal_code (CharField)
- is_active_donor (BooleanField)
- total_donations (IntegerField)

New Fields (added):
- location (CharField) - Replaces the address-related fields
- is_available (BooleanField) - Replaces is_active_donor
- wallet_address (CharField) - New field for blockchain wallet address

Field Changes:
- user: Updated related_name to 'donor_profile'

New Indexes:
- location field is now indexed for faster queries

Creating and Applying Migrations
=================================

1. Create migration file:
   python manage.py makemigrations donor

2. Review the migration (optional):
   python manage.py showmigration donor

3. Apply the migration:
   python manage.py migrate donor

4. If migrating from an older version with existing data:
   
   Option A: Data Migration (Recommended for production)
   ------
   You'll need to create a data migration to handle the transformation:
   
   python manage.py makemigrations donor --empty --name migrate_location_data
   
   Then edit the migration file to transform old address fields to location:
   
   ```python
   def migrate_address_to_location(apps, schema_editor):
       Donor = apps.get_model('donor', 'Donor')
       for donor in Donor.objects.all():
           # Combine address fields into location
           parts = [donor.address, donor.city, donor.state, donor.country]
           location = ', '.join(p for p in parts if p)
           donor.location = location or 'Unknown'
           donor.save()
   
   def reverse_migrate(apps, schema_editor):
       pass  # Reverse migration logic
   
   operations = [
       migrations.RunPython(migrate_address_to_location, reverse_migrate),
   ]
   ```
   
   Option B: Fresh Database (Development)
   ------
   If you're starting fresh or don't have important data:
   
   python manage.py migrate donor zero  # Unapply all migrations
   python manage.py migrate donor       # Reapply fresh

New API Endpoints
=================

1. Register a new donor (POST)
   POST /api/donors/register/
   
   Request body:
   {
       "username": "john_doe",
       "email": "john@example.com",
       "password": "securepassword123",
       "first_name": "John",
       "last_name": "Doe",
       "blood_type": "O+",
       "phone_number": "555-1234",
       "location": "New York, NY",
       "date_of_birth": "1990-01-15",
       "is_available": true,
       "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f42bE" (optional)
   }

2. Get user's donor profile (GET)
   GET /api/donors/my_profile/
   
   Returns: Donor profile for authenticated user

3. Update donor availability (PATCH)
   PATCH /api/donors/{id}/update_availability/
   
   Request body:
   {
       "is_available": true/false
   }

4. List available donors (GET)
   GET /api/donors/available/
   
   Query parameters:
   - blood_type: Filter by blood type (optional)
   - location: Filter by location (partial match, case-insensitive)
   
   Examples:
   - GET /api/donors/available/?blood_type=O+
   - GET /api/donors/available/?location=New York
   - GET /api/donors/available/?blood_type=A+&location=California

5. Get available donors by blood type (GET)
   GET /api/donors/by_blood_type/?blood_type=O+
   
   Returns: List of available donors with specified blood type

Updated Admin Interface
=======================

The Django admin interface has been updated with:
- New fields: location, is_available, wallet_address
- Removed fields: address, city, state, country, postal_code, total_donations
- Updated list display to show location and is_available instead
- Improved search to include location

Model Features
==============

1. One-to-One relationship with Django User model
   - Related name: 'donor_profile' (access via user.donor_profile)

2. Blood type choices:
   - A+, A-, B+, B-, AB+, AB-, O+, O-

3. Location field:
   - Stores city, state/region information
   - Indexed for quick lookups

4. Blockchain integration:
   - wallet_address field stores Ethereum-compatible wallet addresses
   - Ready for token reward distribution

5. Availability tracking:
   - is_available boolean indicates if donor can donate

6. Automatic timestamps:
   - created_at and updated_at fields

Testing the Migration
====================

After running migrations, test with:

1. Create a donor user:
   POST http://localhost:8000/api/donors/register/
   
2. List available donors:
   GET http://localhost:8000/api/donors/available/
   
3. Filter by blood type:
   GET http://localhost:8000/api/donors/available/?blood_type=O+
   
4. Filter by location:
   GET http://localhost:8000/api/donors/available/?location=New York

Rollback (If needed)
====================

To rollback to previous version:
python manage.py migrate donor <previous_migration_name>

Or to remove all donor migrations:
python manage.py migrate donor zero
