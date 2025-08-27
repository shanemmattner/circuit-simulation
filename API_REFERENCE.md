# FastAPI Circuit Simulation - API Reference

## Overview

The Circuit Simulation API provides REST endpoints for creating circuits, running simulations, and monitoring results in real-time via WebSocket connections.

**Base URL**: `http://localhost:8000`  
**Interactive Documentation**: `http://localhost:8000/docs`  
**API Schema**: `http://localhost:8000/openapi.json`

## Authentication

Currently no authentication required for MVP. All endpoints are publicly accessible.

## Response Format

All API responses follow standard HTTP status codes and JSON format:

```json
{
  "status": "success|error",
  "data": { /* response data */ },
  "message": "Human readable message"
}
```

## Endpoints

### Health & System

#### `GET /health`
Health check endpoint for monitoring.

**Response** (200):
```json
{
  "status": "healthy",
  "service": "circuit-simulation-api"
}
```

#### `GET /`
Root endpoint with API information and available endpoints.

**Response** (200):
```json
{
  "message": "Circuit Simulation API - Visit /docs for interactive documentation",
  "version": "0.1.0",
  "endpoints": {
    "docs": "/docs",
    "health": "/health",
    "circuits": "/api/circuits",
    "simulations": "/api/simulations"
  }
}
```

---

## Circuit Management

### `POST /api/circuits`
Create a new circuit.

**Request Body**:
```json
{
  "name": "RC Filter",
  "description": "Simple RC low-pass filter",
  "components": [
    {
      "type": "voltage_source",
      "name": "V1",
      "positive_node": "1",
      "negative_node": "0",
      "value": "5V"
    },
    {
      "type": "resistor",
      "name": "R1",
      "positive_node": "1",
      "negative_node": "2",
      "value": "1k"
    },
    {
      "type": "capacitor",
      "name": "C1",
      "positive_node": "2",
      "negative_node": "0",
      "value": "1u"
    }
  ]
}
```

**Component Types**:
- `voltage_source`: DC voltage source
- `current_source`: DC current source  
- `resistor`: Resistor
- `capacitor`: Capacitor
- `inductor`: Inductor

**Response** (201):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "RC Filter",
  "description": "Simple RC low-pass filter",
  "component_count": 3,
  "node_count": 3,
  "created_at": "2025-08-27T12:00:00Z",
  "updated_at": "2025-08-27T12:00:00Z"
}
```

### `GET /api/circuits/{circuit_id}`
Get circuit details by ID.

**Parameters**:
- `circuit_id`: UUID of the circuit

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "RC Filter", 
  "description": "Simple RC low-pass filter",
  "component_count": 3,
  "node_count": 3,
  "created_at": "2025-08-27T12:00:00Z",
  "updated_at": "2025-08-27T12:00:00Z"
}
```

### `GET /api/circuits`
List all circuits with pagination.

**Query Parameters**:
- `skip` (int): Number of circuits to skip (default: 0)
- `limit` (int): Maximum circuits to return (default: 100, max: 1000)

**Response** (200):
```json
{
  "circuits": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "RC Filter",
      "description": "Simple RC low-pass filter",
      "component_count": 3,
      "node_count": 3,
      "created_at": "2025-08-27T12:00:00Z",
      "updated_at": "2025-08-27T12:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### `DELETE /api/circuits/{circuit_id}`
Delete a circuit by ID.

**Parameters**:
- `circuit_id`: UUID of the circuit

**Response** (204): No content

---

## Simulation Management

### `POST /api/circuits/{circuit_id}/simulate`
Start a simulation job for a circuit.

**Parameters**:
- `circuit_id`: UUID of the circuit to simulate

**Request Body**:
```json
{
  "type": "dc|transient|ac",
  "parameters": {
    // For DC analysis
    "analysis": "operating_point"
    
    // For transient analysis  
    "stop_time": 0.01,
    "step_time": 0.0001,
    "start_time": 0,
    "max_time_step": 0.001
    
    // For AC frequency analysis
    "start_frequency": 1.0,
    "stop_frequency": 10000.0,
    "points_per_decade": 20,
    "variation": "dec"  // "dec" or "lin"
  },
  "priority": 5  // 1 (lowest) to 10 (highest)
}
```

**Response** (202):
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "circuit_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "dc",
  "priority": 5,
  "status": "pending",
  "progress": 0.0,
  "eta_seconds": null,
  "message": "Simulation queued",
  "created_at": "2025-08-27T12:00:00Z",
  "started_at": null,
  "completed_at": null
}
```

### `GET /api/simulations/{job_id}`
Get simulation job status.

**Parameters**:
- `job_id`: UUID of the simulation job

**Response** (200):
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "circuit_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "dc",
  "priority": 5,
  "status": "completed",
  "progress": 100.0,
  "eta_seconds": null,
  "message": "DC analysis complete",
  "created_at": "2025-08-27T12:00:00Z",
  "started_at": "2025-08-27T12:00:01Z",
  "completed_at": "2025-08-27T12:00:03Z"
}
```

**Status Values**:
- `pending`: Job queued, not started
- `running`: Simulation in progress
- `completed`: Simulation finished successfully
- `failed`: Simulation failed with error
- `cancelled`: Job cancelled by user

### `DELETE /api/simulations/{job_id}`
Cancel a simulation job.

**Parameters**:
- `job_id`: UUID of the simulation job

**Response** (204): No content

### `GET /api/simulations`
List all simulation jobs with pagination.

**Query Parameters**:
- `skip` (int): Number of simulations to skip (default: 0)
- `limit` (int): Maximum simulations to return (default: 100, max: 1000)

**Response** (200):
```json
{
  "simulations": [
    {
      "job_id": "123e4567-e89b-12d3-a456-426614174000",
      "circuit_id": "550e8400-e29b-41d4-a716-446655440000",
      "type": "dc",
      "priority": 5,
      "status": "completed",
      "progress": 100.0,
      "message": "DC analysis complete",
      "created_at": "2025-08-27T12:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### `GET /api/simulations/{job_id}/results`
Get simulation results.

**Parameters**:
- `job_id`: UUID of the simulation job

**Response** (200):

**DC Analysis Results**:
```json
{
  "voltages": {
    "0": 0.0,      // Ground node
    "1": 5.0,      // Node 1 voltage
    "2": 3.333     // Node 2 voltage  
  },
  "currents": {
    "v1": 0.001667  // Current through V1
  },
  "time": null,
  "metadata": {
    "temperature": 25,
    "circuit_name": "RC Filter"
  }
}
```

**AC Analysis Results**:
```json
{
  "voltages": {
    "2": {
      "magnitude": [1.0, 0.707, 0.316, ...],  // |V(2)| vs frequency
      "phase": [0, -45, -71.6, ...],          // ∠V(2) vs frequency  
      "complex": true
    }
  },
  "currents": {
    "v1": {
      "magnitude": [0.001, 0.0007, ...],
      "phase": [90, 45, ...],
      "complex": true
    }
  },
  "frequency": [1, 10, 100, 1000, 10000],     // Frequency points (Hz)
  "metadata": {
    "start_frequency": 1.0,
    "stop_frequency": 10000.0,
    "points_per_decade": 20,
    "variation": "dec",
    "circuit_name": "RC Filter"
  }
}
```

---

## WebSocket Real-time Updates

### `WS /ws/simulation/{job_id}`
WebSocket connection for real-time simulation updates.

**Connection URL**: `ws://localhost:8000/ws/simulation/{job_id}`

#### Messages from Server

**Connection Established**:
```json
{
  "type": "connection",
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Connected to simulation updates",
  "timestamp": "2025-08-27T12:00:00.000Z"
}
```

**Progress Update**:
```json
{
  "type": "progress",
  "job_id": "123e4567-e89b-12d3-a456-426614174000", 
  "data": {
    "progress": 45.2,
    "message": "Running DC analysis...",
    "status": "running"
  },
  "timestamp": "2025-08-27T12:00:01.500Z"
}
```

**Simulation Complete**:
```json
{
  "type": "result",
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "data": {
    "status": "completed",
    "results_available": true,
    "message": "Simulation completed"
  },
  "timestamp": "2025-08-27T12:00:03.000Z"
}
```

#### Messages to Server

**Ping**:
```json
{
  "type": "ping"
}
```

**Cancel Simulation**:
```json
{
  "type": "command",
  "action": "cancel"
}
```

**Request Status**:
```json
{
  "type": "command", 
  "action": "status"
}
```

#### Server Responses

**Pong**:
```json
{
  "type": "pong",
  "message": "WebSocket connection active",
  "timestamp": "2025-08-27T12:00:00.000Z"
}
```

**Command Acknowledgment**:
```json
{
  "type": "command_ack",
  "action": "cancel",
  "message": "Simulation cancellation requested",
  "timestamp": "2025-08-27T12:00:00.000Z"
}
```

**Error**:
```json
{
  "type": "error",
  "message": "Invalid command action: unknown",
  "timestamp": "2025-08-27T12:00:00.000Z"
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error description"
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created successfully
- `202` - Accepted (async operation started)
- `204` - No content (successful deletion)
- `400` - Bad request (invalid input)
- `404` - Resource not found
- `409` - Conflict (e.g., results not ready)
- `422` - Validation error
- `500` - Internal server error

### Example Error Response

```json
{
  "detail": "Circuit not found"
}
```

---

## Rate Limiting

- **Default**: 100 requests per minute per IP
- **Headers** (included in responses):
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Requests remaining in window
  - `X-RateLimit-Reset`: Time when window resets

---

## Client Libraries & Examples

### Python Example

```python
import requests
import websockets
import json
import asyncio

# Create circuit
circuit_data = {
    "name": "Test Circuit",
    "components": [
        {
            "type": "voltage_source",
            "name": "V1",
            "positive_node": "1", 
            "negative_node": "0",
            "value": "5V"
        }
    ]
}

response = requests.post("http://localhost:8000/api/circuits", json=circuit_data)
circuit_id = response.json()["id"]

# Start simulation
sim_data = {"type": "dc", "parameters": {}, "priority": 5}
response = requests.post(f"http://localhost:8000/api/circuits/{circuit_id}/simulate", json=sim_data)
job_id = response.json()["job_id"]

# WebSocket monitoring
async def monitor_simulation():
    uri = f"ws://localhost:8000/ws/simulation/{job_id}"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            data = json.loads(message)
            print(f"Update: {data['type']} - {data.get('message', '')}")
            
            if data['type'] == 'result':
                break

asyncio.run(monitor_simulation())
```

### cURL Examples

```bash
# Create circuit
curl -X POST http://localhost:8000/api/circuits \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RC Filter",
    "components": [...]
  }'

# Start simulation  
curl -X POST http://localhost:8000/api/circuits/{circuit_id}/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "dc",
    "parameters": {},
    "priority": 5
  }'

# Get results
curl http://localhost:8000/api/simulations/{job_id}/results
```

---

## Limits & Constraints

- **Maximum Components**: 10,000 per circuit
- **Maximum Simulation Time**: 300 seconds  
- **WebSocket Connections**: 10 per simulation job
- **Result Retention**: 24 hours
- **File Upload Size**: 10MB (for netlist import - future feature)

---

**Last Updated**: August 27, 2025  
**API Version**: 1.0.0