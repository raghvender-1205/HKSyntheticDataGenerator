import os
from typing import List, Dict, Any, Optional
from PyPDF2 import PdfReader
from pydantic import BaseModel, Field

from core.datasource import DataSource, DataSourceConfig, Document

class PDFDataSourceConfig(DataSourceConfig):
    """
    Configuration for the PDF datasource.
    """
    source_type: str = "pdf"
    file_path: str
    extract_images: bool = False
    page_separator: str = "\n\n"  # Separator between pages
    encoding: str = "utf-8"  # For metadata

class PDFDataSource(DataSource):
    """
    A datasource that loads documents from PDF files.
    """
    plugin_id = "pdf_datasource"
    
    def __init__(self, config: PDFDataSourceConfig):
        """
        Initialize the PDF datasource.
        
        Args:
            config: Configuration for the PDF datasource
        """
        self.config = config
        self.file_path = config.file_path
        self.extract_images = config.extract_images
        self.page_separator = config.page_separator
        self.encoding = config.encoding
    
    async def load(self) -> List[Document]:
        """
        Load documents from the PDF file.
        
        Returns:
            A list of Document objects (one per page)
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        documents = []
        
        try:
            # Open the PDF file
            pdf_reader = PdfReader(self.file_path)
            
            # Process each page
            for i, page in enumerate(pdf_reader.pages):
                # Extract text from the page
                text = page.extract_text()
                
                # Skip empty pages
                if not text.strip():
                    continue
                
                # Create a document for the page
                documents.append(Document(
                    content=text,
                    metadata={
                        "source": self.file_path,
                        "page": i + 1,
                        "type": "pdf",
                        "total_pages": len(pdf_reader.pages)
                    }
                ))
            
            # If no pages were extracted, create a single empty document
            if not documents:
                documents.append(Document(
                    content="",
                    metadata={
                        "source": self.file_path,
                        "type": "pdf",
                        "error": "No text content found in PDF"
                    }
                ))
                
        except Exception as e:
            # Handle errors during PDF processing
            documents.append(Document(
                content=f"Error processing PDF: {str(e)}",
                metadata={
                    "source": self.file_path,
                    "type": "pdf",
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
        exists = os.path.exists(self.file_path)
        info = {
            "id": self.plugin_id,
            "name": self.config.name,
            "description": self.config.description,
            "file_path": self.file_path,
            "exists": exists
        }
        
        if exists:
            try:
                # Try to get page count
                pdf_reader = PdfReader(self.file_path)
                info["page_count"] = len(pdf_reader.pages)
            except Exception as e:
                info["error"] = str(e)
                
        return info
    
    @staticmethod
    def get_config_schema() -> Dict[str, Any]:
        """
        Get the JSON schema for the datasource configuration.
        
        Returns:
            A dictionary representing the JSON schema
        """
        return {
            "title": "PDF DataSource Configuration",
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
                    "default": "pdf",
                    "enum": ["pdf"],
                },
                "file_path": {
                    "type": "string",
                    "title": "File Path",
                    "description": "Path to the PDF file",
                },
                "extract_images": {
                    "type": "boolean",
                    "title": "Extract Images",
                    "description": "Whether to extract images from the PDF",
                    "default": False,
                },
                "page_separator": {
                    "type": "string",
                    "title": "Page Separator",
                    "description": "Separator to use between pages",
                    "default": "\n\n",
                },
                "encoding": {
                    "type": "string",
                    "title": "Encoding",
                    "description": "Encoding for metadata",
                    "default": "utf-8",
                },
            },
            "required": ["source_id", "name", "file_path"],
        } 