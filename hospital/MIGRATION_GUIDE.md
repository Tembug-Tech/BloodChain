# Hospital App - Migration Guide

## Overview

This guide explains how to handle database migrations for the Hospital app, particularly the new `BloodRequest` model.

---

## Quick Migration (First Time)

### 1. Generate Migrations
```bash
python manage.py makemigrations hospital
```

**Output:**
```
Migrations for 'hospital':
  hospital/migrations/0002_bloodrequest.py
    - Create model BloodRequest
```

### 2. Review Migration File
```bash
cat hospital/migrations/0002_bloodrequest.py
```

You'll see:
- BloodRequest model definition
- Field definitions
- Index creation
- Foreign key to Hospital

### 3. Apply Migrations
```bash
python manage.py migrate hospital
```

**Output:**
```
Operations to perform:
  Apply all migrations: hospital
Running migrations:
  Applying hospital.0002_bloodrequest... OK
```

### 4. Verify Database
```bash
python manage.py dbshell

# Then in PostgreSQL shell:
\dt hospital_bloodrequest
```

You should see the table with columns:
- id
- hospital_id
- blood_type
- units_needed
- urgency_level
- status
- description
- created_at
- fulfilled_at

---

## Migration File Structure

### Example Migration: 0002_bloodrequest.py

```python
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BloodRequest',
            fields=[
                ('id', models.BigAutoField(...)),
                ('blood_type', models.CharField(...)),
                ('units_needed', models.DecimalField(...)),
                ('urgency_level', models.CharField(...)),
                ('status', models.CharField(...)),
                ('description', models.TextField(...)),
                ('created_at', models.DateTimeField(...)),
                ('fulfilled_at', models.DateTimeField(...)),
                ('hospital', models.ForeignKey(...)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='bloodrequest',
            index=models.Index(...),
        ),
    ]
```

---

## Common Migration Scenarios

### Scenario 1: First Time Setup (Fresh Database)

```bash
# 1. Create superuser
python manage.py createsuperuser

# 2. Run all migrations
python manage.py migrate

# 3. Create test data
python manage.py shell

>>> from hospital.models import Hospital, BloodRequest
>>> from django.contrib.auth.models import User
>>> 
>>> # Create user
>>> user = User.objects.create_user('admin', 'admin@test.com', 'password')
>>> 
>>> # Create hospital
>>> hospital = Hospital.objects.create(
...     name='Test Hospital',
...     registration_number='REG-TEST-001',
...     address='123 Test Ave',
...     city='Boston',
...     state='MA',
...     country='USA',
...     postal_code='02101',
...     phone_number='+1-617-555-0001',
...     email='test@hospital.com',
...     admin=user
... )
>>> 
>>> # Create blood request
>>> request = BloodRequest.objects.create(
...     hospital=hospital,
...     blood_type='O+',
...     units_needed=15.00,
...     urgency_level='critical',
...     description='Emergency supply'
... )
>>> 
>>> exit()

# 4. Run server
python manage.py runserver
```

### Scenario 2: Adding New Field to BloodRequest

```bash
# 1. Update hospital/models.py
# Add new field to BloodRequest model

# 2. Create migration
python manage.py makemigrations hospital
# This creates: hospital/migrations/0003_bloodrequest_fieldname.py

# 3. Review migration
cat hospital/migrations/0003_bloodrequest_fieldname.py

# 4. Apply migration
python manage.py migrate hospital

# 5. Test
python manage.py shell
>>> from hospital.models import BloodRequest
>>> # Verify new field exists
```

### Scenario 3: Changing Field Type

```bash
# Example: Change units_needed from Decimal to Integer

# 1. Update model
# OLD: units_needed = models.DecimalField(max_digits=5, decimal_places=2)
# NEW: units_needed = models.IntegerField()

# 2. Create migration (Django detects change)
python manage.py makemigrations hospital
# Creates: hospital/migrations/0004_alter_bloodrequest_units_needed.py

# 3. Review migration - may need data conversion

# 4. If migration needs data migration:
# Edit the migration file to add:
# migrations.RunPython(convert_decimal_to_int)

# 5. Apply
python manage.py migrate hospital

# 6. Test that data is preserved/converted correctly
```

### Scenario 4: Rollback Changes

```bash
# 1. View migration history
python manage.py showmigrations hospital

# Output:
# hospital
#  [ ] 0001_initial
#  [X] 0002_bloodrequest
#  [X] 0003_bloodrequest_fieldname
#  [X] 0004_alter_bloodrequest_units_needed

# 2. Rollback to specific migration
python manage.py migrate hospital 0002_bloodrequest
# Now only 0001 and 0002 are applied

# 3. Or rollback all migrations
python manage.py migrate hospital zero
# Removes all hospital app migrations

# 4. Check status
python manage.py showmigrations hospital
```

### Scenario 5: Fresh Start (Delete All)

```bash
# WARNING: This deletes all data!

# 1. Delete migration files (keep 0001_initial.py)
rm hospital/migrations/000[2-9]*.py
rm hospital/migrations/00[1-9][0-9]*.py

# 2. Reset database to initial migration
python manage.py migrate hospital zero

# 3. Create fresh migrations
python manage.py makemigrations hospital

# 4. Apply
python manage.py migrate hospital

# 5. Recreate superuser
python manage.py createsuperuser
```

---

## Migration Commands Reference

### View All Migrations
```bash
python manage.py showmigrations
# Shows all apps and their migration status ([ ] = not applied, [X] = applied)

python manage.py showmigrations hospital
# Shows only hospital app migrations
```

### Show Current Migration State
```bash
python manage.py showmigrations --plan hospital
# Shows planned migrations to be applied
```

### Create Migrations
```bash
python manage.py makemigrations hospital
# Automatically detects model changes and creates migration files

python manage.py makemigrations hospital --name add_blood_request_model
# Create with custom name

python manage.py makemigrations hospital --dry-run
# Preview without creating files

python manage.py makemigrations hospital --verbosity 3
# Verbose output showing what's being detected
```

### Apply Migrations
```bash
python manage.py migrate hospital
# Apply all pending migrations

python manage.py migrate hospital 0002_bloodrequest
# Apply up to specific migration

python manage.py migrate hospital --plan
# Show what would be applied

python manage.py migrate hospital --verbosity 3
# Verbose output
```

### Check Migration Status
```bash
python manage.py migrate --check
# Returns 0 if all migrations applied, 1 otherwise
# Good for CI/CD pipelines
```

### Inspect Migration
```bash
python manage.py sqlmigrate hospital 0002_bloodrequest
# Shows SQL that will be executed
# Useful for reviewing actual SQL changes

python manage.py sqlsequencereset hospital
# Shows SQL to reset sequences
```

---

## Migration Best Practices

### 1. Always Review Generated Migrations
```bash
# Before applying:
cat hospital/migrations/0002_bloodrequest.py

# Check the SQL it will execute:
python manage.py sqlmigrate hospital 0002_bloodrequest
```

### 2. Test Migrations Locally First
```bash
# Apply to local development database
python manage.py migrate hospital

# Test API endpoints
curl -X POST http://localhost:8000/api/blood-requests/ ...

# If issues, rollback
python manage.py migrate hospital 0001_initial
```

### 3. Backup Database Before Major Migrations
```bash
# PostgreSQL backup
pg_dump bloodchain_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Apply migration
python manage.py migrate

# Test
# If issues, restore:
psql bloodchain_db < backup_20240115_103000.sql
```

### 4. Use Data Migrations for Complex Changes
```bash
# For data transformation, not just schema changes:
python manage.py makemigrations hospital --empty --name migration_name

# This creates empty migration file you can populate with custom code
```

### 5. Never Edit Historical Migrations
```
❌ WRONG: Edit 0001_initial.py after it's applied
✅ RIGHT: Create new migration 0002_fix_field.py

Editing historical migrations breaks other developers' databases!
```

### 6. Keep Migrations Small and Focused
```
❌ WRONG: 0005_long_migration.py (adds 5 models, changes 3 fields)
✅ RIGHT: 
    0005_add_bloodrequest_model.py
    0006_alter_hospital_fields.py
    0007_add_inventory_model.py
```

---

## Troubleshooting Migrations

### Issue: "No migrations to apply"
```bash
# All migrations already applied
python manage.py showmigrations hospital
# Should show [X] for all migrations

# If you made changes:
python manage.py makemigrations hospital
# If nothing appears, no model changes detected
```

### Issue: "Migration error: table already exists"
```bash
# Migration trying to create table that exists
# Usually means database is out of sync

# Check current migration status
python manage.py showmigrations hospital

# If status shown as applied but table exists, mark as applied:
python manage.py migrate hospital --fake 0002_bloodrequest
```

### Issue: "IntegrityError: UNIQUE constraint failed"
```bash
# Data migration caused unique constraint violation

# Option 1: Rollback and fix data first
python manage.py migrate hospital 0001_initial
# Fix duplicate data in database
# Reapply migration

# Option 2: Create data migration to deduplicate
python manage.py makemigrations hospital --empty --name fix_duplicates
# Edit migration to remove duplicates
python manage.py migrate hospital
```

### Issue: "Circular dependency in migrations"
```bash
# Migration files reference each other in circular way

# Check dependencies
cat hospital/migrations/*.py | grep dependencies

# Fix by:
# 1. Identify circular reference
# 2. Reorganize migrations to break cycle
# 3. Or merge migrations that depend on each other
```

### Issue: "No changes detected in app"
```bash
# Model changed but makemigrations found no changes

# Possible causes:
# 1. Syntax error in model
# 2. Change not saved to file
# 3. Class not properly indented

# Check:
python manage.py check
# Shows validation errors

# Verify file saved:
cat hospital/models.py | grep "class BloodRequest"
```

---

## Database Schema

### Hospital Table (Existing)
```sql
hospital_hospital
├── id (INTEGER PRIMARY KEY)
├── name (VARCHAR UNIQUE)
├── registration_number (VARCHAR UNIQUE)
├── address (VARCHAR)
├── city (VARCHAR)
├── state (VARCHAR)
├── country (VARCHAR)
├── postal_code (VARCHAR)
├── phone_number (VARCHAR)
├── email (VARCHAR)
├── website (VARCHAR)
├── is_verified (BOOLEAN)
├── is_active (BOOLEAN)
├── admin_id (INTEGER FK to auth_user)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

### BloodRequest Table (New)
```sql
hospital_bloodrequest
├── id (INTEGER PRIMARY KEY)
├── hospital_id (INTEGER FK to hospital_hospital) [INDEX]
├── blood_type (VARCHAR) [INDEX]
├── units_needed (DECIMAL)
├── urgency_level (VARCHAR) [INDEX]
├── status (VARCHAR) [INDEX]
├── description (TEXT NULL)
├── created_at (TIMESTAMP) [INDEX in composite]
└── fulfilled_at (TIMESTAMP NULL)

Composite Index: (hospital_id, status)
```

---

## Environment-Specific Migration

### Development
```bash
# In development, migrations are straightforward
python manage.py makemigrations hospital
python manage.py migrate hospital
python manage.py runserver
```

### Staging
```bash
# Test migrations on staging first
# Set DEBUG=False in settings

python manage.py migrate hospital
python manage.py test hospital

# If tests pass, ready for production
```

### Production
```bash
# 1. Backup database
pg_dump bloodchain_db > backup_prod_$(date +%Y%m%d_%H%M%S).sql

# 2. Review migrations
python manage.py showmigrations hospital

# 3. Test on production clone first (if possible)
# 4. Apply migrations during maintenance window
python manage.py migrate hospital

# 5. Monitor for errors
tail -f logs/error.log

# 6. If issue, restore backup
psql bloodchain_db < backup_prod_20240115_103000.sql
```

---

## Checking Migration Health

```bash
# 1. Check for unapplied migrations
python manage.py migrate --check

# 2. Check for missing migrations
python manage.py makemigrations --dry-run --check

# 3. Check model validity
python manage.py check

# 4. Show all migration info
python manage.py showmigrations --plan

# 5. Verify SQL that will execute
python manage.py sqlmigrate hospital 0002_bloodrequest
```

---

## Git & Version Control

### Committing Migrations

```bash
# After creating migration
git add hospital/migrations/0002_bloodrequest.py
git commit -m "Add BloodRequest model for hospital blood tracking"

# Before deploying
git pull origin main
python manage.py makemigrations --check  # Ensure no unmigrated changes
```

### Merging Migration Conflicts

```bash
# If two branches create migrations:
# Branch A: 0002_feature_a.py
# Branch B: 0002_feature_b.py

# This creates conflict on branch name

# Solution:
# 1. Rebase one branch
# 2. Rename 0002 to 0003 in one branch
# 3. Update dependencies in later migrations

# Better: Use feature branches that get merged before migrations
```

---

## Performance Impact

### Migration Performance
```bash
# Large data migrations can take time
# Monitor with:
PYTHONUNBUFFERED=1 python manage.py migrate hospital

# For large tables (1M+ rows):
# Add --no-atomic flag to avoid table locking
python manage.py migrate hospital --no-atomic
```

### Index Performance
BloodRequest has indexes on:
- blood_type: For filtering by blood type
- urgency_level: For filtering by urgency
- status: For filtering open/fulfilled/cancelled
- (hospital_id, status): For hospital-specific queries

These indexes improve query performance but slow down inserts slightly.

---

## Archive & Cleanup

### After Many Migrations

```bash
# List old migrations
python manage.py showmigrations hospital

# If confident migrations are stable:
# Squash old migrations (Django 1.11+)
python manage.py squashmigrations hospital 0001 0010

# This creates:
# hospital/migrations/0001_squashed_0010_field_name.py
# And allows deleting original files

# Benefits:
# ✓ Cleaner history
# ✓ Faster initial setup of new databases
# ✓ Easier to understand current state
```

---

## Quick Reference Table

| Task | Command |
|------|---------|
| Create migrations | `python manage.py makemigrations hospital` |
| Apply migrations | `python manage.py migrate hospital` |
| Check status | `python manage.py showmigrations hospital` |
| Review SQL | `python manage.py sqlmigrate hospital 0002` |
| Rollback | `python manage.py migrate hospital 0001` |
| Rollback all | `python manage.py migrate hospital zero` |
| Preview changes | `python manage.py makemigrations --dry-run` |
| Check health | `python manage.py check` |
| Reset sequences | `python manage.py sqlsequencereset hospital` |

---

## Next Steps

1. Run `python manage.py makemigrations hospital`
2. Review the generated 0002_bloodrequest.py file
3. Run `python manage.py migrate hospital`
4. Verify table created: `python manage.py dbshell`
5. Test API endpoints
6. Create test blood requests

---

**Happy Migrating! 🗄️**

For issues, see troubleshooting section above.
