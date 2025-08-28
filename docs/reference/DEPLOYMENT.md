# FastAPI Circuit Simulation - Deployment Guide

## 🚀 Quick Start

### Local Development
```bash
# Start the API server
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, test the API
curl http://localhost:8000/health
```

### Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose -f docker-compose.fastapi.yml up -d --build

# Check service health
docker-compose -f docker-compose.fastapi.yml ps

# View logs
docker-compose -f docker-compose.fastapi.yml logs -f api

# Stop services
docker-compose -f docker-compose.fastapi.yml down
```

## 📋 Service Architecture

### Services
- **api**: FastAPI web server with WebSocket support
- **worker**: Celery background job processor  
- **redis**: Job queue and caching
- **nginx**: Reverse proxy with rate limiting (optional)

### Ports
- `8000`: FastAPI API server
- `6379`: Redis (internal)
- `80`: Nginx HTTP (if enabled)
- `443`: Nginx HTTPS (if SSL configured)

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
# Edit .env with your settings
```

### Key Settings
```bash
# Production deployment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Scale workers based on CPU cores
API_WORKERS=4

# Redis connection
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=generate-secure-random-key
ALLOWED_ORIGINS=https://yourdomain.com

# Performance
RATE_LIMIT=1000/hour
MAX_SIMULATION_TIME=600
```

## 🐳 Docker Deployment

### Build Images
```bash
# Build FastAPI image
docker build -f Dockerfile.fastapi -t circuit-sim-api:latest .

# Or use Docker Compose
docker-compose -f docker-compose.fastapi.yml build
```

### Production Deployment
```bash
# Start production services
ENVIRONMENT=production docker-compose -f docker-compose.fastapi.yml up -d

# Scale workers
docker-compose -f docker-compose.fastapi.yml up -d --scale worker=3

# Monitor logs
docker-compose -f docker-compose.fastapi.yml logs -f
```

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Redis health  
docker-compose exec redis redis-cli ping

# Check all services
docker-compose -f docker-compose.fastapi.yml ps
```

## 🔍 Monitoring

### Service Status
```bash
# View service status
docker-compose -f docker-compose.fastapi.yml ps

# Check resource usage
docker stats

# View detailed logs
docker-compose -f docker-compose.fastapi.yml logs --tail=100 api
docker-compose -f docker-compose.fastapi.yml logs --tail=100 worker
```

### API Metrics
Visit `http://localhost:8000/docs` for:
- API documentation
- Interactive testing interface
- Schema validation

### WebSocket Testing
```bash
# Test WebSocket connection
uv run python websocket_demo.py

# Or use wscat
npm install -g wscat
wscat -c ws://localhost:8000/ws/simulation/test-job-123
```

## 📊 Performance Tuning

### Scaling
```bash
# Scale API workers (CPU intensive)
API_WORKERS=4 docker-compose up api -d --scale api=2

# Scale Celery workers (simulation jobs)  
docker-compose up -d --scale worker=4

# Monitor with htop
docker-compose exec api htop
```

### Redis Optimization
```bash
# Memory usage
docker-compose exec redis redis-cli info memory

# Key statistics
docker-compose exec redis redis-cli info keyspace

# Performance metrics
docker-compose exec redis redis-cli info stats
```

## 🔒 Security

### Production Checklist
- [ ] Set strong `SECRET_KEY` and `JWT_SECRET`
- [ ] Configure proper `ALLOWED_ORIGINS`
- [ ] Enable rate limiting
- [ ] Use HTTPS with SSL certificates
- [ ] Restrict Redis access (password, firewall)
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

### SSL Configuration
```bash
# Generate self-signed certificates (development only)
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem

# Enable HTTPS server in nginx.conf
# Uncomment the HTTPS server block
```

## 🧪 Testing

### API Testing
```bash
# Run test suite
uv run pytest tests/test_api*.py tests/test_*_routes.py -v

# Test with running container
docker-compose -f docker-compose.fastapi.yml exec api pytest tests/ -v

# Load testing
pip install locust
locust -f load_test.py --host=http://localhost:8000
```

### Integration Testing
```bash
# Full API workflow
./test_api_examples.sh

# WebSocket functionality
uv run python websocket_demo.py

# Health check
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

### Common Issues

**API won't start:**
```bash
# Check logs
docker-compose logs api

# Verify dependencies
docker-compose exec api uv run python -c "import ngspice; print('OK')"

# Port conflicts
lsof -i :8000
```

**Redis connection errors:**
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Verify network
docker-compose exec api ping redis

# Check environment
docker-compose exec api env | grep REDIS
```

**Simulation failures:**
```bash
# Check ngspice
docker-compose exec api ngspice --version

# Test simulation
docker-compose exec api uv run python -c "
from src.circuit_sim.circuit import Circuit
c = Circuit('test')
c.add_resistor('R1', 1, 0, '1k')
print('Circuit OK')
"

# Worker logs
docker-compose logs worker
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Monitor API responses
curl -w "@curl-format.txt" http://localhost:8000/health

# Redis performance
docker-compose exec redis redis-cli --latency-history -i 1
```

## 📦 Backup & Recovery

### Data Backup
```bash
# Backup Redis data
docker-compose exec redis redis-cli BGSAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb ./backup/

# Restore Redis data
docker cp ./backup/dump.rdb $(docker-compose ps -q redis):/data/
docker-compose restart redis
```

### Configuration Backup
```bash
# Backup deployment files
tar -czf circuit-sim-config.tar.gz \
  docker-compose.fastapi.yml \
  Dockerfile.fastapi \
  nginx/ \
  .env
```

## 🚀 Production Deployment

### Cloud Deployment (AWS/GCP/Azure)
1. Use container orchestration (ECS/GKE/ACI)
2. Set up load balancer with SSL termination
3. Use managed Redis (ElastiCache/Cloud Memorystore)
4. Configure auto-scaling based on CPU/memory
5. Set up monitoring and alerting
6. Implement proper backup strategies

### Environment-Specific Configurations
- **Development**: Single containers, debug enabled
- **Staging**: Multi-container, production-like settings  
- **Production**: Scaled services, monitoring, backups

---

**Last Updated**: August 27, 2025  
**Version**: 1.0.0