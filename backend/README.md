# Backend

The backend API for HK Synthetic Data Generator.

## Setup and Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

## Testing

The project includes various tests for different components:

1. **Unit Tests** - Test individual components like LLM services
2. **API Integration Tests** - Test API endpoints and controller interactions
3. **PDF Datasource Tests** - Test PDF data extraction functionality
4. **API Configuration Tests** - Test configuration management APIs

### Running Tests

To run all tests:

```bash
python run_all_tests.py
```

To run specific test types:

```bash
# Run only unit tests
python run_all_tests.py --unit-only

# Run only API tests
python run_all_tests.py --api-only

# Run only PDF datasource tests
python run_all_tests.py --pdf-only

# Run only API configuration tests
python run_all_tests.py --config-only
```

### Using pytest directly

You can also run the tests using pytest directly:

```bash
# Run all tests in the tests directory
pytest -xvs tests/

# Run a specific test file
pytest -xvs tests/test_llm_services.py

# Run with coverage report
pytest -xvs --cov=app tests/
```

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration Management

The API provides endpoints for managing LLM and datasource configurations:

- GET/POST/PUT/DELETE `/api/v1/config/llm` - Manage LLM configurations
- GET/POST/PUT/DELETE `/api/v1/config/datasource` - Manage datasource configurations
- GET/POST/PUT/DELETE `/api/v1/config/saved` - Manage saved generation configurations
- GET `/api/v1/config` - Get all configurations

## Custom LLM Testing

To test the custom LLM integration:

```bash
python -m tests.test_custom_llm --pdf sample_pdfs/your-test-pdf.pdf --api-key your-api-key
```