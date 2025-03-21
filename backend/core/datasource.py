from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class Document(BaseModel):
    """
    Represents a document with content and metadata.
    """
    content: str
    metadata: Dict[str, Any] = {}
    
    def __str__(self) -> str:
        return f"Document(content={self.content[:50]}..., metadata={self.metadata})"

class DataSourceConfig(BaseModel):
    """
    Base configuration for data sources.
    """
    source_id: str
    name: str
    description: Optional[str] = None

class DataSource(ABC):
    """
    Abstract base class for data sources.
    All data source plugins must inherit from this class.
    """
    plugin_id: str = "base_datasource"
    
    @abstractmethod
    def __init__(self, config: DataSourceConfig):
        """
        Initialize the data source.
        
        Args:
            config: Configuration for the data source
        """
        self.config = config
    
    @abstractmethod
    async def load(self) -> List[Document]:
        """
        Load documents from the data source.
        
        Returns:
            A list of Document objects
        """
        pass
    
    @abstractmethod
    async def get_info(self) -> Dict[str, Any]:
        """
        Get information about the data source.
        
        Returns:
            A dictionary with information about the data source
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_config_schema() -> Dict[str, Any]:
        """
        Get the JSON schema for the data source configuration.
        
        Returns:
            A dictionary representing the JSON schema
        """
        pass 