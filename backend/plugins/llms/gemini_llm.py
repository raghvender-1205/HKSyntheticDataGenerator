import os
import json
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import asyncio

from core.llm import LLMProvider, LLMConfig, LLMResponse

class GeminiLLMConfig(LLMConfig):
    """
    Configuration for the Google Gemini LLM provider.
    """
    provider: str = "gemini"
    api_key: str = os.getenv("GOOGLE_API_KEY", "")
    model: str = "gemini-1.5-pro"  # Default model
    system_prompt: Optional[str] = None

class GeminiLLMProvider(LLMProvider):
    """
    An LLM provider that uses Google Gemini API.
    """
    plugin_id = "gemini_llm"
    
    def __init__(self, config: GeminiLLMConfig):
        """
        Initialize the Google Gemini LLM provider.
        
        Args:
            config: Configuration for the Gemini LLM provider
        """
        self.config = config
        self.api_key = config.api_key
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.system_prompt = config.system_prompt
        
        # Base URL is constructed using the model
        base_model = self.model.replace("-", "_")
        self.base_url = f"https://generativelanguage.googleapis.com/v1/models/{base_model}"
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Generate text using the Google Gemini API.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters for the LLM
            
        Returns:
            An LLMResponse object
        """
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        # Prepare the request data based on API format
        content = []
        
        # Add system prompt if provided
        if self.system_prompt:
            content.append({
                "role": "system",
                "parts": [{"text": self.system_prompt}]
            })
        
        # Add user message
        content.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
        
        # API params
        params = {
            "key": self.api_key
        }
        
        request_data = {
            "contents": content,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}:generateContent",
                params=params,
                json=request_data,
                timeout=120.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Error calling Gemini API: {response.text}")
            
            response_data = response.json()
            
            if "candidates" not in response_data or not response_data["candidates"]:
                raise Exception("No response from Gemini API")
            
            # Extract the text from the response
            text_parts = []
            for part in response_data["candidates"][0]["content"]["parts"]:
                if "text" in part:
                    text_parts.append(part["text"])
            
            text = "".join(text_parts)
            
            return LLMResponse(
                text=text,
                metadata={
                    "model": self.model,
                    "prompt": prompt,
                    "usage": {
                        "prompt_tokens": response_data.get("usageMetadata", {}).get("promptTokenCount", 0),
                        "completion_tokens": response_data.get("usageMetadata", {}).get("candidatesTokenCount", 0),
                        "total_tokens": response_data.get("usageMetadata", {}).get("totalTokenCount", 0)
                    },
                    "finish_reason": response_data["candidates"][0].get("finishReason", "STOP")
                }
            )
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[LLMResponse]:
        """
        Generate text for multiple prompts using the Gemini API.
        
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
        
        # List of known Gemini models
        known_models = [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro",
            "gemini-1.0-pro-vision"
        ]
        
        # Try to get models list if API key is present
        available_models = []
        if is_valid_api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://generativelanguage.googleapis.com/v1/models",
                        params={"key": self.api_key},
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        models_data = response.json()
                        available_models = [model["name"].split("/")[-1].replace("_", "-") 
                                           for model in models_data.get("models", [])
                                           if "generateContent" in model.get("supportedGenerationMethods", [])]
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
            "provider": "gemini",
            "model": self.model,
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
            "title": "Google Gemini LLM Provider Configuration",
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
                    "default": "gemini",
                    "enum": ["gemini"],
                },
                "api_key": {
                    "type": "string",
                    "title": "API Key",
                    "description": "Google API key for authentication",
                },
                "model": {
                    "type": "string",
                    "title": "Model",
                    "description": "Model to use",
                    "default": "gemini-1.5-pro",
                    "enum": [
                        "gemini-1.5-pro",
                        "gemini-1.5-flash",
                        "gemini-1.0-pro",
                        "gemini-1.0-pro-vision"
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