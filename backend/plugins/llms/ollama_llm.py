import os
import json
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import asyncio

from core.llm import LLMProvider, LLMConfig, LLMResponse

class OllamaLLMConfig(LLMConfig):
    """
    Configuration for the Ollama LLM provider.
    """
    provider: str = "ollama"
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model: str = "llama2"  # The model to use
    system_prompt: Optional[str] = None

class OllamaLLMProvider(LLMProvider):
    """
    An LLM provider that uses Ollama API.
    """
    plugin_id = "ollama_llm"
    
    def __init__(self, config: OllamaLLMConfig):
        """
        Initialize the Ollama LLM provider.
        
        Args:
            config: Configuration for the Ollama LLM provider
        """
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.system_prompt = config.system_prompt
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Generate text using the Ollama API.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters for the LLM
            
        Returns:
            An LLMResponse object
        """
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        request_data = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if self.system_prompt:
            request_data["system"] = self.system_prompt
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=request_data,
                timeout=120.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Error calling Ollama API: {response.text}")
            
            response_data = response.json()
            
            return LLMResponse(
                text=response_data.get("response", ""),
                metadata={
                    "model": self.model,
                    "prompt": prompt,
                    "total_duration": response_data.get("total_duration", 0),
                    "load_duration": response_data.get("load_duration", 0),
                    "sample_count": response_data.get("sample_count", 0),
                    "sample_duration": response_data.get("sample_duration", 0),
                    "prompt_eval_duration": response_data.get("prompt_eval_duration", 0),
                    "eval_count": response_data.get("eval_count", 0),
                    "eval_duration": response_data.get("eval_duration", 0),
                }
            )
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[LLMResponse]:
        """
        Generate text for multiple prompts using the Ollama API.
        
        Args:
            prompts: A list of input prompts
            **kwargs: Additional parameters for the LLM
            
        Returns:
            A list of LLMResponse objects
        """
        # Create a list of tasks for each prompt
        tasks = [self.generate(prompt, **kwargs) for prompt in prompts]
        
        # Run all tasks concurrently
        responses = await asyncio.gather(*tasks)
        
        return responses
    
    async def get_info(self) -> Dict[str, Any]:
        """
        Get information about the LLM provider.
        
        Returns:
            A dictionary with information about the LLM provider
        """
        # Get list of available models
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                
                if response.status_code != 200:
                    available_models = []
                else:
                    models_data = response.json()
                    available_models = [model["name"] for model in models_data.get("models", [])]
            except Exception:
                available_models = []
        
        return {
            "id": self.plugin_id,
            "name": self.config.name,
            "description": self.config.description,
            "provider": "ollama",
            "model": self.model,
            "base_url": self.base_url,
            "available_models": available_models,
            "parameters": {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
        }
    
    @staticmethod
    def get_config_schema() -> Dict[str, Any]:
        """
        Get the JSON schema for the LLM provider configuration.
        
        Returns:
            A dictionary representing the JSON schema
        """
        return {
            "title": "Ollama LLM Provider Configuration",
            "type": "object",
            "properties": {
                "model_id": {
                    "type": "string",
                    "title": "Model ID",
                    "description": "Unique identifier for the LLM model",
                },
                "name": {
                    "type": "string",
                    "title": "Name",
                    "description": "Display name for the LLM provider",
                },
                "description": {
                    "type": "string",
                    "title": "Description",
                    "description": "Description of the LLM provider",
                },
                "provider": {
                    "type": "string",
                    "title": "Provider",
                    "description": "LLM provider type",
                    "default": "ollama",
                    "enum": ["ollama"],
                },
                "base_url": {
                    "type": "string",
                    "title": "Base URL",
                    "description": "Base URL for the Ollama API",
                    "default": "http://localhost:11434",
                },
                "model": {
                    "type": "string",
                    "title": "Model",
                    "description": "Model to use",
                    "default": "llama2",
                },
                "temperature": {
                    "type": "number",
                    "title": "Temperature",
                    "description": "Temperature for text generation",
                    "default": 0.7,
                    "minimum": 0,
                    "maximum": 2,
                },
                "max_tokens": {
                    "type": "integer",
                    "title": "Max Tokens",
                    "description": "Maximum number of tokens to generate",
                    "default": 1024,
                    "minimum": 1,
                },
                "system_prompt": {
                    "type": "string",
                    "title": "System Prompt",
                    "description": "System prompt to use for text generation",
                },
            },
            "required": ["model_id", "name", "model"],
        } 