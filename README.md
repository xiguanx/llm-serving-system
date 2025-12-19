## Distributed LLM Serving
A production-ready text-generation service with focus on distributed systems, observability, and reliability patterns.
### Project Goals

- Build a runnable, measurable, and observable LLM serving system
- Implement production-grade reliability patterns (backpressure, retries, idempotency)
- Demonstrate systems engineering skills beyond simple AI wrappers

### Architecture
The system follows a layered architecture:

Request Flow:

1. Client → HTTP/REST requests
2. FastAPI Gateway → Request handling, validation, and middleware
    - Request validation and rate limiting
    - Prometheus metrics collection
    - OpenTelemetry distributed tracing
    - Backpressure control (queue management)
3. LLM Engine → Model inference
    - Simple Engine (Hugging Face Transformers - Milestone 1)
    - vLLM Engine (High-performance serving - Milestone 2)
4. Monitoring Stack
    - Prometheus for metrics aggregation
    - Grafana for visualization and dashboards

### Prerequisites

Windows 11 + WSL2 (or Linux/macOS)

Docker Desktop installed and running

Python 3.10+

At least 8GB RAM (16GB recommended)

### Quick Start
1. Clone and Setup
```bash
# Execute in WSL2
git clone <your-repo>
cd distributed-llm-serving

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows WSL2

### Install dependencies
pip install -r requirements.txt

### Copy environment variables
cp .env.example .env
```
2. Local Development (without Docker)
```bash
# start services
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Visit:

API: http://localhost:8000

Docs: http://localhost:8000/docs

Metrics: http://localhost:8000/metrics

3. Docker Deployment
```bash
# build and start all services
docker-compose up --build

# Execution in background
docker-compose up -d

# Check logs
docker-compose logs -f llm-server

# Stop service
docker-compose down
```
Visit:

API: http://localhost:8000

Prometheus: http://localhost:9091

Grafana: http://localhost:3000 (admin/admin)

### API Usage
Health Check
```bash
curl http://localhost:8000/health
```
Chat Completion (Non-streaming)
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello! Tell me about distributed systems."}
    ],
    "temperature": 0.7,
    "max_tokens": 150
  }'
```
Chat Completion (Streaming)
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain Docker in simple terms"}
    ],
    "stream": true,
    "max_tokens": 200
  }'
```
Python Client Example
```python
import httpx
import asyncio

async def test_chat():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "What is FastAPI?"}
                ],
                "temperature": 0.7,
                "max_tokens": 100
            }
        )
        print(response.json())

asyncio.run(test_chat())
```
### Monitoring
#### Prometheus Metrics

Visit http://localhost:8000/metrics :

llm_requests_total - total number of requests

llm_requests_in_progress - requests in progress

llm_request_duration_seconds - request duration

llm_generation_tokens - tokens generated

llm_generation_latency_seconds - generation latency

llm_engine_errors_total - total number of engine errors

#### Grafana Dashboard

Visit http://localhost:3000

Login (admin/admin)

Add Prometheus data source: http://prometheus:9090

Ingest dashboard JSON

### Milestone

#### Milestone 1: Baseline & Streaming

FastAPI gateway with metrics
Simple transformer engine
Health checks and monitoring


#### Milestone 2: Engine Swap (in progress)

vLLM integration
OpenAI-compatible API
Performance benchmarking


#### Milestone 3: Reliability

Backpressure control
Safe retries
Idempotency


#### Milestone 4: Ops Shape-up

SLO targets
Alert rules
Runbook


#### Milestone 5: Efficiency

Cost optimization
Batching strategies


#### Milestone 6: Hardening

Graceful shutdown
Failure drills

### Testing

Unit Tests
```bash
pytest tests/ -v
```

Load Testing
```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py --host http://localhost:8000
```
Visit http://localhost:8089 for configuration and backpressure
### Configuration
Edit .env to adjust configuration:
```bash
# Switch to larger model (more storage required)
MODEL_NAME=gpt2-medium

#### Start backpressure
ENABLE_BACKPRESSURE=true
QUEUE_CAPACITY=50

#### Adjust concurrency limitations
MAX_CONCURRENT_REQUESTS=5
```
### Development Notes
CPU vs GPU

Current configuration is optimized for CPU. If you have GPU:

1. Modify engine/simple_engine.py:

```python
self.device = "cuda" if torch.cuda.is_available() else "cpu"
```

2. Install GPU version of PyTorch:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```
#### Using Colab GPU for Performance Testing
For Milestone 5 performance optimization:

1. Start service in Colab
2. Expose port using ngrok
3. Run load tests locally connecting to Colab endpoint
4. Collect real performance data in GPU environment

### Troubleshooting
Docker Out of Memory
```bash
# Increase Docker memory limit (Docker Desktop -> Settings -> Resources)
# Recommend at least 8GB
```
### Resources

FastAPI Documentation

vLLM Documentation

Prometheus Best Practices

OpenTelemetry Tracing