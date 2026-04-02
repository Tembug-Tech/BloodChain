# BloodChain Deployment Guide

This guide covers deploying BloodChain to production using industry best practices.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Traditional Server Deployment](#traditional-server-deployment)
5. [Database Migration](#database-migration)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Security Hardening](#security-hardening)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Scaling](#scaling)

---

## Pre-Deployment Checklist

- [ ] All tests passing locally
- [ ] SECRET_KEY changed and kept secure
- [ ] DEBUG set to False
- [ ] Allowed hosts configured
- [ ] Database credentials secured
- [ ] Static files configured
- [ ] Blockchain provider configured
- [ ] Email backend configured
- [ ] CORS origins configured
- [ ] SSL certificate obtained
- [ ] Monitoring tools set up
- [ ] Backup strategy implemented

---

## Environment Configuration

### 1. Production `.env` File

Create `.env` for production (never commit to git):

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your_very_secret_key_here_min_50_chars
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@db.yourdomain.com:5432/bloodchain_prod

# Blockchain
WEB3_PROVIDER_URI=https://sepolia.infura.io/v3/YOUR_PRODUCTION_KEY
BLOOD_UNIT_CONTRACT_ADDRESS=0x...
BLOOD_UNIT_CONTRACT_ABI='[...]'

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_SECURITY_POLICY=default-src 'self'

# Logging
LOG_LEVEL=INFO
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 2. Securing Environment Variables

```bash
# Create .env with restricted permissions
touch .env
chmod 600 .env  # Only owner can read/write

# Never commit .env
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

### 3. Generate Secure SECRET_KEY

```python
# In Python shell:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## Docker Deployment

### 1. Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["gunicorn", "bloodchain.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### 2. docker-compose.yml

Create `docker-compose.yml`:

```yaml
version: '3.9'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: bloodchain-db
    environment:
      POSTGRES_DB: bloodchain_prod
      POSTGRES_USER: bloodchain
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bloodchain"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Django Application
  web:
    build: .
    container_name: bloodchain-web
    command: >
      sh -c "python manage.py migrate &&
             gunicorn bloodchain.wsgi:application --bind 0.0.0.0:8000 --workers 4"
    environment:
      DEBUG: "False"
      DATABASE_URL: postgresql://bloodchain:${DB_PASSWORD}@db:5432/bloodchain_prod
      WEB3_PROVIDER_URI: ${WEB3_PROVIDER_URI}
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_HOSTS: ${ALLOWED_HOSTS}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - static_volume:/app/staticfiles
    restart: unless-stopped

  # Redis Cache (Optional)
  redis:
    image: redis:7-alpine
    container_name: bloodchain-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: bloodchain-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
      - static_volume:/app/staticfiles:ro
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_volume:
```

### 3. Deploy with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

---

## Traditional Server Deployment

### 1. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    ufw \
    git \
    curl

# Fedora/RHEL
sudo dnf install -y \
    python3.11 \
    python3.11-devel \
    postgresql \
    nginx \
    git
```

### 2. Setup Application User

```bash
# Create dedicated user
sudo useradd -m -s /bin/bash bloodchain
sudo usermod -aG sudo bloodchain
sudo su - bloodchain
```

### 3. Clone Repository

```bash
cd ~
git clone https://github.com/yourorg/bloodchain.git
cd bloodchain
```

### 4. Setup Python Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 5. Configure Application

```bash
# Create .env file
cp .env.example .env
nano .env  # Edit with production values

# Create directories
mkdir -p logs
mkdir -p staticfiles
mkdir -p media

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Setup Gunicorn Service

Create `/etc/systemd/system/bloodchain.service`:

```ini
[Unit]
Description=BloodChain Django Application
After=network.target postgresql.service

[Service]
User=bloodchain
Group=www-data
WorkingDirectory=/home/bloodchain/bloodchain
Environment="PATH=/home/bloodchain/bloodchain/venv/bin"
EnvironmentFile=/home/bloodchain/bloodchain/.env
ExecStart=/home/bloodchain/bloodchain/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:/run/gunicorn.sock \
    --timeout 30 \
    --access-logfile /home/bloodchain/bloodchain/logs/access.log \
    --error-logfile /home/bloodchain/bloodchain/logs/error.log \
    bloodchain.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bloodchain
sudo systemctl start bloodchain
sudo systemctl status bloodchain
```

---

## Database Migration

### PostgreSQL Setup

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE bloodchain_prod;
CREATE USER bloodchain WITH PASSWORD 'secure_password';
ALTER ROLE bloodchain SET client_encoding TO 'utf8';
ALTER ROLE bloodchain SET default_transaction_isolation TO 'read committed';
ALTER ROLE bloodchain SET default_transaction_deferrable TO on;
ALTER ROLE bloodchain SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE bloodchain_prod TO bloodchain;
\q
```

### Run Migrations

```bash
python manage.py migrate
python manage.py migrate blood_tracking
python manage.py migrate donor
python manage.py migrate hospital
```

### Backup Strategy

```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/home/bloodchain/backups"
DB_NAME="bloodchain_prod"
DB_USER="bloodchain"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Create backup
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_backup_$TIMESTAMP.sql.gz"
```

Schedule with cron:

```bash
# Add to crontab (daily at 2 AM)
crontab -e

# Add line:
0 2 * * * /home/bloodchain/bloodchain/backup_db.sh
```

---

## SSL/TLS Configuration

### Using Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates stored in:
# /etc/letsencrypt/live/yourdomain.com/
```

### Nginx Configuration

Create `/etc/nginx/sites-available/bloodchain`:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/javascript application/json;
    gzip_min_length 1000;
    
    # Static files
    location /static/ {
        alias /home/bloodchain/bloodchain/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /home/bloodchain/bloodchain/media/;
        expires 7d;
    }
    
    # Proxy to Gunicorn
    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Enable and test:

```bash
sudo ln -s /etc/nginx/sites-available/bloodchain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Auto-Renewal

```bash
# Test renewal process
sudo certbot renew --dry-run

# Enable auto-renewal timer
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Security Hardening

### 1. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny all other
sudo ufw default deny incoming
sudo ufw default allow outgoing

# View rules
sudo ufw status
```

### 2. Django Security Settings

Update `settings.py`:

```python
# Security
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/bloodchain/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]
```

### 3. Dependencies Security

```bash
# Check for vulnerabilities
pip install safety
safety check

# Update packages
pip install --upgrade -r requirements.txt
```

---

## Monitoring & Logging

### 1. Application Logging

```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/home/bloodchain/bloodchain/logs/django.log',
            'maxBytes': 1024 * 1024 * 100,  # 100 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### 2. Sentry Integration

```bash
# Install Sentry SDK
pip install sentry-sdk 

# Configure in settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False
)
```

### 3. Monitoring Tools

```bash
# Install monitoring tools
pip install django-extensions django-silk django-debug-toolbar

# Monitor process
# Use htop, top, or Prometheus
sudo apt-get install -y prometheus grafana-server
```

---

## Backup & Recovery

### Automated Backups

Create backup script:

```bash
#!/bin/bash
# /usr/local/bin/backup_bloodchain.sh

BACKUP_DIR="/backups/bloodchain"
APP_DIR="/home/bloodchain/bloodchain"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U bloodchain bloodchain_prod | gzip > $BACKUP_DIR/db_$TIMESTAMP.sql.gz

# Application files backup
tar -czf $BACKUP_DIR/app_$TIMESTAMP.tar.gz \
    --exclude='venv' \
    --exclude='.git' \
    --exclude='media' \
    --exclude='logs' \
    $APP_DIR

# Media files backup
tar -czf $BACKUP_DIR/media_$TIMESTAMP.tar.gz $APP_DIR/media

# Keep only 30 days
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed - $TIMESTAMP"
```

Schedule daily:

```bash
sudo crontab -e

# Add line (3 AM daily)
0 3 * * * /usr/local/bin/backup_bloodchain.sh
```

### Disaster Recovery

```bash
# Restore database
gunzip < /backups/bloodchain/db_20260402_030000.sql.gz | psql -U bloodchain bloodchain_prod

# Restore application
cd /home/bloodchain
tar -xzf /backups/bloodchain/app_20260402_030000.tar.gz

# Restore media
tar -xzf /backups/bloodchain/media_20260402_030000.tar.gz
```

---

## Scaling

### Horizontal Scaling with Load Balancing

```nginx
# Upstream backend servers
upstream bloodchain_backend {
    server 10.0.1.10:8000;
    server 10.0.1.11:8000;
    server 10.0.1.12:8000;
    
    # Health check
    check interval=3000 rise=2 fall=5 timeout=1000 type=http;
    check_http_send "GET /health HTTP/1.0\r\n\r\n";
    check_http_expect_alive http_2xx;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://bloodchain_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Database Scaling

```bash
# Set up PostgreSQL replication
# See PostgreSQL wal-based replication documentation

# Or use managed database services:
# - AWS RDS for PostgreSQL
# - Azure Database for PostgreSQL
# - Google Cloud SQL
```

### Caching Layer

```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

---

## Final Checklist

- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configured
- [ ] SECRET_KEY changed
- [ ] Database credentials secured
- [ ] SSL certificates installed
- [ ] Backups automated
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Firewall configured
- [ ] Security headers configured
- [ ] CORS origins configured
- [ ] Static files collected
- [ ] Environment variables set
- [ ] Tests passing
- [ ] Health checks working
- [ ] Recovery procedures tested

---

**Last Updated:** 2026-04-02

For more help, see [SETUP_GUIDE.md](SETUP_GUIDE.md)
