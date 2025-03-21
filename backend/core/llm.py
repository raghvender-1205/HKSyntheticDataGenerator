from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class LLMConfig(BaseModel):
    """
    Base configuration for LLM providers.
    """
    model_id: str
    name: str
    description: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024

class LLMResponse(BaseModel):
    """
    Response from an LLM.
    """
    text: str
    metadata: Dict[str, Any] = {}

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    All LLM provider plugins must inherit from this class.
    """
    plugin_id: str = "base_llm_provider"
    
    @abstractmethod
    def __init__(self, config: LLMConfig):
        """
        Initialize the LLM provider.
        
        Args:
            config: Configuration for the LLM provider
        """
        self.config = config
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters for the LLM
            
        Returns:
            An LLMResponse object
        """
        pass
    
    @abstractmethod
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[LLMResponse]:
        """
        Generate text for multiple prompts.
        
        Args:
            prompts: A list of input prompts
            **kwargs: Additional parameters for the LLM
            
        Returns:
            A list of LLMResponse objects
        """
        pass
    
    @abstractmethod
    async def get_info(self) -> Dict[str, Any]:
        """
        Get information about the LLM provider.
        
        Returns:
            A dictionary with information about the LLM provider
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_config_schema() -> Dict[str, Any]:
        """
        Get the JSON schema for the LLM provider configuration.
        
        Returns:
            A dictionary representing the JSON schema
        """ 