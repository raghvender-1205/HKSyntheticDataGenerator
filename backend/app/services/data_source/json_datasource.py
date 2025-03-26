from typing import List, Dict
import json
import os

from app.models import DataSourceConfig
from app.services.base import BaseDataSource


class JSONDataSource(BaseDataSource):
    """
    Data source for handling JSON data.
    """
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        
        # Add fallback logic for missing source_path
        if not hasattr(config, 'source_path'):
            if isinstance(config, dict) and 'source_path' in config:
                self.json_directory = config['source_path']
            else:
                # Fallback to default directory
                self.json_directory = "data/uploads"
                print(f"Warning: source_path not found in config, using default: {self.json_directory}")
        else:
            self.json_directory = config.source_path
        
        # Initialize parameters if needed
        self.parameters = {}
        if hasattr(config, 'parameters') and config.parameters is not None:
            self.parameters = config.parameters
        elif isinstance(config, dict) and 'parameters' in config:
            self.parameters = config['parameters']
        
        # Set default parameters if not specified
        if not self.parameters:
            self.parameters = {
                "extract_metadata": "true",
                "extract_layout": "true"
            }
        
        # Ensure the directory exists
        os.makedirs(self.json_directory, exist_ok=True)
        
    async def fetch_data(self, limit: int) -> List[Dict]:
        """
        Fetches data from JSON files in the configured directory or from direct JSON input.
        
        Args:
            limit: Maximum number of JSON documents to process
            
        Returns:
            List of dictionaries containing the JSON data
        """
        results = []
        files_processed = 0
        
        # If we have direct JSON data in the config, use that
        if hasattr(self.config, 'json_data') and self.config.json_data:
            try:
                json_data = json.loads(self.config.json_data)
                if isinstance(json_data, list):
                    results.extend(json_data[:limit])
                else:
                    results.append(json_data)
                return results
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON data: {str(e)}")
                return []
        
        # Otherwise, process JSON files from the directory
        for filename in os.listdir(self.json_directory):
            if not filename.lower().endswith('.json'):
                continue
                
            if files_processed >= limit:
                break
                
            file_path = os.path.join(self.json_directory, filename)
            try:
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                    
                # Handle both single objects and arrays
                if isinstance(json_data, list):
                    results.extend(json_data[:limit - len(results)])
                else:
                    results.append(json_data)
                    
                files_processed += 1
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                
        return results
        
    async def get_schema(self) -> Dict:
        """
        Returns the schema of the JSON data.
        
        Returns:
            Dictionary representing the schema of the JSON data
        """
        # Get a sample of the data to infer the schema
        sample_data = await self.fetch_data(1)
        if not sample_data:
            return {"type": "object", "properties": {}}
            
        # For now, return a simple schema based on the first item
        first_item = sample_data[0]
        if isinstance(first_item, dict):
            return {
                "type": "object",
                "properties": {
                    key: {"type": type(value).__name__}
                    for key, value in first_item.items()
                }
            }
        else:
            return {
                "type": "array",
                "items": {"type": type(first_item).__name__}
            } 