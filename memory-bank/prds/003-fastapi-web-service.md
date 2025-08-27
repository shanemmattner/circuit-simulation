# PRD: FastAPI Web Service with WebSocket Support

## 🎯 Product Overview
**Feature**: Production-ready REST API service for circuit simulation  
**GitHub Issue**: #5  
**Priority**: High  
**Estimated Effort**: 4-5 days  

## 📋 Problem Statement
Currently, the circuit simulation library only provides:
- Python API for programmatic use
- MCP server for AI integration
- CLI examples for testing

**Missing capabilities:**
- Web-based API for remote access
- Real-time simulation progress updates
- Scalable job processing for multiple concurrent simulations
- Standard REST endpoints for web/mobile integration

## 🎯 Objectives
Build a FastAPI web service that enables:
1. **Remote Access**: REST API accessible over HTTP
2. **Real-time Updates**: WebSocket support for live simulation progress
3. **Scalable Processing**: Background job queue for long-running simulations
4. **Professional Quality**: Production-ready with proper error handling, validation, and documentation

## 👥 Target Users
- **Web Developers**: Integrating circuit simulation into web applications
- **Mobile App Developers**: Building circuit simulation mobile apps
- **DevOps Engineers**: Deploying circuit simulation as a service
- **Researchers**: Running batch simulations remotely

## 📐 Technical Requirements

### Core API Endpoints
- `POST /api/circuits` - Create new circuit
- `GET /api/circuits/{id}` - Get circuit details
- `POST /api/circuits/{id}/simulate` - Start simulation job
- `GET /api/simulations/{job_id}` - Get simulation status
- `GET /api/simulations/{job_id}/results` - Get results
- `DELETE /api/simulations/{job_id}` - Cancel simulation
- `GET /api/circuits/examples` - List example circuits
- `POST /api/circuits/import` - Import netlist
- `GET /api/circuits/{id}/export` - Export circuit

### WebSocket Features
- Real-time simulation progress (percentage, ETA)
- Live result streaming during simulation
- Multi-client support with per-job channels
- Automatic reconnection handling
- Progress messages and status updates

### Background Job Processing
- Redis-based job queue using Celery
- Parallel simulation processing
- Job priority levels (1-10 scale)
- Result caching (24-hour retention)
- Automatic cleanup of old jobs/results

### Dependencies to Add
```toml
fastapi = "^0.104.0"
uvicorn[standard] = "^0.24.0" 
redis = "^5.0.0"
celery = "^5.3.0"
websockets = "^12.0"
pydantic = "^2.5.0"
python-multipart = "^0.0.6"
plotly = "^5.17.0"
```

## 📊 Success Criteria
- [ ] API handles 100+ concurrent requests without degradation
- [ ] WebSocket maintains stable connections for 1+ hour sessions
- [ ] Jobs process in parallel (up to CPU core count)
- [ ] Results cached and retrievable for 24 hours
- [ ] Auto-generated OpenAPI documentation at `/docs`
- [ ] 95%+ uptime in production environment
- [ ] API response time <100ms (p95) for CRUD operations
- [ ] WebSocket update latency <100ms

## 🏗️ Architecture

### File Structure
```
src/api/
├── __init__.py              # FastAPI app
├── main.py                  # Application entry point
├── models/
│   ├── circuit.py           # Pydantic models for circuits
│   ├── simulation.py        # Request/response models
│   └── job.py              # Job queue models
├── routes/
│   ├── circuits.py          # Circuit CRUD endpoints
│   ├── simulations.py       # Simulation job endpoints
│   └── websocket.py         # WebSocket handlers
├── services/
│   ├── circuit_service.py   # Circuit business logic
│   ├── simulation_service.py # Simulation orchestration
│   └── cache_service.py     # Redis caching
├── workers/
│   ├── celery_app.py        # Celery configuration
│   ├── tasks.py             # Background simulation tasks
│   └── scheduler.py         # Task scheduling
├── middleware/
│   ├── cors.py              # CORS configuration
│   ├── rate_limit.py        # Rate limiting
│   └── error_handler.py     # Global error handling
└── utils/
    ├── exceptions.py        # Custom exceptions
    └── validators.py        # Input validation
```

### Integration Points
- **Circuit Engine**: Uses existing `src/circuit_sim/` modules
- **Simulation Engine**: Integrates with `simulator/engine.py`  
- **Results**: Leverages `simulator/results.py` for data formatting
- **MCP Server**: Runs independently, no conflicts

## 🔒 Security Considerations
- Input validation on all endpoints using Pydantic
- Rate limiting to prevent abuse (100 requests/minute per IP)
- CORS configuration for web browser access
- No authentication required for MVP (will be Phase 2)
- Sanitize file uploads for netlist import
- Limit simulation duration/complexity to prevent resource exhaustion

## 🚀 Deployment Strategy
- Docker Compose with 4 services: API, Worker, Redis, Nginx (optional)
- Environment-based configuration
- Health check endpoints for monitoring
- Graceful shutdown handling
- Log aggregation with structured logging

## 📈 Performance Targets
- **Concurrent Users**: 100+ simultaneous API users
- **Job Throughput**: Limited by CPU cores (typically 4-8 parallel simulations)
- **Memory Usage**: <2GB per worker process
- **Response Times**: 
  - CRUD operations: <100ms (p95)
  - Job submission: <200ms (p95)
  - WebSocket updates: <100ms latency

## 🧪 Testing Strategy
- Unit tests for all API endpoints using pytest + httpx
- Integration tests for WebSocket connections
- Load testing with 100+ concurrent requests
- End-to-end tests simulating real user workflows
- Redis/Celery integration tests
- Docker deployment verification

## 📝 Documentation Requirements
- Auto-generated OpenAPI schema at `/docs` endpoint
- Interactive Swagger UI for API exploration  
- WebSocket protocol documentation
- Docker deployment guide
- Performance tuning recommendations

## 🔗 Dependencies
**Blocks**: None (independent feature)  
**Depends on**: Core simulation engine (already implemented)  
**Related**: Issue #1 (CLI), MCP server (complementary)

## 🎯 Acceptance Criteria
1. ✅ All REST endpoints implemented with proper validation
2. ✅ WebSocket real-time updates working with <100ms delay
3. ✅ Background jobs queue and process correctly under load
4. ✅ Auto-generated API documentation accessible and complete
5. ✅ Docker Compose deployment works out of the box
6. ✅ Test coverage >85% for new API code
7. ✅ Load testing passes with 100+ concurrent requests
8. ✅ All existing tests continue to pass

## 📋 Implementation Plan
1. **Phase 1**: Basic FastAPI app structure and Pydantic models
2. **Phase 2**: Circuit CRUD endpoints with validation
3. **Phase 3**: Simulation job endpoints with basic queuing  
4. **Phase 4**: WebSocket support for real-time updates
5. **Phase 5**: Redis/Celery integration for scalable processing
6. **Phase 6**: Docker Compose deployment configuration
7. **Phase 7**: Comprehensive testing and documentation

## 🏷️ Success Metrics
- API uptime >95%
- Average response time <100ms
- Successful job completion rate >99%
- Zero data corruption issues
- Positive developer feedback on API usability

---
**Created**: August 27, 2025  
**Status**: Pending Approval  
**Next Step**: Get explicit approval before implementation