import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.controllers import SyntheticDataController
from app.models import SyntheticDataRequest, SyntheticDataResponse


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

        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        # logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating data: {str(e)}"
        )

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

