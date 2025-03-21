import os
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from core.datasource import DataSource, DataSourceConfig, Document

class FileDataSourceConfig(DataSourceConfig):
    """
    Configuration for the file datasource.
    """
    source_type: str = "file"
    file_path: str
    file_type: str = "txt"  # txt, json, csv, etc.
    encoding: str = "utf-8"

class FileDataSource(DataSource):
    """
    A datasource that loads documents from files.
    """
    plugin_id = "file_datasource"
    
    def __init__(self, config: FileDataSourceConfig):
        """
        Initialize the file datasource.
        
        Args:
            config: Configuration for the file datasource
        """
        self.config = config
        self.file_path = config.file_path
        self.file_type = config.file_type
        self.encoding = config.encoding
    
    async def load(self) -> List[Document]:
        """
        Load documents from the file.
        
        Returns:
            A list of Document objects
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        documents = []
        
        if self.file_type.lower() == "txt":
            # Load a single text file as one document
            with open(self.file_path, "r", encoding=self.encoding) as f:
                content = f.read()
                documents.append(Document(
                    content=content,
                    metadata={
                        "source": self.file_path,
                        "type": "txt"
                    }
                ))
        
        elif self.file_type.lower() == "json":
            # Load a JSON file as one or more documents
            with open(self.file_path, "r", encoding=self.encoding) as f:
                data = json.load(f)
                
                if isinstance(data, list):
                    # Assume each item is a document
                    for i, item in enumerate(data):
                        if isinstance(item, dict):
                            content = item.get("content", str(item))
                            metadata = item.get("metadata", {})
                            metadata["source"] = self.file_path
                            metadata["index"] = i
                            metadata["type"] = "json"
                            
                            documents.append(Document(
                                content=content,
                                metadata=metadata
                            ))
                        else:
                            # If the item is not a dict, use it as content
                            documents.append(Document(
                                content=str(item),
                                metadata={
                                    "source": self.file_path,
                                    "index": i,
                                    "type": "json"
                                }
                            ))
                else:
                    # Assume the JSON object is a single document
                    if isinstance(data, dict):
                        content = data.get("content", str(data))
                        metadata = data.get("metadata", {})
                        metadata["source"] = self.file_path
                        metadata["type"] = "json"
                        
                        documents.append(Document(
                            content=content,
                            metadata=metadata
                        ))
                    else:
                        # If the data is not a dict, use it as content
                        documents.append(Document(
                            content=str(data),
                            metadata={
                                "source": self.file_path,
                                "type": "json"
                            }
                        ))
        
        elif self.file_type.lower() == "csv":
            # Load a CSV file
            import csv
            
            with open(self.file_path, "r", encoding=self.encoding) as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                
                if headers:
                    for i, row in enumerate(reader):
                        # Create a content string from the row
                        content = "\n".join([f"{headers[j]}: {value}" for j, value in enumerate(row) if j < len(headers)])
                        
                        documents.append(Document(
                            content=content,
                            metadata={
                                "source": self.file_path,
                                "row": i + 1,
                                "type": "csv",
                                "headers": headers,
                                "values": row
                            }
                        ))
        
        else:
            # Unsupported file type
            raise ValueError(f"Unsupported file type: {self.file_type}")
        
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
            "file_path": self.file_path,
            "file_type": self.file_type,
            "exists": os.path.exists(self.file_path)
        }
    
    @staticmethod
    def get_config_schema() -> Dict[str, Any]:
        """
        Get the JSON schema for the datasource configuration.
        
        Returns:
            A dictionary representing the JSON schema
        """
        return {
            "title": "File DataSource Configuration",
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
                    "default": "file",
                    "enum": ["file"],
                },
                "file_path": {
                    "type": "string",
                    "title": "File Path",
                    "description": "Path to the file",
                },
                "file_type": {
                    "type": "string",
                    "title": "File Type",
                    "description": "Type of file",
                    "default": "txt",
                    "enum": ["txt", "json", "csv"],
                },
                "encoding": {
                    "type": "string",
                    "title": "Encoding",
                    "description": "File encoding",
                    "default": "utf-8",
                },
            },
            "required": ["source_id", "name", "file_path"],
        } 