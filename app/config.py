from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    # App settings
    app_name: str = "Distributed LLM Serving"
    app_version: str = "0.1.0"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Engine settings
    engine_type: Literal["simple", "vllm"] = "simple"
    model_name: str = "gpt2"  # default to a small model
    max_tokens: int = 512
    temperature: float = 0.7
    
    # Performance settings
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    
    # Backpressure settings (Milestone 3)
    enable_backpressure: bool = False
    queue_capacity: int = 100
    
    # Observability
    enable_metrics: bool = True
    enable_tracing: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()