# Synthetic Data Generator Backend

A configurable FastAPI-based backend for generating LLM datasets for specific use cases.

## Features

- **Plugin Architecture**: Easily extend with new data sources, LLM providers, and dataset generators
- **Multiple LLM Support**: Works with OpenAI, Ollama, Groq, and Google Gemini models
- **Configurable Data Sources**: Load documents from files, URLs, and other sources
- **Flexible Dataset Generation**: Create QA pairs, instruction-response pairs, and more
- **REST API**: Simple and well-documented API for frontend integration

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in the API keys for the LLM providers you plan to use

4. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

5. Access the API documentation at `http://localhost:8000/docs`

## Architecture

The system is built around a plugin architecture with these core components:

1. **Data Sources**: Plugin classes that implement the `DataSource` interface for loading documents from various sources
   - File-based sources (text, JSON, CSV)
   - URL-based sources (coming soon)
   - Database sources (coming soon)

2. **LLM Providers**: Plugin classes that implement the `LLMProvider` interface for generating text
   - OpenAI API (with custom endpoint support)
   - Ollama (local LLM server)
   - Groq API
   - Google Gemini API

3. **Dataset Generators**: Plugin classes that implement the `DatasetGenerator` interface for creating datasets
   - QA pair generator
   - Instruction-response generator (via QA format)

## API Endpoints

- `/datasources/*`: Endpoints for managing data sources
- `/llms/*`: Endpoints for managing LLM providers
- `/datasets/*`: Endpoints for managing and generating datasets

## Creating Plugins

To add a new plugin, follow these steps:

1. Create a new Python file in the appropriate plugins directory:
   - `plugins/datasources/` for data sources
   - `plugins/llms/` for LLM providers
   - `plugins/dataset_generators/` for dataset generators

2. Implement the required base class and methods
3. The system will automatically discover and register your plugin

See existing plugins for examples of implementation patterns. 