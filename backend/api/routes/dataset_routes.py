from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from core.service import SyntheticDataService
from core.dataset_generator import DatasetGeneratorConfig, Dataset
from api.dependencies import get_service

router = APIRouter(
    prefix="/datasets",
    tags=["datasets"],
    responses={404: {"description": "Not found"}},
)

@router.get("/generators", response_model=Dict[str, Dict[str, Any]])
async def get_dataset_generators(service: SyntheticDataService = Depends(get_service)):
    """
    Get all available dataset generator plugins.
    """
    plugins = service.get_dataset_generator_plugins()
    result = {}
    
    for plugin_id, plugin_class in plugins.items():
        result[plugin_id] = {
            "id": plugin_id,
            "config_schema": plugin_class.get_config_schema()
        }
    
    return result

@router.get("/generators/{plugin_id}", response_model=Dict[str, Any])
async def get_dataset_generator(
    plugin_id: str, 
    service: SyntheticDataService = Depends(get_service)
):
    """
    Get information about a specific dataset generator plugin.
    """
    try:
        plugin_class = service.get_dataset_generator_plugin(plugin_id)
        return {
            "id": plugin_id,
            "config_schema": plugin_class.get_config_schema()
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Dataset generator plugin {plugin_id} not found")

@router.post("/generators/create", response_model=Dict[str, Any])
async def create_dataset_generator(
    config: DatasetGeneratorConfig, 
    service: SyntheticDataService = Depends(get_service)
):
    """
    Create a dataset generator instance.
    """
    try:
        generator = await service.create_dataset_generator(config)
        return {"status": "success", "generator_id": config.generator_id}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Dataset generator plugin {config.generator_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generators/{generator_id}/info", response_model=Dict[str, Any])
async def get_dataset_generator_info(
    generator_id: str, 
    service: SyntheticDataService = Depends(get_service)
):
    """
    Get information about a dataset generator instance.
    """
    try:
        if generator_id not in service.dataset_generator_instances:
            raise KeyError(f"Dataset generator {generator_id} not initialized")
        
        return await service.dataset_generator_instances[generator_id].get_info()
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Dataset generator {generator_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GenerateDatasetRequest(BaseModel):
    datasource_id: str
    llm_id: str
    options: Dict[str, Any] = {}

@router.post("/generators/{generator_id}/generate", response_model=Dict[str, Any])
async def generate_dataset(
    generator_id: str,
    request: GenerateDatasetRequest,
    service: SyntheticDataService = Depends(get_service)
):
    """
    Generate a dataset using a dataset generator.
    """
    try:
        dataset = await service.generate_dataset(
            generator_id,
            request.datasource_id,
            request.llm_id,
            **request.options
        )
        
        return dataset.dict()
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 