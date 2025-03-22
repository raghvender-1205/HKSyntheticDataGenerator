import logging
from datetime import datetime
import os
import shutil
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from uuid import UUID
import json

from app.controllers import SyntheticDataController, ConfigController
from app.schemas import (
    LLMConfig, LLMConfigCreate, LLMConfigUpdate,
    DataSourceConfig, DataSourceConfigCreate, DataSourceConfigUpdate,
    SavedGeneration, SavedGenerationCreate, SavedGenerationUpdate,
    GenerationRequest, GenerationResponse,
    SyntheticDataRequest, SyntheticDataResponse, DatasetType
)
from app.database import (
    LLMConfigRepository, DataSourceConfigRepository, SavedGenerationRepository,
    get_llm_config_repository, get_datasource_config_repository, get_saved_generation_repository,
    SettingsRepository, get_settings_repository
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
async def generate_data(
    request: SyntheticDataRequest,
    llm_repo: LLMConfigRepository = Depends(get_llm_config_repository),
    datasource_repo: DataSourceConfigRepository = Depends(get_datasource_config_repository),
    saved_repo: SavedGenerationRepository = Depends(get_saved_generation_repository)
):
    """
    Generate Synthetic Data based on the provided configuration
    :param request: contains data_source, llm config
    :return: generated data and metadata
    """
    try:
        # logger.info(f"Recieved request: {request.dict()}")
        response = await SyntheticDataController.generate_synthetic_data(
            request, llm_repo, datasource_repo, saved_repo
        )
        # logger.info(f"Successfully generated {request.sample_size} samples")

        # Mark the configurations as used if IDs are provided
        if request.llm_config_id and request.datasource_config_id:
            await ConfigController.mark_config_as_used(
                request.llm_config_id,
                request.datasource_config_id,
                llm_repo,
                datasource_repo
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

@app.post(
    "/api/v1/upload/pdf",
    response_model=dict,
    summary="Upload PDF file",
    description="Upload a PDF file to be used for data generation"
)
async def upload_pdf(
    file: UploadFile = File(...),
    datasource_name: str = Form("uploaded_pdf"),
):
    """
    Upload a PDF file to the server for processing
    """
    try:
        # Create the uploads directory if it doesn't exist
        os.makedirs("data/uploads", exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join("data/uploads", file.filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "filename": file.filename,
            "path": file_path,
            "success": True,
            "message": f"File {file.filename} uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )

@app.post(
    "/api/v1/generate/upload",
    response_model=SyntheticDataResponse,
    summary="Generate synthetic data with file upload",
    description="Upload a file and generate synthetic data in one request"
)
async def generate_with_upload(
    file: UploadFile = File(...),
    payload: str = Form(...),
    llm_repo: LLMConfigRepository = Depends(get_llm_config_repository),
    datasource_repo: DataSourceConfigRepository = Depends(get_datasource_config_repository),
    saved_repo: SavedGenerationRepository = Depends(get_saved_generation_repository)
):
    """
    Upload a file and generate synthetic data in one request
    """
    try:
        # Parse the JSON payload
        request_data = json.loads(payload)
        
        # Create the uploads directory if it doesn't exist
        os.makedirs("data/uploads", exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join("data/uploads", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Ensure datasource_config is properly formatted
        if "datasource_config" not in request_data:
            request_data["datasource_config"] = {}
            
        # Make sure source_path is at the top level of the datasource_config
        request_data["datasource_config"]["source_path"] = "data/uploads"
        request_data["datasource_config"]["type"] = "pdf"
        
        # Ensure connection_string is present (required by PDFDataSource)
        if "connection_string" not in request_data["datasource_config"]:
            request_data["datasource_config"]["connection_string"] = ""
            
        # Ensure parameters are present
        if "parameters" not in request_data["datasource_config"]:
            request_data["datasource_config"]["parameters"] = {
                "extract_metadata": "true",
                "extract_layout": "true"
            }
        
        # Create the request object
        request = SyntheticDataRequest(**request_data)
        
        # Generate synthetic data
        response = await SyntheticDataController.generate_synthetic_data(
            request, llm_repo, datasource_repo, saved_repo
        )
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating data: {str(e)}"
        )

# Configuration Management API Routes
# ----------------------------------------------------------------------------------

# LLM Configuration Routes
@app.get(
    "/api/v1/config/llm",
    response_model=list[LLMConfig],
    summary="Get all LLM configurations",
    description="Returns all saved LLM configurations"
)
async def get_all_llm_configs(
    llm_repo: LLMConfigRepository = Depends(get_llm_config_repository),
    datasource_repo: DataSourceConfigRepository = Depends(get_datasource_config_repository)
):
    """Get all LLM configurations"""
    configs = await ConfigController.get_all_configs(llm_repo, datasource_repo)
    return configs["llm_configs"]

@app.get(
    "/api/v1/config/llm/default",
    response_model=LLMConfig,
    summary="Get default LLM configuration",
    description="Returns the default LLM configuration"
)
async def get_default_llm_config(
    llm_repo: LLMConfigRepository = Depends(get_llm_config_repository)
):
    """Get the default LLM configuration"""
    config = await ConfigController.get_default_llm_config(llm_repo)
    if not config:
        raise HTTPException(404, "No default LLM configuration found")
    return config

@app.get(
    "/api/v1/config/llm/{config_id}",
    response_model=LLMConfig,
    summary="Get an LLM configuration",
    description="Returns a specific LLM configuration by ID"
)
async def get_llm_config(
    config_id: UUID,
    llm_repo: LLMConfigRepository = Depends(get_llm_config_repository)
):
    """Get an LLM configuration by ID"""
    return await ConfigController.get_llm_config(config_id, llm_repo)

@app.post(
    "/api/v1/config/llm",
    response_model=LLMConfig,
    summary="Create an LLM configuration",
    description="Creates a new LLM configuration"
)
async def create_llm_config(
    request: LLMConfigCreate,
    llm_repo: LLMConfigRepository = Depends(get_llm_config_repository)
):
    """Create a new LLM configuration"""
    return await ConfigController.create_llm_config(request, llm_repo)

@app.put(
    "/api/v1/config/llm/{config_id}",
    response_model=LLMConfig,
    summary="Update an LLM configuration",
    description="Updates an existing LLM configuration"
)
async def update_llm_config(
    config_id: UUID, 
    request: LLMConfigUpdate,
    llm_repo: LLMConfigRepository = Depends(get_llm_config_repository)
):
    """Update an existing LLM configuration"""
    return await ConfigController.update_llm_config(config_id, request, llm_repo)

@app.delete(
    "/api/v1/config/llm/{config_id}",
    summary="Delete an LLM configuration",
    description="Deletes an existing LLM configuration"
)
async def delete_llm_config(
    config_id: UUID,
    llm_repo: LLMConfigRepository = Depends(get_llm_config_repository)
):
    """Delete an LLM configuration"""
    await ConfigController.delete_llm_config(config_id, llm_repo)
    return {"status": "success", "message": f"LLM configuration {config_id} deleted"}

# Data Source Configuration Routes
@app.get(
    "/api/v1/config/datasource",
    response_model=list[DataSourceConfig],
    summary="Get all data source configurations",
    description="Returns all saved data source configurations"
)
async def get_all_datasource_configs(
    llm_repo: LLMConfigRepository = Depends(get_llm_config_repository),
    datasource_repo: DataSourceConfigRepository = Depends(get_datasource_config_repository)
):
    """Get all data source configurations"""
    configs = await ConfigController.get_all_configs(llm_repo, datasource_repo)
    return configs["data_source_configs"]

@app.get(
    "/api/v1/config/datasource/default",
    response_model=DataSourceConfig,
    summary="Get default data source configuration",
    description="Returns the default data source configuration"
)
async def get_default_datasource_config(
    datasource_repo: DataSourceConfigRepository = Depends(get_datasource_config_repository)
):
    """Get the default data source configuration"""
    config = await ConfigController.get_default_datasource_config(datasource_repo)
    if not config:
        raise HTTPException(404, "No default data source configuration found")
    return config

@app.get(
    "/api/v1/config/datasource/{config_id}",
    response_model=DataSourceConfig,
    summary="Get a data source configuration",
    description="Returns a specific data source configuration by ID"
)
async def get_datasource_config(
    config_id: UUID,
    datasource_repo: DataSourceConfigRepository = Depends(get_datasource_config_repository)
):
    """Get a data source configuration by ID"""
    return await ConfigController.get_datasource_config(config_id, datasource_repo)

@app.post(
    "/api/v1/config/datasource",
    response_model=DataSourceConfig,
    summary="Create a data source configuration",
    description="Creates a new data source configuration"
)
async def create_datasource_config(
    request: DataSourceConfigCreate,
    datasource_repo: DataSourceConfigRepository = Depends(get_datasource_config_repository)
):
    """Create a new data source configuration"""
    return await ConfigController.create_datasource_config(request, datasource_repo)

@app.put(
    "/api/v1/config/datasource/{config_id}",
    response_model=DataSourceConfig,
    summary="Update a data source configuration",
    description="Updates an existing data source configuration"
)
async def update_datasource_config(
    config_id: UUID, 
    request: DataSourceConfigUpdate,
    datasource_repo: DataSourceConfigRepository = Depends(get_datasource_config_repository)
):
    """Update an existing data source configuration"""
    return await ConfigController.update_datasource_config(config_id, request, datasource_repo)

@app.delete(
    "/api/v1/config/datasource/{config_id}",
    summary="Delete a data source configuration",
    description="Deletes an existing data source configuration"
)
async def delete_datasource_config(
    config_id: UUID,
    datasource_repo: DataSourceConfigRepository = Depends(get_datasource_config_repository)
):
    """Delete a data source configuration"""
    await ConfigController.delete_datasource_config(config_id, datasource_repo)
    return {"status": "success", "message": f"Data source configuration {config_id} deleted"}

# Saved Generation Configuration Routes
@app.get(
    "/api/v1/config/saved",
    response_model=list[SavedGeneration],
    summary="Get all saved generation configurations",
    description="Returns all saved generation configurations"
)
async def get_all_saved_generations(
    saved_repo: SavedGenerationRepository = Depends(get_saved_generation_repository)
):
    """Get all saved generation configurations"""
    return await ConfigController.get_all_saved_generations(saved_repo)

@app.get(
    "/api/v1/config/saved/{config_id}",
    response_model=SavedGeneration,
    summary="Get a saved generation configuration",
    description="Returns a specific saved generation configuration by ID"
)
async def get_saved_generation(
    config_id: UUID,
    saved_repo: SavedGenerationRepository = Depends(get_saved_generation_repository)
):
    """Get a saved generation configuration by ID"""
    return await ConfigController.get_saved_generation(config_id, saved_repo)

@app.post(
    "/api/v1/config/saved",
    response_model=SavedGeneration,
    summary="Create a saved generation configuration",
    description="Creates a new saved generation configuration"
)
async def create_saved_generation(
    request: SavedGenerationCreate,
    saved_repo: SavedGenerationRepository = Depends(get_saved_generation_repository),
    llm_repo: LLMConfigRepository = Depends(get_llm_config_repository),
    datasource_repo: DataSourceConfigRepository = Depends(get_datasource_config_repository)
):
    """Create a new saved generation configuration"""
    return await ConfigController.create_saved_generation(request, saved_repo, llm_repo, datasource_repo)

@app.put(
    "/api/v1/config/saved/{config_id}",
    response_model=SavedGeneration,
    summary="Update a saved generation configuration",
    description="Updates an existing saved generation configuration"
)
async def update_saved_generation(
    config_id: UUID, 
    request: SavedGenerationUpdate,
    saved_repo: SavedGenerationRepository = Depends(get_saved_generation_repository)
):
    """Update an existing saved generation configuration"""
    return await ConfigController.update_saved_generation(config_id, request, saved_repo)

@app.delete(
    "/api/v1/config/saved/{config_id}",
    summary="Delete a saved generation configuration",
    description="Deletes an existing saved generation configuration"
)
async def delete_saved_generation(
    config_id: UUID,
    saved_repo: SavedGenerationRepository = Depends(get_saved_generation_repository)
):
    """Delete a saved generation configuration"""
    await ConfigController.delete_saved_generation(config_id, saved_repo)
    return {"status": "success", "message": f"Saved generation configuration {config_id} deleted"}

# Combined Configuration Route
@app.get(
    "/api/v1/config",
    summary="Get all configurations",
    description="Returns all configurations (LLM and data source)"
)
async def get_all_configs(
    llm_repo: LLMConfigRepository = Depends(get_llm_config_repository),
    datasource_repo: DataSourceConfigRepository = Depends(get_datasource_config_repository)
):
    """Get all configurations"""
    return await ConfigController.get_all_configs(llm_repo, datasource_repo)

# Application Settings
@app.get(
    "/api/v1/config/settings",
    response_model=dict,
    summary="Get application settings",
    description="Returns all application settings"
)
async def get_settings(
    settings_repo: SettingsRepository = Depends(get_settings_repository)
):
    """Get all application settings"""
    settings = await ConfigController.get_all_settings(settings_repo)
    return settings

@app.post(
    "/api/v1/config/settings",
    response_model=dict,
    summary="Update application settings",
    description="Updates application settings"
)
async def update_settings(
    settings: dict,
    settings_repo: SettingsRepository = Depends(get_settings_repository)
):
    """Update application settings"""
    updated_settings = await ConfigController.update_settings(settings, settings_repo)
    return updated_settings

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

