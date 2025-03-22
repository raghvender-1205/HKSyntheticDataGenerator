import pytest
from fastapi.testclient import TestClient
import json
import os
from unittest.mock import patch, MagicMock, AsyncMock

from app.main import app
from app.models import DatasetType, LLMType, DataSourceType

client = TestClient(app)

# Mock synthetic data for testing
MOCK_SYNTHETIC_DATA = [
    {"question": "What is the duration of maternity leave?", "answer": "26 weeks"},
    {"question": "How much paternity leave can male employees avail?", "answer": "5 working days"},
    {"question": "When should paternity leave be taken?", "answer": "Within one month of the birth of their child"}
]

# Test payload to use for integration tests
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
        "api_key": "test-key",
        "model_name": "hkllm",
        "parameters": {
            "api_base_url": "https://apillm.healthkart.com/v1",
            "temperature": "0.7",
            "max_tokens": "1000"
        }
    },
    "sample_size": 3,
    "output_format": "json"
}


@pytest.fixture
def mock_pdf_data():
    """Mock PDF data source using content similar to sample_pdfs/doc.pdf"""
    return [
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


@pytest.fixture
def mock_services(mock_pdf_data):
    """Mock all the necessary services for integration testing"""
    # Create a properly mocked async fetch_data method
    async def mock_fetch_data(*args, **kwargs):
        return mock_pdf_data
    
    # Create a properly mocked async generate_synthetic_data method
    async def mock_generate_synthetic_data(*args, **kwargs):
        return MOCK_SYNTHETIC_DATA
    
    # Create mock for PDFDataSource
    pdf_datasource = MagicMock()
    pdf_datasource.return_value.fetch_data = AsyncMock(side_effect=mock_fetch_data)
    
    # Create mock for CustomLLMService
    custom_llm = MagicMock()
    custom_llm.return_value.generate_synthetic_data = AsyncMock(side_effect=mock_generate_synthetic_data)
    
    with patch("app.controllers.synthetic_data.PDFDataSource", pdf_datasource), \
         patch("app.controllers.synthetic_data.CustomLLMService", custom_llm):
        yield {
            "pdf_datasource": pdf_datasource,
            "custom_llm": custom_llm
        }


def test_generate_endpoint(mock_services):
    """Test the /api/v1/generate endpoint"""
    # Make request to the API
    response = client.post("/api/v1/generate", json=TEST_PAYLOAD)
    
    # Print the response details for debugging
    print(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        print(f"Response details: {response.json()}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "data" in data
    assert "metadata" in data
    assert "generated_str" in data
    
    # Check if the data matches our mock data
    assert data["data"] == MOCK_SYNTHETIC_DATA
    assert len(data["data"]) == 3
    
    # Verify the metadata
    assert data["metadata"]["source_type"] == DataSourceType.PDF
    assert data["metadata"]["llm_type"] == LLMType.CUSTOM
    assert data["metadata"]["dataset_type"] == DatasetType.QA
    
    # Verify that our mocks were called correctly
    pdf_mock = mock_services["pdf_datasource"]
    llm_mock = mock_services["custom_llm"]
    
    # Check if PDFDataSource was initialized
    pdf_mock.assert_called_once()
    
    # Check if the fetch_data method was called
    assert pdf_mock.return_value.fetch_data.called
    
    # Check if CustomLLMService was initialized
    llm_mock.assert_called_once()
    
    # Check if the generate_synthetic_data method was called
    assert llm_mock.return_value.generate_synthetic_data.called


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_error_handling():
    """Test error handling for invalid input"""
    # Bad request with invalid dataset type
    bad_payload = TEST_PAYLOAD.copy()
    bad_payload["dataset_type"] = "invalid_type"
    
    response = client.post("/api/v1/generate", json=bad_payload)
    assert response.status_code == 422  # Validation error


def test_unsupported_datasource():
    """Test error handling for unsupported data source type"""
    # Create patch that raises an HTTPException
    with patch("app.controllers.synthetic_data.SyntheticDataController.generate_synthetic_data") as mock_generate:
        mock_generate.side_effect = Exception("Unsupported data source type")
        
        response = client.post("/api/v1/generate", json=TEST_PAYLOAD)
        assert response.status_code == 500
        assert "Unsupported data source type" in response.json()["detail"] 