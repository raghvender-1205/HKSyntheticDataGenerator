import pytest
import os
import json
from unittest.mock import patch, AsyncMock
from typing import Dict, Any

from app.models import DatasetType
from app.models import SyntheticDataRequest, SyntheticDataResponse
from app.controllers import SyntheticDataController
from app.services.llm_service import CustomLLMService


# Test payload for the API
TEST_PAYLOAD = {
    "dataset_type": "qa",
    "data_source": {
        "type": "pdf",
        "connection_string": "sample_pdfs/doc.pdf",
        "parameters": {
            "extract_metadata": "true",
            "extract_layout": "true"
        }
    },
    "llm_config": {
        "type": "custom",
        "api_key": "test-api-key",
        "model_name": "custom-model",
        "parameters": {
            "api_base_url": "https://apillm.healthkart.com/v1",
            "temperature": "0.7",
            "max_tokens": "1000",
            "top_p": "0.95"
        }
    },
    "sample_size": 3,
    "output_format": "json"
}

# Mock PDF data - representing content from a real sample PDF
MOCK_PDF_DATA = [
    {
        "filename": "doc.pdf",
        "source_path": "sample_pdfs/doc.pdf",
        "content": [
            {
                "type": "text",
                "text": "Maternity Leave: A female employee who has been in continuous service for a period of at least 80 days in the 12 months immediately preceding the date of her expected delivery, shall be entitled to maternity leave of 26 weeks, which she can take a maximum of 8 weeks prior to delivery.",
                "metadata": {
                    "page_number": 1
                }
            },
            {
                "type": "text",
                "text": "Paternity Leave: Male employees can avail of Paternity Leave up to a maximum period of 5 working days within one month of the birth of their child.",
                "metadata": {
                    "page_number": 2
                }
            }
        ]
    }
]

# Mock synthetic data that will be returned by the LLM
MOCK_SYNTHETIC_DATA = [
    {"question": "What is the duration of maternity leave?", "answer": "26 weeks"},
    {"question": "How much paternity leave can male employees avail?", "answer": "5 working days"},
    {"question": "When should paternity leave be taken?", "answer": "Within one month of the birth of their child"}
]


@pytest.mark.asyncio
async def test_custom_llm_generation():
    """Test generation using custom LLM"""
    
    # Create patches for the necessary methods
    with patch("app.services.data_source.PDFDataSource.fetch_data", 
               new_callable=AsyncMock, return_value=MOCK_PDF_DATA), \
         patch.object(CustomLLMService, "generate_synthetic_data", 
                     new_callable=AsyncMock, return_value=MOCK_SYNTHETIC_DATA):
        
        # Create a request object from the test payload
        request = SyntheticDataRequest(**TEST_PAYLOAD)
        
        # Test the controller
        response = await SyntheticDataController.generate_synthetic_data(request)
        
        # Assert that the response is the expected type
        assert isinstance(response, SyntheticDataResponse)
        
        # Check that we got the expected number of data points
        assert len(response.data) == 3
        
        # Check the data matches our expected mock data
        for i, item in enumerate(MOCK_SYNTHETIC_DATA):
            assert response.data[i]["question"] == item["question"]
            assert response.data[i]["answer"] == item["answer"]
        
        # Check metadata
        assert response.metadata["source_type"] == "pdf"
        assert response.metadata["llm_type"] == "custom"
        assert response.metadata["dataset_type"] == "qa" 