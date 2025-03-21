import os
import json
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import asyncio

from core.llm import LLMProvider, LLMConfig, LLMResponse

class GroqLLMConfig(LLMConfig):
    """
    Configuration for the Groq LLM provider.
    """
    provider: str = "groq"
    base_url: str = "https://api.groq.com/openai/v1"
    api_key: str = os.getenv("GROQ_API_KEY", "")
    model: str = "llama3-8b-8192"  # Default model
    system_prompt: Optional[str] = None

class GroqLLMProvider(LLMProvider):
    """
    An LLM provider that uses Groq API.
    """
    plugin_id = "groq_llm"
    
    def __init__(self, config: GroqLLMConfig):
        """
        Initialize the Groq LLM provider.
        
        Args:
            config: Configuration for the Groq LLM provider
        """
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self.api_key = config.api_key
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.system_prompt = config.system_prompt
        
        # Default headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Generate text using the Groq API.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters for the LLM
            
        Returns:
            An LLMResponse object
        """
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        messages = []
        
        # Add system message if provided
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        request_data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=request_data,
                timeout=120.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Error calling Groq API: {response.text}")
            
            response_data = response.json()
            
            message_content = response_data["choices"][0]["message"]["content"]
            
            return LLMResponse(
                text=message_content,
                metadata={
                    "model": self.model,
                    "prompt": prompt,
                    "usage": response_data.get("usage", {}),
                    "finish_reason": response_data["choices"][0]["finish_reason"]
                }
            )
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[LLMResponse]:
        """
        Generate text for multiple prompts using the Groq API.
        
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
        # Check if API key is valid
        is_valid_api_key = bool(self.api_key)
        
        # List of known Groq models
        known_models = [
            "llama3-8b-8192",
            "llama3-70b-8192",
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]
        
        # Try to get models list if API key is present
        available_models = []
        if is_valid_api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/models",
                        headers=self.headers,
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        models_data = response.json()
                        available_models = [model["id"] for model in models_data.get("data", [])]
                    else:
                        available_models = known_models
            except Exception:
                available_models = known_models
        else:
            available_models = known_models
        
        return {
            "id": self.plugin_id,
            "name": self.config.name,
            "description": self.config.description,
            "provider": "groq",
            "model": self.model,
            "base_url": self.base_url,
            "has_api_key": is_valid_api_key,
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
            "title": "Groq LLM Provider Configuration",
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
                    "default": "groq",
                    "enum": ["groq"],
                },
                "base_url": {
                    "type": "string",
                    "title": "Base URL",
                    "description": "Base URL for the Groq API",
                    "default": "https://api.groq.com/openai/v1",
                },
                "api_key": {
                    "type": "string",
                    "title": "API Key",
                    "description": "API key for authentication",
                },
                "model": {
                    "type": "string",
                    "title": "Model",
                    "description": "Model to use",
                    "default": "llama3-8b-8192",
                    "enum": [
                        "llama3-8b-8192",
                        "llama3-70b-8192",
                        "mixtral-8x7b-32768",
                        "gemma-7b-it"
                    ]
                },
                "temperature": {
                    "type": "number",
                    "title": "Temperature",
                    "description": "Temperature for text generation",
                    "default": 0.7,
                    "minimum": 0,
                    "maximum": 1,
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
            "required": ["model_id", "name", "api_key", "model"],
        } 