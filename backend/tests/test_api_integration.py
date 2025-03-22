import pytest
from fastapi.testclient import TestClient
import json
import os
from unittest.mock import patch, MagicMock

from app.main import app
from app.models import DatasetType, LLMType, DataSourceType

client = TestClient(app)

# Mock synthetic data for testing
MOCK_SYNTHETIC_DATA = [
    {"question": "What is synthetic data?", "answer": "Data artificially generated rather than collected from real-world events."}
]

# Test payload to use for integration tests
TEST_PAYLOAD = {
    "dataset_type": "qa",
    "data_source": {
        "type": "pdf",
        "connection_string": "test.pdf",
        "parameters": {
            "extract_metadata": True,
            "extract_layout": True
        }
    },
    "llm_config": {
        "type": "custom",
        "api_key": "test-key",
        "model_name": "hkllm",
        "parameters": {
            "api_base_url": "https://apillm.healthkart.com/v1",
            "temperature": 0.7,
            "max_tokens": 1000
        }
    },
    "sample_size": 1,
    "output_format": "json"
}


@pytest.fixture
def mock_pdf_data():
    """Mock PDF data source"""
    return [
        {
            "page_number": 1,
            "content": "This is a test PDF document about synthetic data generation.",
            "source": "test.pdf",
            "metadata": {
                "page_width": 8.5,
                "page_height": 11.0,
                "layout": {
                    "text_blocks": [
                        {
                            "text": "This is a test PDF document about synthetic data generation.",
                            "bbox": [72, 72, 540, 100]
                        },
                        {
                            "text": "The document explains how to generate synthetic data.",
                            "bbox": [72, 120, 540, 150]
                        }
                    ],
                    "tables": [
                        [
                            ["Header 1", "Header 2"],
                            ["Value 1", "Value 2"],
                            ["Value 3", "Value 4"]
                        ]
                    ],
                    "figures": []
                }
            }
        }
    ]


@pytest.fixture
def mock_services():
    """Mock all the necessary services for integration testing"""
    # Create mock for PDFDataSource
    pdf_datasource = MagicMock()
    pdf_datasource.return_value.fetch_data.return_value = mock_pdf_data()
    
    # Create mock for CustomLLMService
    custom_llm = MagicMock()
    custom_llm.return_value.generate_synthetic_data.return_value = MOCK_SYNTHETIC_DATA
    
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
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "data" in data
    assert "metadata" in data
    assert "generated_str" in data
    
    # Check if the data matches our mock data
    assert data["data"] == MOCK_SYNTHETIC_DATA
    
    # Verify the metadata
    assert data["metadata"]["source_type"] == DataSourceType.PDF
    assert data["metadata"]["llm_type"] == LLMType.CUSTOM
    assert data["metadata"]["dataset_type"] == DatasetType.QA
    
    # Verify that our mocks were called correctly
    pdf_mock = mock_services["pdf_datasource"]
    llm_mock = mock_services["custom_llm"]
    
    # Check if PDFDataSource was initialized with the right config
    pdf_mock.assert_called_once()
    pdf_mock.return_value.fetch_data.assert_called_once()
    
    # Check if CustomLLMService was initialized with the right config
    llm_mock.assert_called_once()
    llm_mock.return_value.generate_synthetic_data.assert_called_once()


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