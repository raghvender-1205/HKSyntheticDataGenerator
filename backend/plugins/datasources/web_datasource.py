import os
from typing import List, Dict, Any, Optional
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from pydantic import BaseModel, Field

from core.datasource import DataSource, DataSourceConfig, Document

class WebDataSourceConfig(DataSourceConfig):
    """
    Configuration for the web datasource.
    """
    source_type: str = "web"
    url: str  # URL to crawl
    max_pages: int = 10  # Maximum number of pages to crawl
    depth: int = 2  # Depth of crawling (1 = just the given URL)
    same_domain: bool = True  # Whether to stay on the same domain
    extract_text: bool = True  # Whether to extract text content
    extract_metadata: bool = True  # Whether to extract metadata
    timeout: int = 30  # Timeout in seconds

class WebDataSource(DataSource):
    """
    A datasource that crawls websites and extracts content.
    """
    plugin_id = "web_datasource"
    
    def __init__(self, config: WebDataSourceConfig):
        """
        Initialize the web datasource.
        
        Args:
            config: Configuration for the web datasource
        """
        self.config = config
        self.url = config.url
        self.max_pages = config.max_pages
        self.depth = config.depth
        self.same_domain = config.same_domain
        self.extract_text = config.extract_text
        self.extract_metadata = config.extract_metadata
        self.timeout = config.timeout
    
    async def load(self) -> List[Document]:
        """
        Load documents from the web by crawling.
        
        Returns:
            A list of Document objects (one per page)
        """
        documents = []
        
        try:
            # Create a crawl4ai crawler
            crawler = AsyncWebCrawler()
            
            # Configure the crawler
            crawler_config = CrawlerRunConfig(
                urls=[self.url],
                max_pages=self.max_pages,
                max_depth=self.depth,
                stay_within_same_domain=self.same_domain,
                timeout=self.timeout
            )
            
            # Run the crawler synchronously in an async function
            result = await crawler.crawl(crawler_config)
            
            # Process results - each page becomes a document
            for page in result.pages:
                if not page.text or not page.text.strip():
                    continue
                
                # Create metadata
                metadata = {
                    "source": page.url,
                    "url": page.url,
                    "type": "web",
                    "title": page.title or "",
                    "status_code": page.status_code
                }
                
                # Create a document for the page
                documents.append(Document(
                    content=page.text,
                    metadata=metadata
                ))
            
            # If no pages were crawled, create a single empty document
            if not documents:
                documents.append(Document(
                    content="",
                    metadata={
                        "source": self.url,
                        "type": "web",
                        "error": "No content found during crawling"
                    }
                ))
                
        except Exception as e:
            # Handle errors during crawling
            documents.append(Document(
                content=f"Error crawling website: {str(e)}",
                metadata={
                    "source": self.url,
                    "type": "web",
                    "error": str(e)
                }
            ))
        
        return documents
    
    async def get_info(self) -> Dict[str, Any]:
        """
        Get information about the datasource.
        
        Returns:
            A dictionary with information about the datasource
        """
        return {
            "id": self.plugin_id,
            "name": self.config.name,
            "description": self.config.description,
            "url": self.url,
            "max_pages": self.max_pages,
            "depth": self.depth,
            "same_domain": self.same_domain
        }
    
    @staticmethod
    def get_config_schema() -> Dict[str, Any]:
        """
        Get the JSON schema for the datasource configuration.
        
        Returns:
            A dictionary representing the JSON schema
        """
        return {
            "title": "Web DataSource Configuration",
            "type": "object",
            "properties": {
                "source_id": {
                    "type": "string",
                    "title": "Source ID",
                    "description": "Unique identifier for the datasource",
                },
                "name": {
                    "type": "string",
                    "title": "Name",
                    "description": "Display name for the datasource",
                },
                "description": {
                    "type": "string",
                    "title": "Description",
                    "description": "Description of the datasource",
                },
                "source_type": {
                    "type": "string",
                    "title": "Source Type",
                    "description": "Type of datasource",
                    "default": "web",
                    "enum": ["web"],
                },
                "url": {
                    "type": "string",
                    "title": "URL",
                    "description": "URL to crawl",
                    "format": "uri"
                },
                "max_pages": {
                    "type": "integer",
                    "title": "Max Pages",
                    "description": "Maximum number of pages to crawl",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100,
                },
                "depth": {
                    "type": "integer",
                    "title": "Crawl Depth",
                    "description": "Depth of crawling (1 = just the given URL)",
                    "default": 2,
                    "minimum": 1,
                    "maximum": 5,
                },
                "same_domain": {
                    "type": "boolean",
                    "title": "Stay on Same Domain",
                    "description": "Whether to stay on the same domain during crawling",
                    "default": True,
                },
                "extract_text": {
                    "type": "boolean",
                    "title": "Extract Text",
                    "description": "Whether to extract text content from pages",
                    "default": True,
                },
                "extract_metadata": {
                    "type": "boolean",
                    "title": "Extract Metadata",
                    "description": "Whether to extract metadata (title, links, etc.)",
                    "default": True,
                },
                "timeout": {
                    "type": "integer",
                    "title": "Timeout",
                    "description": "Timeout in seconds for each page",
                    "default": 30,
                    "minimum": 5,
                    "maximum": 120,
                },
            },
            "required": ["source_id", "name", "url"],
        } 