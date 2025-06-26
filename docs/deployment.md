# 🚀 Deployment Guide

Complete guide for deploying your MCP Server to production environments with Docker, cloud platforms, and monitoring.

## 🏗️ Production Deployment Options

### 1. Docker Deployment (Recommended)

#### Basic Docker Deployment

```bash
# Build production image
docker build -t my-mcp-server:latest .

# Run container
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  -e MCP_SERVER_NAME="Production Server" \
  -e API_KEY="your-secret-key" \
  -e LOG_LEVEL="INFO" \
  my-mcp-server:latest
```

#### Docker Compose Production Setup

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mcp-server:
    build:
      context: .
      target: production
    container_name: mcp-server
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - MCP_SERVER_NAME=Production MCP Server
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
      - LOG_LEVEL=INFO
      - ENABLE_HEALTH_CHECK=true
      - API_KEY=${API_KEY}
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "python", "scripts/healthcheck.py"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - mcp-network

  nginx:
    image: nginx:alpine
    container_name: mcp-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - mcp-server
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
```

### 2. Cloud Platform Deployment

#### AWS ECS Deployment

```json
{
  "family": "mcp-server",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "mcp-server",
      "image": "your-account.dkr.ecr.region.amazonaws.com/mcp-server:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "MCP_HOST", "value": "0.0.0.0"},
        {"name": "MCP_PORT", "value": "8000"}
      ],
      "secrets": [
        {"name": "API_KEY", "valueFrom": "arn:aws:secretsmanager:region:account:secret:mcp-api-key"}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "python scripts/healthcheck.py"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mcp-server",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Google Cloud Run

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/mcp-server', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/mcp-server']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'mcp-server'
      - '--image'
      - 'gcr.io/$PROJECT_ID/mcp-server'
      - '--platform'
      - 'managed'
      - '--region'
      - 'us-central1'
      - '--allow-unauthenticated'
```

#### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name mcp-server \
  --image myregistry.azurecr.io/mcp-server:latest \
  --cpu 1 \
  --memory 1 \
  --ports 8000 \
  --environment-variables \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
  --secure-environment-variables \
    API_KEY=your-secret-key
```

## 🔒 Security Configuration

### Environment Variables for Production

```bash
# .env.production
MCP_SERVER_NAME="Production MCP Server"
MCP_HOST="0.0.0.0"
MCP_PORT="8000"
MCP_TRANSPORT="http"

# Security
API_KEY="your-strong-api-key-here"
REQUIRE_AUTH="true"
CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"

# Performance
MAX_WORKERS="4"
TIMEOUT_SECONDS="30"
MAX_REQUEST_SIZE="10485760"  # 10MB

# Monitoring
ENABLE_HEALTH_CHECK="true"
ENABLE_METRICS="true"
LOG_LEVEL="INFO"
LOG_FILE="/app/logs/mcp-server.log"

# Database (if needed)
DATABASE_URL="postgresql://user:pass@host:5432/dbname"
REDIS_URL="redis://redis:6379/0"
```

### SSL/TLS Configuration

#### Nginx Reverse Proxy

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream mcp-server {
        server mcp-server:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/ssl/certs/fullchain.pem;
        ssl_certificate_key /etc/ssl/certs/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        location / {
            proxy_pass http://mcp-server;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://mcp-server/health;
            access_log off;
        }
    }
}
```

## 📊 Monitoring and Logging

### Prometheus Metrics

```python
# src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Metrics
REQUEST_COUNT = Counter('mcp_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('mcp_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('mcp_active_connections', 'Active connections')

def setup_metrics():
    """Start metrics server."""
    start_http_server(9090)

@mcp.middleware
async def metrics_middleware(request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response
```

### Structured Logging

```python
# src/config/logging.py
import structlog
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=False),
            "foreign_pre_chain": [
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
            ],
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "file": {
            "level": "INFO", 
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/app/logs/mcp-server.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "json",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": False,
        },
    }
}

def configure_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

### Health Monitoring

```python
# Enhanced health check
@mcp.tool
async def production_health_check() -> Dict[str, Any]:
    """Production health check with detailed metrics."""
    checks = {}
    
    # Database connectivity
    if settings.DATABASE_URL:
        try:
            # Test database connection
            checks["database"] = {"status": "healthy", "response_time": "5ms"}
        except Exception as e:
            checks["database"] = {"status": "unhealthy", "error": str(e)}
    
    # Redis connectivity
    if settings.REDIS_URL:
        try:
            # Test Redis connection
            checks["redis"] = {"status": "healthy", "response_time": "2ms"}
        except Exception as e:
            checks["redis"] = {"status": "unhealthy", "error": str(e)}
    
    # System resources
    import psutil
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1)
    
    checks["system"] = {
        "memory_percent": memory.percent,
        "cpu_percent": cpu,
        "status": "healthy" if memory.percent < 85 and cpu < 85 else "warning"
    }
    
    # Overall status
    overall_status = "healthy"
    if any(check.get("status") == "unhealthy" for check in checks.values()):
        overall_status = "unhealthy"
    elif any(check.get("status") == "warning" for check in checks.values()):
        overall_status = "warning"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "version": settings.SERVER_VERSION,
        "checks": checks
    }
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --extra dev
      - name: Run tests
        run: |
          uv run pytest --cov=src
      - name: Security scan
        run: |
          uv run bandit -r src/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - name: Login to registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # Your deployment commands here
          echo "Deploying to production..."
```

## 🎯 Performance Optimization

### Resource Limits

```yaml
# docker-compose.prod.yml
services:
  mcp-server:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

### Database Connection Pooling

```python
# src/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)
```

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] Secrets properly managed
- [ ] SSL certificates in place
- [ ] Database migrations run
- [ ] Health checks passing
- [ ] Security scan completed
- [ ] Performance testing done

### Deployment
- [ ] Blue-green deployment strategy
- [ ] Rolling updates configured
- [ ] Rollback plan ready
- [ ] Monitoring alerts active
- [ ] Load balancer configured

### Post-deployment
- [ ] Health checks passing
- [ ] Metrics being collected
- [ ] Logs being aggregated
- [ ] Performance within SLAs
- [ ] Security monitoring active

## 🚨 Troubleshooting

### Common Production Issues

#### Memory Leaks
```bash
# Monitor memory usage
docker stats mcp-server

# Check for memory leaks
python -m memory_profiler src/server.py
```

#### High CPU Usage
```bash
# Profile CPU usage
py-spy top --pid $(pgrep -f "python src/server.py")
```

#### Database Connection Issues
```python
# Add connection retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def connect_to_database():
    # Database connection logic
    pass
```

### Monitoring Commands

```bash
# Check container health
docker ps
docker logs mcp-server

# Check resource usage
docker stats

# Test health endpoint
curl -f http://localhost:8000/health || exit 1

# Check application logs
tail -f logs/mcp-server.log
```

---

This deployment guide covers the essential aspects of running your MCP server in production. Remember to regularly update dependencies, monitor performance, and maintain security best practices. 