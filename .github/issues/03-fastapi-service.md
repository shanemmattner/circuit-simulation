# Feature: FastAPI Web Service with WebSocket Support

## 🎯 Objective
Build a production-ready REST API service for circuit simulation with real-time WebSocket updates, job queuing, and scalable architecture.

## 📋 Requirements

### API Endpoints
- [ ] `POST /api/circuits` - Create new circuit
- [ ] `GET /api/circuits/{id}` - Get circuit details
- [ ] `POST /api/circuits/{id}/simulate` - Start simulation job
- [ ] `GET /api/simulations/{job_id}` - Get simulation status
- [ ] `GET /api/simulations/{job_id}/results` - Get results
- [ ] `DELETE /api/simulations/{job_id}` - Cancel simulation
- [ ] `GET /api/circuits/examples` - List example circuits
- [ ] `POST /api/circuits/import` - Import netlist
- [ ] `GET /api/circuits/{id}/export` - Export circuit

### WebSocket Features
- [ ] Real-time simulation progress
- [ ] Live result streaming
- [ ] Multi-client support
- [ ] Automatic reconnection
- [ ] Progress percentage and ETA

### Background Jobs
- [ ] Redis queue for simulations
- [ ] Celery workers for processing
- [ ] Job priority levels
- [ ] Result caching
- [ ] Automatic cleanup

## 🛠️ Technical Implementation

### Dependencies
```toml
[dependencies]
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
redis = "^5.0.0"
celery = "^5.3.0"
websockets = "^12.0"
pydantic = "^2.5.0"
python-multipart = "^0.0.6"
```

### File Structure
```
src/api/
├── __init__.py
├── main.py              # FastAPI app
├── models/
│   ├── circuit.py       # Pydantic models
│   ├── simulation.py    # Request/response models
│   └── job.py          # Job queue models
├── routes/
│   ├── circuits.py      # Circuit endpoints
│   ├── simulations.py   # Simulation endpoints
│   └── websocket.py     # WebSocket handler
├── services/
│   ├── circuit_service.py
│   ├── simulation_service.py
│   └── cache_service.py
├── workers/
│   ├── celery_app.py    # Celery configuration
│   ├── tasks.py         # Background tasks
│   └── scheduler.py     # Task scheduling
├── middleware/
│   ├── auth.py         # Authentication
│   ├── cors.py         # CORS setup
│   └── rate_limit.py   # Rate limiting
└── utils/
    ├── exceptions.py    # Custom exceptions
    └── validators.py    # Input validation
```

### API Schema
```python
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class SimulationType(str, Enum):
    DC = "dc"
    TRANSIENT = "transient"
    AC = "ac"

class ComponentInput(BaseModel):
    type: str
    name: str
    positive_node: str
    negative_node: str
    value: str
    model: Optional[str]

class CircuitCreate(BaseModel):
    name: str
    description: Optional[str]
    components: List[ComponentInput]

class SimulationRequest(BaseModel):
    type: SimulationType
    parameters: dict
    priority: int = 5

class SimulationStatus(BaseModel):
    job_id: str
    status: str  # pending, running, completed, failed
    progress: float
    eta_seconds: Optional[int]
    message: Optional[str]

class SimulationResult(BaseModel):
    job_id: str
    circuit_id: str
    type: SimulationType
    results: dict
    plots: List[str]  # URLs to plot images
    created_at: datetime
    execution_time: float
```

### WebSocket Protocol
```javascript
// Client connects
ws = new WebSocket("ws://localhost:8000/ws/simulation/job123");

// Server sends progress updates
{
  "type": "progress",
  "data": {
    "progress": 45.2,
    "message": "Running DC analysis...",
    "eta": 12
  }
}

// Server sends results
{
  "type": "result",
  "data": {
    "status": "completed",
    "results": {...},
    "plots": ["plot1.png", "plot2.png"]
  }
}

// Client can send commands
{
  "type": "command",
  "action": "cancel"
}
```

### Docker Compose Setup
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - worker

  worker:
    build: .
    command: celery -A src.api.workers.celery_app worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## 📊 Success Criteria
- [ ] API handles 100+ concurrent requests
- [ ] WebSocket maintains stable connections
- [ ] Jobs process in parallel
- [ ] Results cached for 24 hours
- [ ] Comprehensive OpenAPI documentation
- [ ] 95%+ uptime in production

## 🔗 Dependencies
- Depends on: Core simulation engine
- Blocks: None
- Related: #1 (CLI), #5 (Report Generator)

## 📚 Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/tasks.html)
- [WebSocket Guide](https://websockets.readthedocs.io/)

## ✅ Acceptance Criteria
1. All endpoints have input validation
2. WebSocket updates are real-time (<100ms delay)
3. Jobs queue properly under load
4. API documentation is auto-generated
5. Docker deployment works

## 🏷️ Labels
`enhancement` `api` `backend` `priority-high`

## 📝 Branch
`feature/fastapi-service`

## ⏱️ Estimated Effort
**Time**: 4-5 days
**Complexity**: High
**Priority**: High