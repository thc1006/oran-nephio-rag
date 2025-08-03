# O-RAN × Nephio RAG System - Production Deployment Guide

This comprehensive guide covers all aspects of deploying the O-RAN × Nephio RAG System to production environments, from local development to enterprise-scale cloud deployments.

## Table of Contents

- [Overview](#overview)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Environment Setup](#environment-setup)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Monitoring & Observability](#monitoring--observability)
- [Security Considerations](#security-considerations)
- [Performance Optimization](#performance-optimization)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Overview

The O-RAN × Nephio RAG System supports multiple deployment architectures:

- **Single Node**: Development and testing environments
- **Docker Compose**: Small to medium production deployments
- **Kubernetes**: Large-scale, cloud-native deployments
- **Hybrid Cloud**: Multi-cloud and edge deployments

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   App Pod   │  │   App Pod   │  │   App Pod   │     │
│  │             │  │             │  │             │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Redis     │  │  Vector DB  │  │ Monitoring  │     │
│  │  Cluster    │  │   Storage   │  │    Stack    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## Pre-Deployment Checklist

### Infrastructure Requirements

#### Minimum Resources (Single Instance)
- **CPU**: 2 cores (x86_64 or ARM64)
- **Memory**: 4GB RAM
- **Storage**: 10GB available disk space
- **Network**: 1Gbps bandwidth recommended

#### Production Resources (Clustered)
- **CPU**: 8+ cores per node
- **Memory**: 16GB+ RAM per node
- **Storage**: 100GB+ SSD storage
- **Network**: 10Gbps bandwidth
- **Load Balancer**: External or cloud-native

#### High Availability Setup
- **Nodes**: 3+ application instances
- **Database**: Redis cluster with sentinel
- **Storage**: Distributed vector database
- **Monitoring**: Full observability stack

### Software Prerequisites

```bash
# Container Runtime
docker --version                # Docker 20.10+
docker-compose --version        # Docker Compose 2.0+

# Kubernetes (if applicable)
kubectl version --client        # kubectl 1.25+
helm version                    # Helm 3.8+

# Monitoring Tools
curl --version                  # Health check tools
wget --version                  # Download utilities
```

### Network Requirements

#### Inbound Ports
- **8000**: Main application HTTP
- **8443**: HTTPS (if SSL termination at app level)
- **9090**: Prometheus metrics (internal)
- **6379**: Redis (internal cluster only)

#### Outbound Access
- **443**: HTTPS for document fetching
- **80**: HTTP for document sources
- **DNS**: For domain resolution

## Environment Setup

### Environment Configuration Template

Create a production `.env` file:

```bash
# Production Environment Configuration
APP_ENV=production
DEBUG=false

# API Configuration
API_MODE=browser
PUTER_MODEL=claude-sonnet-4
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=120
BROWSER_WAIT_TIME=10

# Database Configuration
VECTOR_DB_PATH=/app/data/vectordb
COLLECTION_NAME=oran_nephio_official
EMBEDDINGS_CACHE_PATH=/app/data/embeddings

# Redis Configuration
REDIS_HOST=redis-master
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_SENTINEL_PASSWORD=${REDIS_SENTINEL_PASSWORD}

# Performance Settings
MAX_TOKENS=4000
TEMPERATURE=0.1
CHUNK_SIZE=1024
CHUNK_OVERLAP=200
RETRIEVER_K=6
RETRIEVER_FETCH_K=15

# Scaling Configuration
WORKERS=4
WORKER_TIMEOUT=120
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=50

# Security Settings
SECRET_KEY=${SECRET_KEY}
VERIFY_SSL=true
CORS_ORIGINS=["https://yourdomain.com"]

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/app/logs/oran_nephio_rag.log
STRUCTURED_LOGGING=true

# Monitoring Configuration
PROMETHEUS_METRICS_PORT=9100
ENABLE_METRICS=true
HEALTH_CHECK_INTERVAL=30

# Data Persistence
DATA_RETENTION_DAYS=30
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"
```

### Secrets Management

#### Using Docker Secrets
```bash
# Create secrets
echo "your-secret-key" | docker secret create app_secret_key -
echo "your-redis-password" | docker secret create redis_password -

# Reference in docker-compose.yml
secrets:
  - app_secret_key
  - redis_password
```

#### Using Kubernetes Secrets
```bash
# Create secret
kubectl create secret generic oran-rag-secrets \
  --from-literal=secret-key=your-secret-key \
  --from-literal=redis-password=your-redis-password

# Apply secret in manifests
env:
  - name: SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: oran-rag-secrets
        key: secret-key
```

## Local Development

### Quick Development Setup

```bash
# 1. Clone and setup
git clone https://github.com/thc1006/oran-nephio-rag.git
cd oran-nephio-rag

# 2. Create development environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements-dev.txt
pip install -e .

# 4. Setup environment
cp .env.example .env  # Create if missing
echo "API_MODE=mock" >> .env
echo "LOG_LEVEL=DEBUG" >> .env

# 5. Initialize database
python create_minimal_database.py

# 6. Run development server
python main.py
```

### Development with Docker

```bash
# Development with hot reload
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f oran-rag-app

# Execute commands in container
docker-compose -f docker-compose.dev.yml exec oran-rag-app python test_verification.py
```

## Docker Deployment

### Single Container Deployment

```bash
# Build production image
docker build -f Dockerfile.production -t oran-rag:prod .

# Run single container
docker run -d \
  --name oran-rag-prod \
  -p 8000:8000 \
  -e API_MODE=browser \
  -e LOG_LEVEL=INFO \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  oran-rag:prod
```

### Docker Compose Production

#### Basic Production Setup

```bash
# Create production environment file
cat > .env.prod <<EOF
# Basic production settings
APP_ENV=production
API_MODE=browser
WORKERS=4
REDIS_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 32)
DATA_PATH=/opt/oran-rag/data
LOG_PATH=/opt/oran-rag/logs
VERSION=latest
EOF

# Deploy
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

#### High Availability Setup

```bash
# Create HA environment
cat > .env.ha <<EOF
APP_REPLICAS=3
REDIS_REPLICAS=2
ENABLE_MONITORING=true
GRAFANA_PASSWORD=$(openssl rand -base64 16)
PROMETHEUS_RETENTION=30d
EOF

# Deploy with monitoring
docker-compose \
  -f docker-compose.prod.yml \
  -f docker-compose.monitoring.yml \
  --env-file .env.ha \
  up -d
```

### Container Health Checks

```bash
# Check container health
docker-compose ps

# View health check logs
docker inspect oran-rag-app --format='{{.State.Health.Status}}'

# Manual health check
curl -f http://localhost:8000/health || exit 1
```

## Cloud Deployment

### Amazon Web Services (AWS)

#### ECS Fargate Deployment

```bash
# 1. Build and push to ECR
aws ecr get-login-password --region us-west-2 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com

docker build -t oran-rag .
docker tag oran-rag:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/oran-rag:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/oran-rag:latest

# 2. Create ECS task definition
cat > task-definition.json <<EOF
{
  "family": "oran-rag",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "oran-rag",
      "image": "123456789012.dkr.ecr.us-west-2.amazonaws.com/oran-rag:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "API_MODE", "value": "browser"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/oran-rag",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

# 3. Register and create service
aws ecs register-task-definition --cli-input-json file://task-definition.json
aws ecs create-service \
  --cluster oran-rag-cluster \
  --service-name oran-rag-service \
  --task-definition oran-rag \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration '{
    "awsvpcConfiguration": {
      "subnets": ["subnet-12345", "subnet-67890"],
      "securityGroups": ["sg-12345"],
      "assignPublicIp": "ENABLED"
    }
  }'
```

#### EC2 with Auto Scaling

```bash
# User Data script for EC2 instances
cat > user-data.sh <<'EOF'
#!/bin/bash
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install docker-compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone and deploy
cd /opt
git clone https://github.com/thc1006/oran-nephio-rag.git
cd oran-nephio-rag
echo "API_MODE=browser" > .env
echo "WORKERS=4" >> .env
docker-compose -f docker-compose.prod.yml up -d
EOF
```

### Google Cloud Platform (GCP)

#### Cloud Run Deployment

```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT-ID/oran-rag

# 2. Deploy to Cloud Run
gcloud run deploy oran-rag \
  --image gcr.io/PROJECT-ID/oran-rag \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --concurrency 80 \
  --max-instances 10 \
  --set-env-vars API_MODE=browser,LOG_LEVEL=INFO \
  --port 8000

# 3. Setup custom domain
gcloud run domain-mappings create \
  --service oran-rag \
  --domain api.yourdomain.com \
  --region us-central1
```

#### GKE Deployment

```yaml
# gke-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oran-rag
spec:
  replicas: 3
  selector:
    matchLabels:
      app: oran-rag
  template:
    metadata:
      labels:
        app: oran-rag
    spec:
      containers:
      - name: oran-rag
        image: gcr.io/PROJECT-ID/oran-rag:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_MODE
          value: "browser"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: oran-rag-service
spec:
  selector:
    app: oran-rag
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Microsoft Azure

#### Container Instances

```bash
# Deploy to Azure Container Instances
az container create \
  --resource-group oran-rag-rg \
  --name oran-rag \
  --image your-registry/oran-rag:latest \
  --dns-name-label oran-rag-unique \
  --ports 8000 \
  --environment-variables API_MODE=browser LOG_LEVEL=INFO \
  --memory 2 \
  --cpu 1
```

#### Azure Kubernetes Service (AKS)

```bash
# Create AKS cluster
az aks create \
  --resource-group oran-rag-rg \
  --name oran-rag-aks \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials and deploy
az aks get-credentials --resource-group oran-rag-rg --name oran-rag-aks
kubectl apply -f k8s/
```

## Kubernetes Deployment

### Namespace and RBAC

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: oran-rag
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: oran-rag
  namespace: oran-rag
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: oran-rag
  name: oran-rag-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: oran-rag-binding
  namespace: oran-rag
subjects:
- kind: ServiceAccount
  name: oran-rag
  namespace: oran-rag
roleRef:
  kind: Role
  name: oran-rag-role
  apiGroup: rbac.authorization.k8s.io
```

### Application Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oran-rag
  namespace: oran-rag
  labels:
    app: oran-rag
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: oran-rag
  template:
    metadata:
      labels:
        app: oran-rag
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9100"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: oran-rag
      containers:
      - name: oran-rag
        image: oran-rag:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9100
          name: metrics
        env:
        - name: API_MODE
          value: "browser"
        - name: REDIS_HOST
          value: "redis-service"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: oran-rag-secrets
              key: secret-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        - name: logs-volume
          mountPath: /app/logs
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: oran-rag-data-pvc
      - name: logs-volume
        persistentVolumeClaim:
          claimName: oran-rag-logs-pvc
```

### Services and Ingress

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: oran-rag-service
  namespace: oran-rag
  labels:
    app: oran-rag
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  - port: 9100
    targetPort: 9100
    protocol: TCP
    name: metrics
  selector:
    app: oran-rag
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: oran-rag-ingress
  namespace: oran-rag
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: oran-rag-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: oran-rag-service
            port:
              number: 80
```

### Persistent Storage

```yaml
# storage.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: oran-rag-data-pvc
  namespace: oran-rag
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 50Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: oran-rag-logs-pvc
  namespace: oran-rag
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 10Gi
```

### Helm Chart Deployment

```bash
# Install with Helm
helm repo add oran-rag https://helm.yourdomain.com
helm repo update

# Install with custom values
cat > values-prod.yaml <<EOF
image:
  tag: "v1.0.0"
replicaCount: 3
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
ingress:
  enabled: true
  hostname: api.yourdomain.com
  tls: true
redis:
  enabled: true
  auth:
    enabled: true
monitoring:
  enabled: true
EOF

helm install oran-rag oran-rag/oran-rag \
  --namespace oran-rag \
  --create-namespace \
  --values values-prod.yaml
```

## Monitoring & Observability

### Prometheus Configuration

```yaml
# prometheus-config.yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'oran-rag'
    static_configs:
      - targets: ['oran-rag-service:9100']
    metrics_path: /metrics
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "O-RAN Nephio RAG System",
    "panels": [
      {
        "title": "Query Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(rag_query_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Active Queries",
        "type": "stat",
        "targets": [
          {
            "expr": "rag_active_queries",
            "legendFormat": "Active Queries"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(rag_errors_total[5m])",
            "legendFormat": "Error Rate"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration

```yaml
# fluent-bit-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush         1
        Log_Level     info
        Daemon        off
        Parsers_File  parsers.conf

    [INPUT]
        Name              tail
        Path              /app/logs/*.log
        Parser            json
        Tag               oran-rag.*
        Refresh_Interval  5

    [OUTPUT]
        Name  es
        Match *
        Host  elasticsearch
        Port  9200
        Index oran-rag-logs
        Type  _doc
```

### Health Check Endpoints

```python
# Health check implementation
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    checks = {
        "vector_db": check_vector_db_connection(),
        "redis": check_redis_connection(),
        "model": check_model_availability()
    }
    
    if all(checks.values()):
        return {"status": "ready", "checks": checks}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")
```

## Security Considerations

### Authentication & Authorization

```python
# JWT Authentication
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

jwt_authentication = JWTAuthentication(
    secret=settings.SECRET_KEY,
    lifetime_seconds=3600,
    tokenUrl="auth/jwt/login",
)

app.include_router(
    fastapi_users.get_auth_router(jwt_authentication),
    prefix="/auth/jwt",
    tags=["auth"],
)
```

### Network Security

```yaml
# Network Policy for Kubernetes
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: oran-rag-netpol
  namespace: oran-rag
spec:
  podSelector:
    matchLabels:
      app: oran-rag
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS
    - protocol: TCP
      port: 53   # DNS
    - protocol: UDP
      port: 53   # DNS
```

### SSL/TLS Configuration

```nginx
# nginx SSL configuration
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;

    location / {
        proxy_pass http://oran-rag-backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Performance Optimization

### Resource Tuning

```yaml
# Resource optimization for Kubernetes
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"

# JVM tuning for Java components
env:
- name: JAVA_OPTS
  value: "-Xms1g -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# Python optimization
env:
- name: PYTHONUNBUFFERED
  value: "1"
- name: PYTHONDONTWRITEBYTECODE
  value: "1"
```

### Caching Strategy

```python
# Redis caching configuration
from redis import Redis
from functools import wraps

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

def cache_result(timeout=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, timeout, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### Database Optimization

```python
# Vector database optimization
chroma_client = chromadb.PersistentClient(
    path=settings.VECTOR_DB_PATH,
    settings=chromadb.config.Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=settings.VECTOR_DB_PATH,
        anonymized_telemetry=False
    )
)

# Query optimization
collection = chroma_client.get_or_create_collection(
    name=settings.COLLECTION_NAME,
    metadata={"hnsw:space": "cosine", "hnsw:M": 16}
)
```

## Backup & Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh - Automated backup script

BACKUP_DIR="/backups/oran-rag"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="oran-rag-backup-${TIMESTAMP}.tar.gz"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Backup vector database
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
  -C /app/data vectordb/ embeddings/ \
  -C /app/logs . \
  --exclude='*.tmp' \
  --exclude='*.lock'

# Upload to S3 (optional)
if [ ! -z "$S3_BUCKET" ]; then
  aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" "s3://${S3_BUCKET}/backups/"
fi

# Cleanup old backups (keep last 7 days)
find "${BACKUP_DIR}" -name "oran-rag-backup-*.tar.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}"
```

### Kubernetes Backup with Velero

```bash
# Install Velero
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.7.0 \
  --bucket oran-rag-backups \
  --secret-file ./credentials-velero

# Create backup schedule
velero schedule create oran-rag-daily \
  --schedule="0 2 * * *" \
  --include-namespaces oran-rag \
  --ttl 720h
```

### Disaster Recovery

```bash
#!/bin/bash
# disaster-recovery.sh

# 1. Restore from backup
BACKUP_FILE="$1"
if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file>"
  exit 1
fi

# 2. Stop services
docker-compose down

# 3. Restore data
tar -xzf "$BACKUP_FILE" -C /app/data/

# 4. Restart services
docker-compose up -d

# 5. Verify restoration
sleep 30
curl -f http://localhost:8000/health || exit 1

echo "Disaster recovery completed successfully"
```

## Troubleshooting

### Common Issues

#### 1. Container Startup Issues

```bash
# Check container logs
docker logs oran-rag-app --tail=100

# Check resource usage
docker stats oran-rag-app

# Inspect container configuration
docker inspect oran-rag-app
```

#### 2. Kubernetes Pod Issues

```bash
# Check pod status
kubectl get pods -n oran-rag

# Describe pod issues
kubectl describe pod oran-rag-xxx -n oran-rag

# Check events
kubectl get events -n oran-rag --sort-by='.lastTimestamp'

# Access pod logs
kubectl logs -f oran-rag-xxx -n oran-rag
```

#### 3. Performance Issues

```bash
# Check resource usage
kubectl top pods -n oran-rag
kubectl top nodes

# Analyze slow queries
grep "slow_query" /app/logs/oran_nephio_rag.log | tail -20

# Check database performance
python -c "
from src import create_rag_system
rag = create_rag_system()
status = rag.get_system_status()
print('Vector DB Info:', status['vectordb_info'])
"
```

### Diagnostic Tools

```bash
#!/bin/bash
# diagnose.sh - System diagnostic script

echo "=== O-RAN Nephio RAG System Diagnostics ==="

# 1. Check application health
echo "1. Application Health:"
curl -s http://localhost:8000/health | jq .

# 2. Check container status
echo "2. Container Status:"
docker-compose ps

# 3. Check resource usage
echo "3. Resource Usage:"
docker stats --no-stream

# 4. Check logs for errors
echo "4. Recent Errors:"
docker-compose logs --tail=50 | grep -i error

# 5. Check disk space
echo "5. Disk Usage:"
df -h | grep -E "(/$|/app)"

# 6. Check network connectivity
echo "6. Network Connectivity:"
curl -s -o /dev/null -w "%{http_code}" https://docs.nephio.org/

echo "=== Diagnostics Complete ==="
```

## Maintenance

### Regular Maintenance Tasks

#### Daily
- Monitor system health and performance metrics
- Check error logs for anomalies
- Verify backup completion
- Review security alerts

#### Weekly
- Update vector database with latest documents
- Analyze query patterns and performance
- Check disk space and cleanup old logs
- Review and rotate secrets if needed

#### Monthly
- Update container images and dependencies
- Performance tuning based on usage patterns
- Security audit and vulnerability scanning
- Disaster recovery testing

### Maintenance Scripts

```bash
#!/bin/bash
# maintenance.sh - Regular maintenance tasks

# Update vector database
echo "Updating vector database..."
python -c "
from src.oran_nephio_rag import ORANNephioRAG
rag = ORANNephioRAG()
rag.update_database()
"

# Cleanup old logs
echo "Cleaning up old logs..."
find /app/logs -name "*.log.*" -mtime +30 -delete

# Cleanup old backups
echo "Cleaning up old backups..."
find /backups -name "*.tar.gz" -mtime +30 -delete

# Update dependencies
echo "Checking for dependency updates..."
pip list --outdated

# Security scan
echo "Running security scan..."
docker run --rm -v $(pwd):/src returntocorp/semgrep --config=auto /src

echo "Maintenance completed"
```

### Monitoring and Alerting

```yaml
# Alert rules for Prometheus
groups:
- name: oran-rag-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(rag_errors_total[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(rag_query_duration_seconds_bucket[5m])) > 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }} seconds"

  - alert: ServiceDown
    expr: up{job="oran-rag"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "O-RAN RAG service is down"
      description: "Service has been down for more than 1 minute"
```

---

## Conclusion

This deployment guide provides comprehensive coverage for deploying the O-RAN × Nephio RAG System in various environments. For additional support or specific deployment scenarios, please refer to:

- 📧 **Technical Support**: hctsai@linux.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/thc1006/oran-nephio-rag/issues)
- 📖 **Documentation**: [Complete Guide](README.md)
- 💬 **Community**: [GitHub Discussions](https://github.com/thc1006/oran-nephio-rag/discussions)

**Production deployment checklist completed! Your O-RAN × Nephio RAG System is ready for enterprise-scale deployment.**