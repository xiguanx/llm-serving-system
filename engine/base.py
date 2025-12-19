from abc import ABC, abstractmethod
from typing import List, AsyncGenerator
from app.models import Message

class BaseEngine(ABC):
    """abstract base class defining the LLM engine interface"""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs
    
    @abstractmethod
    async def initialize(self):
        """init the engine (load the model, etc.)"""
        pass
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        """generate a response (non-streaming)"""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> AsyncGenerator[str, None]:
        """generate a response (streaming)"""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """clean up resources"""
        pass