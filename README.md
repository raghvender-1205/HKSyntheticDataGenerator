# HealthKart Synthetic Data Generator

A powerful tool for generating high-quality synthetic data from PDF documents and text sources using advanced Large Language Models. This application allows you to extract information from documents and generate various types of synthetic data like question-answer pairs, instruction-response pairs, and conversations.

## Project Structure

This project consists of two main components:

- **Backend**: FastAPI-based Python backend that handles:
  - PDF document processing
  - Integration with various LLMs (OpenAI, Anthropic, and custom LLMs)
  - Synthetic data generation
  - Configuration management

- **Frontend**: Svelte-based web application that provides:
  - User-friendly interface for data generation
  - Multi-step configuration process
  - Management of saved configurations
  - Settings for API keys and defaults

## Features

- 📄 **PDF Data Extraction**: Extract and process text from PDF documents
- 🤖 **Multiple LLM Support**: Integrate with OpenAI (GPT models), Anthropic (Claude), and custom LLM endpoints
- 🔄 **Various Data Formats**: Generate Q&A pairs, instruction-response pairs, and conversations
- 💾 **Configuration Management**: Save, load, and reuse generation configurations
- 🔑 **API Key Management**: Securely store and manage API keys for different providers
- 📊 **Customizable Parameters**: Control temperature, tokens, and other generation parameters

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- pip
- npm

### Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```

### Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

## Usage

1. **Upload a document**: Start by uploading a PDF or entering text
2. **Configure output**: Choose data format and set the number of samples
3. **Configure LLM**: Select your preferred LLM and set parameters
4. **Generate data**: Create your synthetic dataset
5. **Save or export**: Save your configuration or download the generated data

## API Documentation

The backend provides a RESTful API with the following main endpoints:

- `/api/generate`: Generate synthetic data
- `/api/configurations`: Manage saved configurations
- `/api/settings`: Manage application settings

For detailed API documentation, visit `/docs` when the backend server is running.

## Development

### Backend

The backend is built with FastAPI and follows a modular architecture:

- `controllers/`: API endpoints
- `services/`: Business logic
- `models/`: Data models
- `datasources/`: Data extraction logic
- `tests/`: Test suite

### Frontend

The frontend is built with Svelte and SvelteKit:

- `src/routes/`: Application pages
- `src/lib/components/`: Reusable UI components
- `static/`: Static assets

## Testing

```bash
# Run backend tests
cd backend
python run_all_tests.py

# Run frontend tests
cd frontend
npm test
```

## License

[MIT License](LICENSE)

## Acknowledgements

- OpenAI for GPT models
- Anthropic for Claude models
- PDFBox for PDF processing