import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from uuid import UUID

from app.controllers import SyntheticDataController, ConfigController
from app.models import SyntheticDataRequest, SyntheticDataResponse
from app.models.http_models.config import (
    LLMConfigResponse, LLMConfigCreateRequest, LLMConfigUpdateRequest,
    DataSourceConfigResponse, DataSourceConfigCreateRequest, DataSourceConfigUpdateRequest,
    ConfigListResponse, SavedGenerationConfig, SavedGenerationCreateRequest, SavedGenerationUpdateRequest
)


app = FastAPI(
    title="Synthetic Data Generator",
    description="API for generating synthetic datasets using various data sources, LLMs",
    version="1.0.0"
)

@app.exception_handler(Exception)
async def global_exception_handler(request, e: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error" : str(e)}
    )

@app.post(
    "/api/v1/generate",
    response_model=SyntheticDataResponse,
    summary="Generate Synthetic data",
    description="Generate synthetic datasets from configured data sources"
)
async def generate_data(request: SyntheticDataRequest):
    """
    Generate Synthetic Data based on the provided configuration
    :param request: contains data_source, llm config
    :return: generated data and metadata
    """
    try:
        # logger.info(f"Recieved request: {request.dict()}")
        response = await SyntheticDataController.generate_synthetic_data(request)
        # logger.info(f"Successfully generated {request.sample_size} samples")

        # Mark the configurations as used
        await ConfigController.mark_config_as_used(
            # Here we assume the LLM config has an id field, but it doesn't
            # In a real app, you would need to find the config by matching or set IDs
            UUID("00000000-0000-0000-0000-000000000000"),
            UUID("00000000-0000-0000-0000-000000000000")
        )

        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        # logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating data: {str(e)}"
        )

# Configuration Management API Routes
# ----------------------------------------------------------------------------------

# LLM Configuration Routes
@app.get(
    "/api/v1/config/llm",
    response_model=list[LLMConfigResponse],
    summary="Get all LLM configurations",
    description="Returns all saved LLM configurations"
)
async def get_all_llm_configs():
    """Get all LLM configurations"""
    configs = await ConfigController.get_all_configs()
    return configs.llm_configs

@app.get(
    "/api/v1/config/llm/default",
    response_model=LLMConfigResponse,
    summary="Get default LLM configuration",
    description="Returns the default LLM configuration"
)
async def get_default_llm_config():
    """Get the default LLM configuration"""
    config = await ConfigController.get_default_llm_config()
    if not config:
        raise HTTPException(404, "No default LLM configuration found")
    return config

@app.get(
    "/api/v1/config/llm/{config_id}",
    response_model=LLMConfigResponse,
    summary="Get an LLM configuration",
    description="Returns a specific LLM configuration by ID"
)
async def get_llm_config(config_id: UUID):
    """Get an LLM configuration by ID"""
    return await ConfigController.get_llm_config(config_id)

@app.post(
    "/api/v1/config/llm",
    response_model=LLMConfigResponse,
    summary="Create an LLM configuration",
    description="Creates a new LLM configuration"
)
async def create_llm_config(request: LLMConfigCreateRequest):
    """Create a new LLM configuration"""
    return await ConfigController.create_llm_config(
        name=request.name,
        config=request.config,
        is_default=request.is_default
    )

@app.put(
    "/api/v1/config/llm/{config_id}",
    response_model=LLMConfigResponse,
    summary="Update an LLM configuration",
    description="Updates an existing LLM configuration"
)
async def update_llm_config(config_id: UUID, request: LLMConfigUpdateRequest):
    """Update an existing LLM configuration"""
    return await ConfigController.update_llm_config(
        config_id=config_id,
        name=request.name,
        config=request.config,
        is_default=request.is_default
    )

@app.delete(
    "/api/v1/config/llm/{config_id}",
    summary="Delete an LLM configuration",
    description="Deletes an existing LLM configuration"
)
async def delete_llm_config(config_id: UUID):
    """Delete an LLM configuration"""
    await ConfigController.delete_llm_config(config_id)
    return {"status": "success", "message": f"LLM configuration {config_id} deleted"}

# Data Source Configuration Routes
@app.get(
    "/api/v1/config/datasource",
    response_model=list[DataSourceConfigResponse],
    summary="Get all data source configurations",
    description="Returns all saved data source configurations"
)
async def get_all_datasource_configs():
    """Get all data source configurations"""
    configs = await ConfigController.get_all_configs()
    return configs.data_source_configs

@app.get(
    "/api/v1/config/datasource/default",
    response_model=DataSourceConfigResponse,
    summary="Get default data source configuration",
    description="Returns the default data source configuration"
)
async def get_default_datasource_config():
    """Get the default data source configuration"""
    config = await ConfigController.get_default_datasource_config()
    if not config:
        raise HTTPException(404, "No default data source configuration found")
    return config

@app.get(
    "/api/v1/config/datasource/{config_id}",
    response_model=DataSourceConfigResponse,
    summary="Get a data source configuration",
    description="Returns a specific data source configuration by ID"
)
async def get_datasource_config(config_id: UUID):
    """Get a data source configuration by ID"""
    return await ConfigController.get_datasource_config(config_id)

@app.post(
    "/api/v1/config/datasource",
    response_model=DataSourceConfigResponse,
    summary="Create a data source configuration",
    description="Creates a new data source configuration"
)
async def create_datasource_config(request: DataSourceConfigCreateRequest):
    """Create a new data source configuration"""
    return await ConfigController.create_datasource_config(
        name=request.name,
        config=request.config,
        is_default=request.is_default
    )

@app.put(
    "/api/v1/config/datasource/{config_id}",
    response_model=DataSourceConfigResponse,
    summary="Update a data source configuration",
    description="Updates an existing data source configuration"
)
async def update_datasource_config(config_id: UUID, request: DataSourceConfigUpdateRequest):
    """Update an existing data source configuration"""
    return await ConfigController.update_datasource_config(
        config_id=config_id,
        name=request.name,
        config=request.config,
        is_default=request.is_default
    )

@app.delete(
    "/api/v1/config/datasource/{config_id}",
    summary="Delete a data source configuration",
    description="Deletes an existing data source configuration"
)
async def delete_datasource_config(config_id: UUID):
    """Delete a data source configuration"""
    await ConfigController.delete_datasource_config(config_id)
    return {"status": "success", "message": f"Data source configuration {config_id} deleted"}

# Saved Generation Configuration Routes
@app.get(
    "/api/v1/config/saved",
    response_model=list[SavedGenerationConfig],
    summary="Get all saved generation configurations",
    description="Returns all saved generation configurations"
)
async def get_all_saved_generations():
    """Get all saved generation configurations"""
    return await ConfigController.get_all_saved_generations()

@app.get(
    "/api/v1/config/saved/{config_id}",
    response_model=SavedGenerationConfig,
    summary="Get a saved generation configuration",
    description="Returns a specific saved generation configuration by ID"
)
async def get_saved_generation(config_id: UUID):
    """Get a saved generation configuration by ID"""
    return await ConfigController.get_saved_generation(config_id)

@app.post(
    "/api/v1/config/saved",
    response_model=SavedGenerationConfig,
    summary="Create a saved generation configuration",
    description="Creates a new saved generation configuration"
)
async def create_saved_generation(request: SavedGenerationCreateRequest):
    """Create a new saved generation configuration"""
    return await ConfigController.create_saved_generation(
        name=request.name,
        llm_config_id=request.llm_config_id,
        data_source_config_id=request.data_source_config_id,
        dataset_type=request.dataset_type,
        sample_size=request.sample_size
    )

@app.put(
    "/api/v1/config/saved/{config_id}",
    response_model=SavedGenerationConfig,
    summary="Update a saved generation configuration",
    description="Updates an existing saved generation configuration"
)
async def update_saved_generation(config_id: UUID, request: SavedGenerationUpdateRequest):
    """Update an existing saved generation configuration"""
    return await ConfigController.update_saved_generation(
        config_id=config_id,
        name=request.name,
        llm_config_id=request.llm_config_id,
        data_source_config_id=request.data_source_config_id,
        dataset_type=request.dataset_type,
        sample_size=request.sample_size
    )

@app.delete(
    "/api/v1/config/saved/{config_id}",
    summary="Delete a saved generation configuration",
    description="Deletes an existing saved generation configuration"
)
async def delete_saved_generation(config_id: UUID):
    """Delete a saved generation configuration"""
    await ConfigController.delete_saved_generation(config_id)
    return {"status": "success", "message": f"Saved generation configuration {config_id} deleted"}

# Combined Configuration Route
@app.get(
    "/api/v1/config",
    response_model=ConfigListResponse,
    summary="Get all configurations",
    description="Returns all configurations (LLM and data source)"
)
async def get_all_configs():
    """Get all configurations"""
    return await ConfigController.get_all_configs()

@app.get(
    "/health",
    summary="health check",
    description="check if API is running"
)
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

