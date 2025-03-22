import os
from typing import List, Dict, Any, Optional
import sqlalchemy
from sqlalchemy import create_engine, text
from pydantic import BaseModel, Field

from core.datasource import DataSource, DataSourceConfig, Document

class SQLDataSourceConfig(DataSourceConfig):
    """
    Configuration for the SQL datasource.
    """
    source_type: str = "sql"
    connection_string: str
    query: str  # SQL query to execute
    row_format: str = "json"  # How to format each row: "json", "text", or "key_value"
    batch_size: int = 1000  # Number of rows to fetch per batch

class SQLDataSource(DataSource):
    """
    A datasource that loads documents from SQL databases.
    """
    plugin_id = "sql_datasource"
    
    def __init__(self, config: SQLDataSourceConfig):
        """
        Initialize the SQL datasource.
        
        Args:
            config: Configuration for the SQL datasource
        """
        self.config = config
        self.connection_string = config.connection_string
        self.query = config.query
        self.row_format = config.row_format
        self.batch_size = config.batch_size
        self._engine = None
    
    @property
    def engine(self):
        """Get SQLAlchemy engine, creating it if it doesn't exist."""
        if self._engine is None:
            self._engine = create_engine(self.connection_string)
        return self._engine
    
    async def load(self) -> List[Document]:
        """
        Load documents from the SQL database.
        
        Returns:
            A list of Document objects (one per row or custom grouping)
        """
        documents = []
        
        try:
            # Connect to the database
            with self.engine.connect() as connection:
                # Execute the query
                result = connection.execute(text(self.query))
                
                # Get column names
                columns = result.keys()
                
                # Process rows
                for i, row in enumerate(result):
                    # Format row based on configuration
                    if self.row_format == "json":
                        # Convert row to dict
                        row_dict = {col: row[col] for col in columns}
                        content = str(row_dict)
                    elif self.row_format == "text":
                        # Join all columns with spaces
                        content = " ".join(str(row[col]) for col in columns)
                    elif self.row_format == "key_value":
                        # Format as "key: value" pairs
                        content = "\n".join(f"{col}: {row[col]}" for col in columns)
                    else:
                        content = str(row)
                    
                    # Create a document for the row
                    documents.append(Document(
                        content=content,
                        metadata={
                            "source": self.connection_string,
                            "query": self.query,
                            "row": i + 1,
                            "type": "sql",
                            "format": self.row_format,
                            "columns": list(columns)
                        }
                    ))
                    
                    # Stop if we've reached the batch size
                    if len(documents) >= self.batch_size:
                        break
            
            # If no rows were processed, create a single empty document
            if not documents:
                documents.append(Document(
                    content="",
                    metadata={
                        "source": self.connection_string,
                        "query": self.query,
                        "type": "sql",
                        "error": "No rows returned"
                    }
                ))
                
        except Exception as e:
            # Handle errors during database connection or query execution
            documents.append(Document(
                content=f"Error executing query: {str(e)}",
                metadata={
                    "source": self.connection_string,
                    "query": self.query,
                    "type": "sql",
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
        info = {
            "id": self.plugin_id,
            "name": self.config.name,
            "description": self.config.description,
            "connection_string": self.connection_string.split("@")[-1] if "@" in self.connection_string else "...",  # Hide credentials
            "query": self.query
        }
        
        try:
            # Test connection and get database info
            with self.engine.connect() as connection:
                info["connected"] = True
                info["database_version"] = str(connection.execute(text("SELECT version();")).fetchone()[0])
        except Exception as e:
            info["connected"] = False
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
            "title": "SQL DataSource Configuration",
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
                    "default": "sql",
                    "enum": ["sql"],
                },
                "connection_string": {
                    "type": "string",
                    "title": "Connection String",
                    "description": "Database connection string (e.g., postgresql://user:password@localhost/dbname)",
                },
                "query": {
                    "type": "string",
                    "title": "SQL Query",
                    "description": "SQL query to execute",
                },
                "row_format": {
                    "type": "string",
                    "title": "Row Format",
                    "description": "How to format each row in the result",
                    "default": "json",
                    "enum": ["json", "text", "key_value"],
                },
                "batch_size": {
                    "type": "integer",
                    "title": "Batch Size",
                    "description": "Maximum number of rows to fetch",
                    "default": 1000,
                    "minimum": 1,
                    "maximum": 10000,
                },
            },
            "required": ["source_id", "name", "connection_string", "query"],
        } 