# Blood Tracking App - Migration Guide

## Quick Migration (First Time)

### 1. Generate Migration
```bash
python manage.py makemigrations blood_tracking
```

**Output:**
```
Migrations for 'blood_tracking':
  blood_tracking/migrations/0003_bloodunit.py
    - Create model BloodUnit
```

### 2. Review Migration File
```bash
cat blood_tracking/migrations/0003_bloodunit.py
```

You'll see:
- BloodUnit model creation
- Field definitions with types
- Index creation for performance
- Foreign key relationships

### 3. Apply Migration
```bash
python manage.py migrate blood_tracking
```

**Output:**
```
Operations to perform:
  Apply all migrations: blood_tracking
Running migrations:
  Applying blood_tracking.0003_bloodunit... OK
```

### 4. Verify Database Table
```bash
python manage.py dbshell

# In PostgreSQL shell:
\dt blood_tracking_bloodunit
```

You should see table with columns:
- id
- unit_id
- donor_id
- blood_type
- collection_date
- expiry_date
- current_location_id
- status
- hiv_test
- hepatitis_test
- blockchain_tx_hash
- status_history
- created_at
- updated_at

---

## Understanding the Migration

### Generated Migration Structure

```python
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('blood_tracking', '0002_previous_migration'),  # Depends on previous
        ('donor', '0001_initial'),    # Depends on donor app
        ('hospital', '0001_initial'),  # Depends on hospital app
    ]

    operations = [
        migrations.CreateModel(
            name='BloodUnit',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('unit_id', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('blood_type', models.CharField(choices=[...], max_length=3)),
                ('collection_date', models.DateTimeField()),
                ('expiry_date', models.DateTimeField()),
                ('status', models.CharField(default='collected', ...)),
                ('hiv_test', models.BooleanField(default=False)),
                ('hepatitis_test', models.BooleanField(default=False)),
                ('blockchain_tx_hash', models.CharField(blank=True, null=True, ...)),
                ('status_history', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_location', models.ForeignKey(..., to='hospital.Hospital')),
                ('donor', models.ForeignKey(..., to='donor.Donor')),
            ],
            options={
                'ordering': ['-collection_date'],
            },
        ),
        migrations.AddIndex(
            model_name='bloodunit',
            index=models.Index(fields=['blood_type'], name='blood_track_blood_t_idx'),
        ),
        migrations.AddIndex(
            model_name='bloodunit',
            index=models.Index(fields=['status'], name='blood_track_status_idx'),
        ),
        migrations.AddIndex(
            model_name='bloodunit',
            index=models.Index(fields=['donor', 'collection_date'], name='blood_track_donor_id_coll_date_idx'),
        ),
        migrations.AddIndex(
            model_name='bloodunit',
            index=models.Index(fields=['current_location', 'status'], name='blood_track_current_l_status_idx'),
        ),
    ]
```

### What It Does

1. **Creates table:** `blood_tracking_bloodunit`
2. **Adds fields:** 14 columns including FK relationships
3. **Creates indexes:** 4 indexes for query optimization
4. **Sets defaults:** status='collected', timestamps auto
5. **Enables constraints:** Unique unit_id, required fields

---

## Common Migration Scenarios

### Scenario 1: Fresh Installation (First Time)

```bash
# 1. Check if migrations exist
python manage.py showmigrations blood_tracking

# Should show:
# blood_tracking
#  [ ] 0001_initial
#  [ ] 0002_blooddonation_bloodtransfer
#  [ ] 0003_bloodunit

# 2. Apply all migrations
python manage.py migrate blood_tracking

# 3. Verify
python manage.py showmigrations blood_tracking

# Should show:
# blood_tracking
#  [X] 0001_initial
#  [X] 0002_blooddonation_bloodtransfer
#  [X] 0003_bloodunit

# 4. Test creating a unit
python manage.py shell
>>> from blood_tracking.models import BloodUnit
>>> BloodUnit.objects.count()
0  # Empty initially
```

### Scenario 2: Adding New Field to BloodUnit

```bash
# 1. Update blood_tracking/models.py
# Add new field to BloodUnit class:
# quality_score = models.IntegerField(default=0)

# 2. Create migration (Django detects change)
python manage.py makemigrations blood_tracking

# Creates: blood_tracking/migrations/0004_bloodunit_quality_score.py

# 3. Review migration
cat blood_tracking/migrations/0004_bloodunit_quality_score.py

# 4. Apply migration
python manage.py migrate blood_tracking

# 5. Verify field exists
python manage.py shell
>>> from blood_tracking.models import BloodUnit
>>> BloodUnit._meta.get_field('quality_score')
<django.db.models.fields.IntegerField: quality_score>
```

### Scenario 3: Changing Field Type

```bash
# Example: Change status choices

# 1. Update model with new choices
# OLD: ('transfused', 'Transfused'), ('expired', 'Expired')
# NEW: ('transfused', 'Transfused'), ('expired', 'Expired'), ('quarantine', 'Quarantine')

# 2. Create migration
python manage.py makemigrations blood_tracking

# Django creates: 0005_alter_bloodunit_status.py
# (only AlterField, no data loss)

# 3. Apply migration
python mange.py migrate blood_tracking

# No data migration needed for choice additions
```

### Scenario 4: Rename a Field

```bash
# Example: Rename 'current_location' to 'storage_location'

# 1. Update model - change field name
# OLD: current_location = models.ForeignKey(Hospital, ...)
# NEW: storage_location = models.ForeignKey(Hospital, ...)

# 2. Create migration
python manage.py makemigrations blood_tracking

# Django detects as field removal + addition
# Creates: 0006_auto_rename.py with RenameField

# Or manually create:
python manage.py makemigrations blood_tracking --empty --name rename_location

# Then edit to:
migrations.RenameField(
    model_name='bloodunit',
    old_name='current_location',
    new_name='storage_location',
)

# 3. Apply migration
python manage.py migrate blood_tracking

# 4. Update code references
# Old: unit.current_location
# New: unit.storage_location
```

### Scenario 5: Rollback Changes

```bash
# 1. View migration history
python manage.py showmigrations blood_tracking

# Output:
# blood_tracking
#  [X] 0001_initial
#  [X] 0002_blooddonation_bloodtransfer
#  [X] 0003_bloodunit
#  [X] 0004_bloodunit_quality_score

# 2. Rollback to specific migration
python manage.py migrate blood_tracking 0003_bloodunit

# Now only 0001-0003 are applied
# quality_score field is removed from database

# 3. Or rollback all migrations
python manage.py migrate blood_tracking zero

# Removes all blood_tracking tables

# 4. Check status
python manage.py showmigrations blood_tracking

# All should show [ ] (not applied)
```

---

## Migration Commands Reference

### Create Migrations
```bash
# Auto-detect changes
python manage.py makemigrations blood_tracking

# With custom name
python manage.py makemigrations blood_tracking --name add_field_xyz

# Preview without creating
python manage.py makemigrations --dry-run blood_tracking

# Verbose output
python manage.py makemigrations blood_tracking --verbosity 3

# Empty migration for manual edits
python manage.py makemigrations blood_tracking --empty --name custom_migration
```

### Apply Migrations
```bash
# Apply all pending
python manage.py migrate blood_tracking

# Apply specific migration
python manage.py migrate blood_tracking 0003_bloodunit

# Preview what would be applied
python manage.py migrate blood_tracking --plan

# Verbose output
python manage.py migrate blood_tracking --verbosity 3

# Apply without atomic transaction (for long migrations)
python manage.py migrate blood_tracking --no-atomic
```

### Show Migration Status
```bash
# Show all migrations
python manage.py showmigrations blood_tracking

# Show planned migrations
python manage.py showmigrations --plan blood_tracking

# Show all apps
python manage.py showmigrations
```

### Inspect Migrations
```bash
# Show SQL for migration
python manage.py sqlmigrate blood_tracking 0003_bloodunit

# Check if all migrations applied
python manage.py migrate --check

# Show current state
python manage.py dbshell
# Then: \dt blood_tracking_bloodunit
# Or: SELECT * FROM django_migrations WHERE app='blood_tracking';
```

---

## Database Schema After Migration

### blood_tracking_bloodunit Table

```sql
CREATE TABLE blood_tracking_bloodunit (
    id bigserial PRIMARY KEY,
    unit_id uuid UNIQUE NOT NULL,
    donor_id integer NOT NULL REFERENCES donor_donor(id),
    blood_type varchar(3) NOT NULL,
    collection_date timestamp NOT NULL,
    expiry_date timestamp NOT NULL,
    current_location_id integer REFERENCES hospital_hospital(id),
    status varchar(20) NOT NULL DEFAULT 'collected',
    hiv_test boolean NOT NULL DEFAULT false,
    hepatitis_test boolean NOT NULL DEFAULT false,
    blockchain_tx_hash varchar(256) NULL,
    status_history jsonb NOT NULL DEFAULT '[]'::jsonb,
    created_at timestamp NOT NULL,
    updated_at timestamp NOT NULL
);

-- Indexes created
CREATE INDEX blood_track_blood_t_idx ON blood_tracking_bloodunit(blood_type);
CREATE INDEX blood_track_status_idx ON blood_tracking_bloodunit(status);
CREATE INDEX blood_track_donor_id_coll_date_idx ON blood_tracking_bloodunit(donor_id, collection_date);
CREATE INDEX blood_track_current_l_status_idx ON blood_tracking_bloodunit(current_location_id, status);
```

### Foreign Keys

```sql
ALTER TABLE blood_tracking_bloodunit
ADD CONSTRAINT fk_donor
FOREIGN KEY (donor_id) REFERENCES donor_donor(id) ON DELETE CASCADE;

ALTER TABLE blood_tracking_bloodunit
ADD CONSTRAINT fk_location
FOREIGN KEY (current_location_id) REFERENCES hospital_hospital(id) ON DELETE SET NULL;
```

---

## Environment-Specific Migration

### Development
```bash
# Fresh start
python manage.py migrate
python manage.py createsuperuser
python manage.py shell

# Create test data
>>> from donor.models import Donor
>>> from blood_tracking.models import BloodUnit
>>> from datetime import datetime, timedelta
>>> # Create test blood unit
>>> donor = Donor.objects.first()
>>> unit = BloodUnit.objects.create(
...     donor=donor,
...     blood_type=donor.blood_type,
...     collection_date=datetime.now(),
...     expiry_date=datetime.now() + timedelta(days=35)
... )
>>> exit()
```

### Staging
```bash
# Test migrations on staging environment
python manage.py migrate blood_tracking

# Run tests
python manage.py test blood_tracking

# If tests fail, rollback:
python manage.py migrate blood_tracking zero
python manage.py migrate blood_tracking 0002_blooddonation_bloodtransfer
```

### Production
```bash
# Backup database first!
pg_dump bloodchain_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Apply migrations during maintenance window
python manage.py migrate blood_tracking

# Monitor for errors
tail -f logs/error.log

# If issues, restore backup
psql bloodchain_db < backup_20260402_103000.sql
```

---

## Troubleshooting Migrations

### Issue: "No migrations to apply"
```bash
# Check if all migrations already applied
python manage.py showmigrations blood_tracking

# Should show [X] for all

# If you made model changes, ensure migration created:
python manage.py makemigrations blood_tracking

# Nothing created? Check for syntax errors in models.py:
python manage.py check
```

### Issue: "table already exists"
```bash
# Migration trying to create table that exists
# Causes: Database out of sync with migration state

# Check status
python manage.py showmigrations blood_tracking

# If status shows as applied but error occurs:
python manage.py migrate blood_tracking --fake 0003_bloodunit

# Then continue:
python manage.py migrate blood_tracking
```

### Issue: "column does not exist"
```bash
# Old code trying to access field that hasn't been migrated

# Check pending migrations
python manage.py showmigrations blood_tracking

# Apply all pending:
python manage.py migrate blood_tracking

# Verify:
python manage.py migrate --check
```

### Issue: "foreign key constraint failed"
```bash
# Usually happens when:
# 1. Donor referenced by BloodUnit doesn't exist
# 2. Hospital referenced doesn't exist

# Check your test data:
python manage.py shell
>>> from donor.models import Donor
>>> Donor.objects.count()  # Should be > 0

# If empty, create a test donor:
>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('testdonor', 'test@example.com', 'pass')
>>> from datetime import date
>>> donor = Donor.objects.create(
...     user=user,
...     blood_type='O+',
...     phone_number='+1-617-555-0001',
...     location='Boston, MA',
...     date_of_birth=date(1990, 1, 1)
... )
```

### Issue: "duplicate key value violates constraint"
```bash
# Usually: Duplicate unit_id or other unique field

# Check:
python manage.py shell
>>> from blood_tracking.models import BloodUnit
>>> units = BloodUnit.objects.values('unit_id').annotate(Count('unit_id')).filter(unit_id__count__gt=1)
>>> units  # Shows duplicates

# Remove duplicates (if safe):
>>> BloodUnit.objects.filter(unit_id='...', id__gt=1).delete()

# Or re-initialize data
```

### Issue: "no such table"
```bash
# Migrations haven't been applied yet

# Apply:
python manage.py migrate blood_tracking

# Or check migration status:
python manage.py showmigrations blood_tracking
```

---

## Best Practices

### 1. Always Review Generated Migrations
```bash
# Before applying
git diff blood_tracking/migrations/0003_bloodunit.py

# And check SQL
python manage.py sqlmigrate blood_tracking 0003_bloodunit
```

### 2. Test Locally First
```bash
# On development database
python manage.py migrate blood_tracking

# Test API
python manage.py runserver

# curl -X GET http://localhost:8000/api/blood-tracking/units/
```

### 3. Backup Before Production
```bash
# PostgreSQL backup
pg_dump bloodchain_db > backup.sql

# Apply migrations
python manage.py migrate blood_tracking

# If issue, restore:
psql bloodchain_db < backup.sql
```

### 4. Atomic Transactions
```bash
# Migrations wrapped in transaction (default)
# If migration fails, everything rolled back

# For long migrations, disable atomic:
python manage.py migrate blood_tracking --no-atomic
```

### 5. Never Delete Migrations
```
❌ WRONG: Delete 0003_bloodunit.py after it's applied
✅ RIGHT: Create new migration 0004_revert_xyz.py to undo

Deleting migrations breaks other developers' databases!
```

### 6. Keep Migrations Small
```
❌ WRONG: One migration file with 5 model changes
✅ RIGHT: Separate migrations for each change
```

---

## Git & Version Control

### Committing Migrations
```bash
# After creating migration
git add blood_tracking/migrations/0003_bloodunit.py
git commit -m "Add BloodUnit model for individual unit tracking"
```

### Before Deployment
```bash
# Ensure nothing needs migrating
python manage.py makemigrations --check

# Exit code 0 = all migrated
# Exit code 1 = migrations pending
```

### Merging Migration Conflicts

If two branches create migrations (0003 in both):

```bash
# Resolve by renaming one
# Branch A: 0003_feature_a.py
# Branch B: 0003_feature_b.py → rename to 0004_feature_b.py

# Update dependencies in 0004:
class Migration(migrations.Migration):
    dependencies = [
        ('blood_tracking', '0003_feature_a'),  # Depend on A
    ]
```

---

## Performance Tuning

### Index Strategy
```python
# Created indexes:
# 1. blood_type - frequent filtering
#    GET /units/by_blood_type/?blood_type=O+

# 2. status - frequent filtering
#    GET /units/?search=collected

# 3. (donor_id, collection_date) - donor queries
#    unit.donor.blood_units (FK reverse)

# 4. (current_location_id, status) - inventory at location
#    GET /units/units_at_location/
```

### Query Optimization
```python
# Use select_related() for FK queries
units = BloodUnit.objects.select_related(
    'donor',
    'current_location'
).filter(status='storage')

# Avoids N+1 queries
```

---

## Cleanup

### After Many Migrations
```bash
# Squash old migrations to reduce files
python manage.py squashmigrations blood_tracking 0001 0010

# Creates: 0001_squashed_0010_xxx.py
# Can delete original migration files

# Allows faster fresh database setup
```

---

## Quick Reference Table

| Task | Command |
|------|---------|
| Create migrations | `python manage.py makemigrations blood_tracking` |
| Apply migrations | `python manage.py migrate blood_tracking` |
| View status | `python manage.py showmigrations blood_tracking` |
| Show SQL | `python manage.py sqlmigrate blood_tracking 0003` |
| Rollback | `python manage.py migrate blood_tracking 0002` |
| Rollback all | `python manage.py migrate blood_tracking zero` |
| Check status | `python manage.py migrate --check` |
| Empty migration | `python manage.py makemigrations blood_tracking --empty --name xyz` |
| Review migration | `git diff blood_tracking/migrations/0003_bloodunit.py` |

---

## Next Steps

1. Run initial migration: `python manage.py migrate blood_tracking`
2. Create test data
3. Test API endpoints
4. Verify admin interface
5. Deploy to production with backup

---

**Happy Migrating! 🗄️**

For more help, see GETTING_STARTED.md or API_DOCUMENTATION.md
