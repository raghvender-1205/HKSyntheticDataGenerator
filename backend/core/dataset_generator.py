from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from .datasource import Document
from .llm import LLMProvider

class DatasetGeneratorConfig(BaseModel):
    """
    Base configuration for dataset generators.
    """
    generator_id: str
    name: str
    description: Optional[str] = None

class DatasetItem(BaseModel):
    """
    A single item in a dataset (e.g., a question-answer pair).
    """
    data: Dict[str, Any]
    metadata: Dict[str, Any] = {}

class Dataset(BaseModel):
    """
    A collection of dataset items.
    """
    name: str
    description: Optional[str] = None
    items: List[DatasetItem] = []
    metadata: Dict[str, Any] = {}

class DatasetGenerator(ABC):
    """
    Abstract base class for dataset generators.
    All dataset generator plugins must inherit from this class.
    """
    plugin_id: str = "base_dataset_generator"
    
    @abstractmethod
    def __init__(self, config: DatasetGeneratorConfig):
        """
        Initialize the dataset generator.
        
        Args:
            config: Configuration for the dataset generator
        """
        self.config = config
    
    @abstractmethod
    async def generate(
        self, 
        documents: List[Document], 
        llm_provider: LLMProvider, 
        **kwargs
    ) -> Dataset:
        """
        Generate a dataset from documents using the specified LLM provider.
        
        Args:
            documents: A list of documents to generate the dataset from
            llm_provider: The LLM provider to use
            **kwargs: Additional parameters for the dataset generation
            
        Returns:
            A Dataset object
        """
        pass
    
    @abstractmethod
    async def get_info(self) -> Dict[str, Any]:
        """
        Get information about the dataset generator.
        
        Returns:
            A dictionary with information about the dataset generator
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_config_schema() -> Dict[str, Any]:
        """
        Get the JSON schema for the dataset generator configuration.
        
        Returns:
            A dictionary representing the JSON schema
        """
        pass 