# 🚀 Deployment Guide for Knowledge Assistant

## 📋 Pre-Deployment Checklist

### **Required Before Push:**

#### 🔐 1. Security Configuration
- [ ] Generated secure secrets using `python generate_secrets.py`
- [ ] Created `.env` file with real values (DO NOT commit)
- [ ] Obtained Google Gemini API key
- [ ] Set strong passwords for databases
- [ ] Configured CORS origins for production

#### 📦 2. Dependencies & Environment
- [ ] Tested with `python test_system.py`
- [ ] All dependencies in requirements.txt work
- [ ] Docker and Docker Compose installed
- [ ] PostgreSQL accessible (local or cloud)
- [ ] Redis accessible (local or cloud)

#### 🗄️ 3. Database Setup
- [ ] PostgreSQL database created
- [ ] Database user with proper permissions
- [ ] Network access configured
- [ ] Backup strategy planned

#### 🌐 4. Infrastructure
- [ ] Domain name registered (if needed)
- [ ] SSL certificate obtained
- [ ] Reverse proxy configured (Nginx)
- [ ] Firewall rules configured
- [ ] Monitoring setup planned

---

## 🏗️ Deployment Options

### **Option 1: Docker Compose (Recommended)**

#### Development Deployment:
```bash
# Clone repository
git clone <your-repo-url>
cd py_fast

# Setup environment
cp .env.example .env
# Edit .env with your values

# Start services
docker-compose up -d

# Verify deployment
python test_system.py
```

#### Production Deployment:
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Check services
docker-compose -f docker-compose.prod.yml ps
```

### **Option 2: Cloud Deployment**

#### **AWS Deployment:**
```bash
# Using AWS ECS/Fargate
aws ecr create-repository --repository-name knowledge-assistant
docker build -t knowledge-assistant .
docker tag knowledge-assistant:latest <aws-account>.dkr.ecr.<region>.amazonaws.com/knowledge-assistant:latest
docker push <aws-account>.dkr.ecr.<region>.amazonaws.com/knowledge-assistant:latest
```

#### **Google Cloud Run:**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/knowledge-assistant
gcloud run deploy --image gcr.io/PROJECT-ID/knowledge-assistant --platform managed
```

#### **Digital Ocean App Platform:**
```yaml
# app.yaml
name: knowledge-assistant
services:
- name: api
  source_dir: /
  github:
    repo: your-username/knowledge-assistant
    branch: main
  run_command: uvicorn main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
  env:
  - key: DATABASE_URL
    value: ${db.DATABASE_URL}
databases:
- engine: PG
  name: knowledge-assistant-db
  num_nodes: 1
  size: db-s-dev-database
  version: "13"
```

### **Option 3: Manual Server Deployment**

#### **Ubuntu/Debian Server:**
```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip nginx postgresql redis-server

# Create application user
sudo useradd -m -s /bin/bash knowledge-assistant
sudo su - knowledge-assistant

# Clone and setup
git clone <your-repo-url>
cd knowledge-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-prod.txt

# Create systemd service
sudo tee /etc/systemd/system/knowledge-assistant.service > /dev/null <<EOF
[Unit]
Description=Knowledge Assistant API
After=network.target

[Service]
Type=exec
User=knowledge-assistant
WorkingDirectory=/home/knowledge-assistant/knowledge-assistant
Environment=PATH=/home/knowledge-assistant/knowledge-assistant/venv/bin
ExecStart=/home/knowledge-assistant/knowledge-assistant/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable knowledge-assistant
sudo systemctl start knowledge-assistant
```

---

## 🔧 Environment Variables for Production

### **Required Environment Variables:**
```bash
# Core Application
DATABASE_URL=postgresql://username:password@host:5432/database
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_generated_secret_key

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
JWT_SECRET_KEY=your_jwt_secret

# File Storage
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=10485760

# External Services
REDIS_URL=redis://username:password@host:6379/0
SENTRY_DSN=your_sentry_dsn_for_error_tracking

# Email (if notifications needed)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### **Optional Environment Variables:**
```bash
# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true

# Performance
WORKERS=4
WORKER_CLASS=uvicorn.workers.UvicornWorker
WORKER_CONNECTIONS=1000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Features
ENABLE_PUBLIC_REGISTRATION=false
ENABLE_FILE_SHARING=true
ENABLE_ANALYTICS=true
```

---

## 📊 Monitoring & Health Checks

### **Health Check Endpoints:**
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system status
- `GET /metrics` - Prometheus metrics

### **Monitoring Setup:**
```bash
# Docker monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Endpoints:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001
# - Application: http://localhost:8000
```

---

## 🔒 Security Hardening

### **Application Security:**
1. **Input Validation:** All endpoints validate input
2. **Rate Limiting:** Implement with Redis
3. **CORS:** Configure allowed origins
4. **File Upload:** Validate file types and sizes
5. **SQL Injection:** Prevented with SQLAlchemy ORM

### **Infrastructure Security:**
```bash
# Firewall rules (UFW)
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### **Database Security:**
```sql
-- Create dedicated database user
CREATE USER knowledge_assistant WITH PASSWORD 'strong_password';
CREATE DATABASE knowledge_assistant OWNER knowledge_assistant;
GRANT ALL PRIVILEGES ON DATABASE knowledge_assistant TO knowledge_assistant;
```

---

## 📈 Performance Optimization

### **Database Optimization:**
```sql
-- Add indexes for better performance
CREATE INDEX idx_documents_is_public ON documents(is_public);
CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_public_shares_token ON public_shares(share_token);
```

### **Application Optimization:**
```python
# Connection pooling
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 30
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_POOL_RECYCLE = 1800
```

### **Caching Strategy:**
```python
# Redis caching for embeddings and search results
CACHE_EMBEDDINGS = True
CACHE_SEARCH_RESULTS = True
CACHE_TTL = 3600  # 1 hour
```

---

## 🚨 Backup Strategy

### **Database Backup:**
```bash
# Create backup script
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U knowledge_assistant knowledge_assistant > $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### **File Backup:**
```bash
# Backup uploaded files
rsync -av /app/uploads/ /backups/uploads/
```

---

## 📞 Troubleshooting

### **Common Issues:**

1. **Database Connection Failed:**
   ```bash
   # Check database status
   docker-compose logs postgres
   # Test connection
   psql -h localhost -U postgres -d knowledge_assistant -c "SELECT 1;"
   ```

2. **Gemini API Errors:**
   ```bash
   # Verify API key
   curl -H "Authorization: Bearer $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1/models
   ```

3. **File Upload Issues:**
   ```bash
   # Check permissions
   ls -la uploads/
   # Check disk space
   df -h
   ```

4. **High Memory Usage:**
   ```bash
   # Monitor resources
   docker stats
   # Check application logs
   docker-compose logs backend
   ```

### **Log Analysis:**
```bash
# View application logs
tail -f logs/app.log

# Check error patterns
grep -i error logs/app.log | tail -20

# Monitor API responses
grep -E "POST|GET" logs/access.log | tail -10
```

---

## 📈 Scaling Considerations

### **Horizontal Scaling:**
- Load balancer (Nginx, HAProxy)
- Multiple application instances
- Database read replicas
- CDN for static files

### **Vertical Scaling:**
- Increase server resources
- Optimize database queries
- Implement caching layers
- Use background task queues

### **Cloud Auto-scaling:**
```yaml
# Kubernetes deployment example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: knowledge-assistant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: knowledge-assistant
  template:
    metadata:
      labels:
        app: knowledge-assistant
    spec:
      containers:
      - name: api
        image: knowledge-assistant:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

This deployment guide covers everything needed for a production-ready Knowledge Assistant deployment!