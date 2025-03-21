from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

from core.service import SyntheticDataService
from core.datasource import DataSourceConfig, Document
from api.dependencies import get_service

router = APIRouter(
    prefix="/datasources",
    tags=["datasources"],
    responses={404: {"description": "Not found"}},
)

@router.get("/plugins", response_model=Dict[str, Dict[str, Any]])
async def get_datasource_plugins(service: SyntheticDataService = Depends(get_service)):
    """
    Get all available datasource plugins.
    """
    plugins = service.get_datasource_plugins()
    result = {}
    
    for plugin_id, plugin_class in plugins.items():
        result[plugin_id] = {
            "id": plugin_id,
            "config_schema": plugin_class.get_config_schema()
        }
    
    return result

@router.get("/plugins/{plugin_id}", response_model=Dict[str, Any])
async def get_datasource_plugin(
    plugin_id: str, 
    service: SyntheticDataService = Depends(get_service)
):
    """
    Get information about a specific datasource plugin.
    """
    try:
        plugin_class = service.get_datasource_plugin(plugin_id)
        return {
            "id": plugin_id,
            "config_schema": plugin_class.get_config_schema()
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Datasource plugin {plugin_id} not found")

@router.post("/create", response_model=Dict[str, Any])
async def create_datasource(
    config: DataSourceConfig, 
    service: SyntheticDataService = Depends(get_service)
):
    """
    Create a datasource instance.
    """
    try:
        datasource = await service.create_datasource(config)
        return {"status": "success", "datasource_id": config.source_id}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Datasource plugin {config.source_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{datasource_id}/info", response_model=Dict[str, Any])
async def get_datasource_info(
    datasource_id: str, 
    service: SyntheticDataService = Depends(get_service)
):
    """
    Get information about a datasource instance.
    """
    try:
        if datasource_id not in service.datasource_instances:
            raise KeyError(f"Datasource {datasource_id} not initialized")
        
        return await service.datasource_instances[datasource_id].get_info()
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Datasource {datasource_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{datasource_id}/load", response_model=List[Dict[str, Any]])
async def load_documents(
    datasource_id: str, 
    service: SyntheticDataService = Depends(get_service)
):
    """
    Load documents from a datasource.
    """
    try:
        documents = await service.load_documents(datasource_id)
        return [doc.dict() for doc in documents]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Datasource {datasource_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 