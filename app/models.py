from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=512, ge=1, le=4096)
    stream: Optional[bool] = False
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "messages": [
                        {"role": "user", "content": "Hello, how are you?"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 150
                }
            ]
        }
    }

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

class StreamChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    version: str
    model: str
    uptime: float
    requests_total: int
    requests_active: int