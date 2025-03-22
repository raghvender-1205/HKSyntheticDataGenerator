import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any

from app.models import DatasetType, LLMConfig, LLMType
from app.services.llm_service import CustomLLMService


class MockResponse:
    def __init__(self, status: int, data: Dict[str, Any]):
        self.status = status
        self._data = data
    
    async def json(self):
        return self._data
    
    async def text(self):
        return json.dumps(self._data)


@pytest.fixture
def custom_llm_config():
    """Fixture for custom LLM configuration"""
    return LLMConfig(
        type=LLMType.CUSTOM,
        api_key="test-api-key",
        model_name="test-model",
        parameters={
            "api_base_url": "http://test-vllm:8000/v1",
            "temperature": 0.7,
            "max_tokens": 500
        }
    )


@pytest.mark.asyncio
async def test_custom_llm_init(custom_llm_config):
    """Test CustomLLMService initialization"""
    service = CustomLLMService(custom_llm_config)
    
    assert service.config.type == LLMType.CUSTOM
    assert service.config.api_key == "test-api-key"
    assert service.config.model_name == "test-model"
    assert service.api_base_url == "http://test-vllm:8000/v1"


@pytest.mark.asyncio
async def test_create_prompt_qa():
    """Test prompt creation for QA dataset type"""
    config = LLMConfig(type=LLMType.CUSTOM, api_key="test", model_name="test")
    service = CustomLLMService(config)
    
    base_data = [{"question": "What is Python?", "answer": "A programming language"}]
    prompt = service._create_prompt(base_data, DatasetType.QA, 3)
    
    assert "Generate 3 synthetic qa examples" in prompt
    assert "Format as question-answer pairs" in prompt


@pytest.mark.asyncio
async def test_format_response_qa():
    """Test response formatting for QA dataset type"""
    config = LLMConfig(type=LLMType.CUSTOM, api_key="test", model_name="test")
    service = CustomLLMService(config)
    
    result = {
        "choices": [
            {"text": "What is FastAPI?\nFastAPI is a modern web framework for building APIs with Python."},
            {"text": "How to install Python?\nYou can download Python from python.org and follow the installation instructions."}
        ]
    }
    
    formatted = service._format_response(result, DatasetType.QA)
    
    assert len(formatted) == 2
    assert formatted[0]["question"] == "What is FastAPI?"
    assert formatted[0]["answer"] == "FastAPI is a modern web framework for building APIs with Python."
    assert formatted[1]["question"] == "How to install Python?"
    assert formatted[1]["answer"] == "You can download Python from python.org and follow the installation instructions."


@pytest.mark.asyncio
async def test_format_response_classification():
    """Test response formatting for classification dataset type"""
    config = LLMConfig(type=LLMType.CUSTOM, api_key="test", model_name="test")
    service = CustomLLMService(config)
    
    result = {
        "choices": [
            {"text": "This product is amazing and works well.\npositive"},
            {"text": "The service was terrible and I want a refund.\nnegative"}
        ]
    }
    
    formatted = service._format_response(result, DatasetType.CLASSIFICATION)
    
    assert len(formatted) == 2
    assert formatted[0]["text"] == "This product is amazing and works well."
    assert formatted[0]["label"] == "positive"
    assert formatted[1]["text"] == "The service was terrible and I want a refund."
    assert formatted[1]["label"] == "negative"


@pytest.mark.asyncio
async def test_generate_synthetic_data():
    """Test the generate_synthetic_data method with mocked HTTP response"""
    config = LLMConfig(type=LLMType.CUSTOM, api_key="test", model_name="test")
    service = CustomLLMService(config)
    
    base_data = [{"text": "Sample data"}]
    
    mock_response = MockResponse(200, {
        "choices": [
            {"text": "What is Python?\nPython is a programming language."},
            {"text": "How to learn FastAPI?\nRead the documentation at fastapi.tiangolo.com."}
        ]
    })
    
    # Mock the aiohttp.ClientSession context manager
    session_mock = MagicMock()
    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    session_mock.post.return_value.__aenter__.return_value = mock_response
    
    with patch("aiohttp.ClientSession", return_value=session_mock):
        result = await service.generate_synthetic_data(base_data, 2, DatasetType.QA)
    
    # Verify the results
    assert len(result) == 2
    assert result[0]["question"] == "What is Python?"
    assert result[0]["answer"] == "Python is a programming language."
    assert result[1]["question"] == "How to learn FastAPI?"
    assert result[1]["answer"] == "Read the documentation at fastapi.tiangolo.com."
    
    # Verify the API was called with the right parameters
    post_call_args = session_mock.post.call_args
    assert post_call_args[0][0].endswith("/completions")


@pytest.mark.asyncio
async def test_generate_synthetic_data_error_handling():
    """Test error handling in generate_synthetic_data method"""
    config = LLMConfig(type=LLMType.CUSTOM, api_key="test", model_name="test")
    service = CustomLLMService(config)
    
    base_data = [{"text": "Sample data"}]
    
    mock_response = MockResponse(400, {"error": "Bad request"})
    
    # Mock the aiohttp.ClientSession context manager
    session_mock = MagicMock()
    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    session_mock.post.return_value.__aenter__.return_value = mock_response
    
    with patch("aiohttp.ClientSession", return_value=session_mock):
        with pytest.raises(Exception) as excinfo:
            await service.generate_synthetic_data(base_data, 2, DatasetType.QA)
    
    assert "vLLM API error: 400" in str(excinfo.value) 