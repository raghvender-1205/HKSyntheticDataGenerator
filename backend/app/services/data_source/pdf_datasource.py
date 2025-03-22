from typing import List, Dict
import os
from unstructured.partition.pdf import partition_pdf
from unstructured.staging.base import elements_to_json

from app.models import DataSourceConfig
from app.services.base import BaseDataSource


class PDFDataSource(BaseDataSource):
    """
    Data source for extracting data from PDF files using the unstructured library.
    """
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.pdf_directory = config.source_path
        
    async def fetch_data(self, limit: int) -> List[Dict]:
        """
        Fetches data from PDF files in the configured directory.
        
        Args:
            limit: Maximum number of PDF documents to process
            
        Returns:
            List of dictionaries containing extracted data from PDFs
        """
        results = []
        files_processed = 0
        
        for filename in os.listdir(self.pdf_directory):
            if not filename.lower().endswith('.pdf'):
                continue
                
            if files_processed >= limit:
                break
                
            file_path = os.path.join(self.pdf_directory, filename)
            try:
                # Extract content from PDF using unstructured
                elements = partition_pdf(file_path)
                
                # Convert elements to structured data
                document_data = elements_to_json(elements)
                
                # Add metadata
                processed_data = {
                    "filename": filename,
                    "source_path": file_path,
                    "content": document_data
                }
                
                results.append(processed_data)
                files_processed += 1
                
            except Exception as e:
                # Handle exceptions but continue processing other files
                print(f"Error processing {filename}: {str(e)}")
                
        return results
        
    async def get_schema(self) -> Dict:
        """
        Returns the schema of the data extracted from PDFs.
        
        Returns:
            Dictionary representing the schema of the extracted data
        """
        return {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "source_path": {"type": "string"},
                "content": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "text": {"type": "string"},
                            "metadata": {"type": "object"}
                        }
                    }
                }
            }
        }
