# Kubernetes Deployment Guide

This comprehensive guide covers deploying the O-RAN × Nephio RAG system on Kubernetes clusters, from development to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment Architecture](#deployment-architecture)
- [Configuration Management](#configuration-management)
- [Storage Configuration](#storage-configuration)
- [Networking and Ingress](#networking-and-ingress)
- [Monitoring and Observability](#monitoring-and-observability)
- [Scaling and High Availability](#scaling-and-high-availability)
- [Security Configuration](#security-configuration)
- [Maintenance and Operations](#maintenance-and-operations)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Kubernetes Cluster Requirements

```bash
# Minimum cluster specifications
- Kubernetes version: 1.20+
- Nodes: 3+ (for production)
- Total CPU: 6+ cores
- Total Memory: 12GB+ RAM
- Storage: 50GB+ (preferably SSD)
- Network: Pod networking (CNI) configured

# Check cluster status
kubectl cluster-info
kubectl get nodes -o wide
kubectl get pods --all-namespaces
```

### Required Tools

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm (optional, for easier management)
curl https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz | tar xz
sudo mv linux-amd64/helm /usr/local/bin/

# Verify installations
kubectl version --client
helm version
```

### Cluster Add-ons

```bash
# Install ingress controller (NGINX)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Install cert-manager (for SSL certificates)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# Install metrics server (for HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify installations
kubectl get pods -n ingress-nginx
kubectl get pods -n cert-manager
kubectl get pods -n kube-system | grep metrics-server
```

## Quick Start

### 1. Deploy Basic Configuration

```bash
# Clone repository
git clone https://github.com/thc1006/oran-nephio-rag.git
cd oran-nephio-rag

# Create namespace and basic resources
kubectl apply -f docs/deployment/kubernetes-manifests.yaml

# Check deployment status
kubectl get all -n oran-nephio-rag
```

### 2. Verify Deployment

```bash
# Check pod status
kubectl get pods -n oran-nephio-rag -w

# Check logs
kubectl logs -f deployment/oran-rag-app -n oran-nephio-rag

# Test service
kubectl port-forward service/oran-rag-service 8000:8000 -n oran-nephio-rag
curl http://localhost:8000/health
```

### 3. Access the Application

```bash
# Get ingress IP
kubectl get ingress oran-rag-ingress -n oran-nephio-rag

# Or use port forwarding for local access
kubectl port-forward service/oran-rag-service 8000:8000 -n oran-nephio-rag &

# Test API
curl http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is O-RAN?", "k": 3}'
```

## Deployment Architecture

### Component Overview

```
┌─────────────────────┐
│   Load Balancer     │ (Ingress Controller)
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   Ingress          │ (SSL Termination, Routing)
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   Service          │ (Load Balancing)
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   Deployment       │ (3 Replicas)
│   ┌─────────────┐   │
│   │   Pod 1     │   │
│   └─────────────┘   │
│   ┌─────────────┐   │
│   │   Pod 2     │   │
│   └─────────────┘   │
│   ┌─────────────┐   │
│   │   Pod 3     │   │
│   └─────────────┘   │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   Persistent       │ (Vector DB, Embeddings)
│   Volumes          │
└─────────────────────┘
```

### Resource Allocation

```yaml
# Recommended resource allocation
Production:
  replicas: 3-5
  resources:
    requests:
      cpu: 1000m
      memory: 2Gi
    limits:
      cpu: 2000m
      memory: 4Gi

Development:
  replicas: 1-2
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1000m
      memory: 2Gi
```

## Configuration Management

### 1. Environment-Specific ConfigMaps

```yaml
# dev-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: oran-rag-config-dev
  namespace: oran-nephio-rag
data:
  API_MODE: "mock"
  LOG_LEVEL: "DEBUG"
  CHUNK_SIZE: "512"
  RETRIEVER_K: "3"
  AUTO_SYNC_ENABLED: "false"

---
# prod-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: oran-rag-config-prod
  namespace: oran-nephio-rag
data:
  API_MODE: "browser"
  PUTER_MODEL: "claude-sonnet-4"
  LOG_LEVEL: "INFO"
  CHUNK_SIZE: "1024"
  RETRIEVER_K: "6"
  AUTO_SYNC_ENABLED: "true"
  BROWSER_HEADLESS: "true"
```

### 2. Secrets Management

```bash
# Create secrets
kubectl create secret generic oran-rag-secrets \
  --from-literal=ANTHROPIC_API_KEY=your_api_key_here \
  --from-literal=JWT_SECRET_KEY=your_jwt_secret_here \
  -n oran-nephio-rag

# Or use YAML
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: oran-rag-secrets
  namespace: oran-nephio-rag
type: Opaque
data:
  ANTHROPIC_API_KEY: $(echo -n "your_api_key" | base64)
  JWT_SECRET_KEY: $(echo -n "your_jwt_secret" | base64)
EOF
```

### 3. Environment Selection

```bash
# Deploy with development config
kubectl patch deployment oran-rag-app -n oran-nephio-rag -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "oran-rag",
          "envFrom": [{
            "configMapRef": {
              "name": "oran-rag-config-dev"
            }
          }]
        }]
      }
    }
  }
}'

# Deploy with production config
kubectl patch deployment oran-rag-app -n oran-nephio-rag -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "oran-rag",
          "envFrom": [{
            "configMapRef": {
              "name": "oran-rag-config-prod"
            }
          }]
        }]
      }
    }
  }
}'
```

## Storage Configuration

### 1. StorageClass Configuration

```yaml
# storage-class.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
  annotations:
    storageclass.kubernetes.io/is-default-class: "false"
provisioner: kubernetes.io/gce-pd  # Change based on your cloud provider
parameters:
  type: pd-ssd
  replication-type: regional-pd
allowVolumeExpansion: true
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
```

### 2. Dynamic Volume Provisioning

```yaml
# persistent-volumes.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: oran-rag-vectordb-pvc
  namespace: oran-nephio-rag
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 20Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: oran-rag-embeddings-pvc
  namespace: oran-nephio-rag
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 10Gi
```

### 3. Backup Configuration

```yaml
# backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: oran-rag-backup
  namespace: oran-nephio-rag
spec:
  schedule: "0 3 * * *"  # Daily at 3 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: ubuntu:20.04
            command:
            - /bin/bash
            - -c
            - |
              apt-get update && apt-get install -y rsync
              rsync -av /app/data/vectordb/ /backup/vectordb-$(date +%Y%m%d)/
              rsync -av /app/data/embeddings/ /backup/embeddings-$(date +%Y%m%d)/
              # Keep only last 7 days of backups
              find /backup -type d -name "*-*" -mtime +7 -exec rm -rf {} \;
            volumeMounts:
            - name: vectordb-storage
              mountPath: /app/data/vectordb
              readOnly: true
            - name: embeddings-storage
              mountPath: /app/data/embeddings
              readOnly: true
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: vectordb-storage
            persistentVolumeClaim:
              claimName: oran-rag-vectordb-pvc
          - name: embeddings-storage
            persistentVolumeClaim:
              claimName: oran-rag-embeddings-pvc
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

## Networking and Ingress

### 1. Service Configuration

```yaml
# service-advanced.yaml
apiVersion: v1
kind: Service
metadata:
  name: oran-rag-service
  namespace: oran-nephio-rag
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"  # AWS specific
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
    prometheus.io/path: "/metrics"
spec:
  type: ClusterIP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600
  ports:
  - name: http
    port: 8000
    targetPort: 8000
    protocol: TCP
  - name: metrics
    port: 9090
    targetPort: 8000
    protocol: TCP
  selector:
    app.kubernetes.io/name: oran-nephio-rag
    app.kubernetes.io/component: application
```

### 2. Advanced Ingress Configuration

```yaml
# ingress-advanced.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: oran-rag-ingress
  namespace: oran-nephio-rag
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/rate-limit-rps: "10"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
    nginx.ingress.kubernetes.io/cors-allow-origin: "*"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization"
spec:
  tls:
  - hosts:
    - oran-rag.example.com
    - api.oran-rag.example.com
    secretName: oran-rag-tls
  rules:
  - host: oran-rag.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: oran-rag-service
            port:
              number: 8000
  - host: api.oran-rag.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: oran-rag-service
            port:
              number: 8000
      - path: /health
        pathType: Prefix
        backend:
          service:
            name: oran-rag-service
            port:
              number: 8000
```

### 3. Network Policies

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: oran-rag-netpol
  namespace: oran-nephio-rag
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: oran-nephio-rag
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow ingress from nginx controller
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  # Allow monitoring
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8000
  egress:
  # Allow DNS
  - to: []
    ports:
    - protocol: UDP
      port: 53
  # Allow HTTPS outbound (for API calls)
  - to: []
    ports:
    - protocol: TCP
      port: 443
  # Allow Redis
  - to:
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: redis
    ports:
    - protocol: TCP
      port: 6379
```

## Monitoring and Observability

### 1. Prometheus ServiceMonitor

```yaml
# service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: oran-rag-metrics
  namespace: oran-nephio-rag
  labels:
    app.kubernetes.io/name: oran-nephio-rag
    monitoring: prometheus
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: oran-nephio-rag
      app.kubernetes.io/component: service
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
    scrapeTimeout: 10s
    honorLabels: true
```

### 2. Grafana Dashboard ConfigMap

```yaml
# grafana-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: oran-rag-dashboard
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  oran-rag-dashboard.json: |
    {
      "dashboard": {
        "title": "O-RAN × Nephio RAG System",
        "panels": [
          {
            "title": "Request Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(http_requests_total{job='oran-rag-metrics'}[5m])",
                "legendFormat": "{{method}} {{endpoint}}"
              }
            ]
          },
          {
            "title": "Response Time",
            "type": "graph",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, rate(rag_query_duration_seconds_bucket[5m]))",
                "legendFormat": "95th percentile"
              }
            ]
          },
          {
            "title": "Pod CPU Usage",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(container_cpu_usage_seconds_total{namespace='oran-nephio-rag'}[5m])",
                "legendFormat": "{{pod}}"
              }
            ]
          },
          {
            "title": "Pod Memory Usage",
            "type": "graph",
            "targets": [
              {
                "expr": "container_memory_usage_bytes{namespace='oran-nephio-rag'}",
                "legendFormat": "{{pod}}"
              }
            ]
          }
        ]
      }
    }
```

### 3. Alerting Rules

```yaml
# alert-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: oran-rag-alerts
  namespace: oran-nephio-rag
  labels:
    prometheus: kube-prometheus
    role: alert-rules
spec:
  groups:
  - name: oran-rag.rules
    rules:
    - alert: ORANRAGHighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High error rate in O-RAN RAG system"
        description: "Error rate is {{ $value | humanizePercentage }} for the last 5 minutes"

    - alert: ORANRAGHighLatency
      expr: histogram_quantile(0.95, rate(rag_query_duration_seconds_bucket[5m])) > 10
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High latency in O-RAN RAG system"
        description: "95th percentile latency is {{ $value }}s"

    - alert: ORANRAGPodCrashLooping
      expr: rate(kube_pod_container_status_restarts_total{namespace="oran-nephio-rag"}[5m]) > 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Pod is crash looping"
        description: "Pod {{ $labels.pod }} is crash looping"

    - alert: ORANRAGPodNotReady
      expr: kube_pod_status_ready{condition="false",namespace="oran-nephio-rag"} == 1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Pod is not ready"
        description: "Pod {{ $labels.pod }} is not ready"
```

## Scaling and High Availability

### 1. Horizontal Pod Autoscaler

```yaml
# hpa-advanced.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: oran-rag-hpa
  namespace: oran-nephio-rag
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: oran-rag-app
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Min
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

### 2. Vertical Pod Autoscaler

```yaml
# vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: oran-rag-vpa
  namespace: oran-nephio-rag
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: oran-rag-app
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: oran-rag
      minAllowed:
        cpu: 500m
        memory: 1Gi
      maxAllowed:
        cpu: 4000m
        memory: 8Gi
      controlledResources: ["cpu", "memory"]
```

### 3. Pod Disruption Budget

```yaml
# pdb-advanced.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: oran-rag-pdb
  namespace: oran-nephio-rag
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: oran-nephio-rag
      app.kubernetes.io/component: application
```

## Security Configuration

### 1. Security Context

```yaml
# security-context.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oran-rag-app-secure
  namespace: oran-nephio-rag
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: oran-rag
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
```

### 2. Pod Security Policy

```yaml
# pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: oran-rag-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

### 3. RBAC Configuration

```yaml
# rbac-advanced.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: oran-rag-sa
  namespace: oran-nephio-rag

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: oran-rag-role
  namespace: oran-nephio-rag
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: oran-rag-rolebinding
  namespace: oran-nephio-rag
subjects:
- kind: ServiceAccount
  name: oran-rag-sa
  namespace: oran-nephio-rag
roleRef:
  kind: Role
  name: oran-rag-role
  apiGroup: rbac.authorization.k8s.io
```

## Maintenance and Operations

### 1. Database Initialization Job

```yaml
# db-init-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: oran-rag-db-init
  namespace: oran-nephio-rag
spec:
  template:
    spec:
      restartPolicy: OnFailure
      initContainers:
      - name: wait-for-storage
        image: busybox
        command: ['sh', '-c', 'until [ -d /app/data/vectordb ]; do echo waiting for storage; sleep 2; done']
        volumeMounts:
        - name: vectordb-storage
          mountPath: /app/data/vectordb
      containers:
      - name: db-init
        image: oran-rag:1.0.0
        command: ["python", "create_minimal_database.py"]
        envFrom:
        - configMapRef:
            name: oran-rag-config
        - secretRef:
            name: oran-rag-secrets
        volumeMounts:
        - name: vectordb-storage
          mountPath: /app/data/vectordb
        - name: embeddings-storage
          mountPath: /app/data/embeddings
        resources:
          limits:
            memory: "4Gi"
            cpu: "2000m"
          requests:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: vectordb-storage
        persistentVolumeClaim:
          claimName: oran-rag-vectordb-pvc
      - name: embeddings-storage
        persistentVolumeClaim:
          claimName: oran-rag-embeddings-pvc
  backoffLimit: 3
  activeDeadlineSeconds: 1800  # 30 minutes
```

### 2. Rolling Updates

```bash
# Update deployment image
kubectl set image deployment/oran-rag-app oran-rag=oran-rag:1.1.0 -n oran-nephio-rag

# Check rollout status
kubectl rollout status deployment/oran-rag-app -n oran-nephio-rag

# Rollback if needed
kubectl rollout undo deployment/oran-rag-app -n oran-nephio-rag

# Scale deployment
kubectl scale deployment oran-rag-app --replicas=5 -n oran-nephio-rag
```

### 3. Health Checks and Maintenance Scripts

```bash
#!/bin/bash
# maintenance.sh - Kubernetes maintenance script

NAMESPACE="oran-nephio-rag"

# Function to check pod health
check_pod_health() {
    echo "=== Pod Health Status ==="
    kubectl get pods -n $NAMESPACE -o wide
    echo ""

    # Check for unhealthy pods
    unhealthy_pods=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running -o name)
    if [ ! -z "$unhealthy_pods" ]; then
        echo "⚠️ Unhealthy pods found:"
        echo "$unhealthy_pods"
    else
        echo "✅ All pods are healthy"
    fi
    echo ""
}

# Function to check resource usage
check_resource_usage() {
    echo "=== Resource Usage ==="
    kubectl top pods -n $NAMESPACE
    echo ""

    kubectl top nodes
    echo ""
}

# Function to check PVC status
check_storage() {
    echo "=== Storage Status ==="
    kubectl get pvc -n $NAMESPACE
    echo ""
}

# Function to restart unhealthy pods
restart_unhealthy_pods() {
    echo "=== Restarting Unhealthy Pods ==="
    kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running -o name | \
    xargs -I {} kubectl delete {} -n $NAMESPACE
}

# Function to clean up old replica sets
cleanup_old_replica_sets() {
    echo "=== Cleaning Up Old Replica Sets ==="
    kubectl get rs -n $NAMESPACE -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.replicas}{"\n"}{end}' | \
    awk '$2==0 {print $1}' | \
    xargs -I {} kubectl delete rs {} -n $NAMESPACE
}

# Main execution
case "$1" in
    "health")
        check_pod_health
        check_resource_usage
        check_storage
        ;;
    "restart")
        restart_unhealthy_pods
        ;;
    "cleanup")
        cleanup_old_replica_sets
        ;;
    "all")
        check_pod_health
        check_resource_usage
        check_storage
        cleanup_old_replica_sets
        ;;
    *)
        echo "Usage: $0 {health|restart|cleanup|all}"
        exit 1
        ;;
esac
```

## Troubleshooting

### 1. Common Issues and Solutions

```bash
# Pod stuck in Pending state
kubectl describe pod <pod-name> -n oran-nephio-rag
# Common causes: Resource constraints, PVC not bound, Node selector issues

# Check events
kubectl get events -n oran-nephio-rag --sort-by='.lastTimestamp'

# Pod CrashLoopBackOff
kubectl logs <pod-name> -n oran-nephio-rag --previous
# Check application logs for startup issues

# Service not accessible
kubectl get endpoints -n oran-nephio-rag
# Verify pods are selected by service

# Ingress not working
kubectl describe ingress oran-rag-ingress -n oran-nephio-rag
# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

### 2. Debug Tools

```bash
# Create debug pod
kubectl run debug --image=busybox -it --rm --restart=Never -n oran-nephio-rag -- sh

# Network debugging
kubectl run netshoot --image=nicolaka/netshoot -it --rm --restart=Never -n oran-nephio-rag

# Test service connectivity
kubectl exec -it <pod-name> -n oran-nephio-rag -- curl http://oran-rag-service:8000/health

# Port forward for local debugging
kubectl port-forward deployment/oran-rag-app 8000:8000 -n oran-nephio-rag
```

### 3. Performance Troubleshooting

```bash
# Check resource usage
kubectl top pods -n oran-nephio-rag
kubectl top nodes

# Check HPA status
kubectl get hpa -n oran-nephio-rag -w

# Analyze slow queries
kubectl logs deployment/oran-rag-app -n oran-nephio-rag | grep "query_time"

# Check database performance
kubectl exec -it deployment/oran-rag-app -n oran-nephio-rag -- \
  python -c "
from src import create_rag_system
rag = create_rag_system()
status = rag.get_system_status()
print(f'Document count: {status.get(\"document_count\", 0)}')
print(f'Vector DB ready: {status.get(\"vectordb_ready\", False)}')
"
```

This comprehensive Kubernetes deployment guide provides everything needed to deploy and operate the O-RAN × Nephio RAG system in production Kubernetes environments with proper monitoring, scaling, and security configurations.