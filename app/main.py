from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
import time
import uuid

from app.config import settings
from app.models import ChatRequest, ChatResponse, HealthResponse
from engine.simple_engine import SimpleEngine
from middleware.metrics import MetricsMiddleware, metrics_endpoint, record_generation_metrics

# global variables
engine = None
app_start_time = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """application lifespan manager"""
    global engine, app_start_time
    
    # initialize engine
    print("Initializing LLM engine...")
    app_start_time = time.time()
    
    if settings.engine_type == "simple":
        engine = SimpleEngine(model_name=settings.model_name)
    else:
        raise ValueError(f"Unknown engine type: {settings.engine_type}")
    
    await engine.initialize()
    print("Engine initialized successfully")
    
    yield
    
    # cleanup
    print("Shutting down engine...")
    await engine.shutdown()
    print("Shutdown complete")

# create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# add metrics middleware
if settings.enable_metrics:
    app.add_middleware(MetricsMiddleware)

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """health check endpoint"""
    from middleware.metrics import requests_total, requests_in_progress
    
    # get total requests
    total_requests = sum(
        metric.collect()[0].samples[0].value 
        for metric in [requests_total]
    )
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        model=engine.model_name,
        uptime=time.time() - app_start_time,
        requests_total=0,
        requests_active=0
    )

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics"""
    return metrics_endpoint()

# Chat completion endpoint
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """OpenAI-compatible chat completions endpoint"""
    
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        if request.stream:
            # streaming response
            async def stream_generator():
                async for chunk in engine.generate_stream(
                    messages=request.messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ):
                    chunk_data = {
                        "id": request_id,
                        "object": "chat.completion.chunk",
                        "created": int(start_time),
                        "model": engine.model_name,
                        "choices": [{
                            "index": 0,
                            "delta": {"content": chunk},
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {chunk_data}\n\n"
                
                # final chunk
                final_chunk = {
                    "id": request_id,
                    "object": "chat.completion.chunk",
                    "created": int(start_time),
                    "model": engine.model_name,
                    "choices": [{
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {final_chunk}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream"
            )
        else:
            # non-streaming response
            response_text = await engine.generate(
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            # calculate prompt and completion tokens（simplified）
            prompt_tokens = sum(len(m.content.split()) for m in request.messages)
            completion_tokens = len(response_text.split())
            total_time = time.time() - start_time
            
            # record generation metrics
            record_generation_metrics(
                tokens=completion_tokens,
                ttft=total_time,  # simplified，actually should be the time taken to generate the first token
                total_time=total_time
            )
            
            return ChatResponse(
                id=request_id,
                created=int(start_time),
                model=engine.model_name,
                choices=[{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }],
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            )
    
    except Exception as e:
        from middleware.metrics import engine_errors
        engine_errors.labels(error_type=type(e).__name__).inc()
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": str(e),
                    "type": type(e).__name__,
                    "code": "internal_error"
                }
            }
        )

@app.get("/")
async def root():
    """root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs"
    }