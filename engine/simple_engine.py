import asyncio
from typing import List, AsyncGenerator
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from app.models import Message
from .base import BaseEngine

class SimpleEngine(BaseEngine):
    """simple engine based on Hugging Face Transformers for CPU mode"""
    
    def __init__(self, model_name: str = "gpt2", **kwargs):
        super().__init__(model_name, **kwargs)
        self.tokenizer = None
        self.model = None
        self.device = "cpu"  # CPU mode
    
    async def initialize(self):
        """load model in background"""
        print(f"Loading model: {self.model_name} on {self.device}")
        
        # load model in background, to avoid blocking the main thread
        loop = asyncio.get_event_loop()
        self.tokenizer, self.model = await loop.run_in_executor(
            None, self._load_model
        )
        print(f"Model loaded successfully")
    
    def _load_model(self):
        """func to load model in background"""
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32,  # CPU mode, use float32
        )
        model.to(self.device)
        model.eval()
        
        # set eos_token as pad_token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        return tokenizer, model
    
    def _messages_to_prompt(self, messages: List[Message]) -> str:
        """turn messages to prompt"""
        prompt_parts = []
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")
        
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)
    
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        """generate response"""
        prompt = self._messages_to_prompt(messages)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            self._generate_sync,
            prompt,
            temperature,
            max_tokens
        )
        return response
    
    def _generate_sync(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """generate response synchronously in thread pool"""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # only return new tokens
        response = response[len(prompt):].strip()
        return response
    
    async def generate_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> AsyncGenerator[str, None]:
        """streaming generate response"""
        # simplified version: yield results in batches
        response = await self.generate(messages, temperature, max_tokens)
        
        # Simulate streaming output (5 characters at a time)
        chunk_size = 5
        for i in range(0, len(response), chunk_size):
            chunk = response[i:i + chunk_size]
            yield chunk
            await asyncio.sleep(0.05)  # simulate generation delay
    
    async def shutdown(self):
        """clean up resources"""
        if self.model is not None:
            del self.model
            del self.tokenizer
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
        print("Engine shutdown complete")