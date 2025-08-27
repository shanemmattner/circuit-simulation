#!/bin/bash

# FastAPI Circuit Simulation - API Testing Examples
# Make sure the server is running: uv run uvicorn src.api.main:app --reload

BASE_URL="http://localhost:8000"

echo "🚀 Testing FastAPI Circuit Simulation Service"
echo "=============================================="

# 1. Health Check
echo "1. Health Check:"
curl -X GET "$BASE_URL/health" | jq
echo -e "\n"

# 2. Create a simple RC circuit
echo "2. Creating RC Circuit:"
CIRCUIT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/circuits" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RC Filter Test",
    "description": "Simple RC low-pass filter for API testing",
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
  }')

echo $CIRCUIT_RESPONSE | jq
CIRCUIT_ID=$(echo $CIRCUIT_RESPONSE | jq -r '.id')
echo "Circuit ID: $CIRCUIT_ID"
echo -e "\n"

# 3. Get circuit details
echo "3. Getting Circuit Details:"
curl -X GET "$BASE_URL/api/circuits/$CIRCUIT_ID" | jq
echo -e "\n"

# 4. Start DC simulation
echo "4. Starting DC Simulation:"
SIM_RESPONSE=$(curl -s -X POST "$BASE_URL/api/circuits/$CIRCUIT_ID/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "dc",
    "parameters": {"analysis": "operating_point"},
    "priority": 5
  }')

echo $SIM_RESPONSE | jq
JOB_ID=$(echo $SIM_RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"
echo -e "\n"

# 5. Check simulation status
echo "5. Checking Simulation Status:"
curl -X GET "$BASE_URL/api/simulations/$JOB_ID" | jq
echo -e "\n"

# 6. Get simulation results (if completed)
echo "6. Getting Simulation Results:"
curl -X GET "$BASE_URL/api/simulations/$JOB_ID/results" | jq
echo -e "\n"

# 7. List all circuits
echo "7. Listing All Circuits:"
curl -X GET "$BASE_URL/api/circuits" | jq
echo -e "\n"

# 8. List all simulations
echo "8. Listing All Simulations:"
curl -X GET "$BASE_URL/api/simulations" | jq
echo -e "\n"

# 9. Start transient simulation
echo "9. Starting Transient Simulation:"
TRANSIENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/circuits/$CIRCUIT_ID/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "transient",
    "parameters": {
      "stop_time": 0.005,
      "step_time": 0.0001
    },
    "priority": 7
  }')

echo $TRANSIENT_RESPONSE | jq
TRANSIENT_JOB_ID=$(echo $TRANSIENT_RESPONSE | jq -r '.job_id')
echo "Transient Job ID: $TRANSIENT_JOB_ID"
echo -e "\n"

echo "✅ API Testing Complete!"
echo "Visit http://localhost:8000/docs for interactive documentation"