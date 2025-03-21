from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from core.service import SyntheticDataService
from core.llm import LLMConfig, LLMResponse
from api.dependencies import get_service

router = APIRouter(
    prefix="/llms",
    tags=["llms"],
    responses={404: {"description": "Not found"}},
)

@router.get("/plugins", response_model=Dict[str, Dict[str, Any]])
async def get_llm_plugins(service: SyntheticDataService = Depends(get_service)):
    """
    Get all available LLM plugins.
    """
    plugins = service.get_llm_plugins()
    result = {}
    
    for plugin_id, plugin_class in plugins.items():
        result[plugin_id] = {
            "id": plugin_id,
            "config_schema": plugin_class.get_config_schema()
        }
    
    return result

@router.get("/plugins/{plugin_id}", response_model=Dict[str, Any])
async def get_llm_plugin(
    plugin_id: str, 
    service: SyntheticDataService = Depends(get_service)
):
    """
    Get information about a specific LLM plugin.
    """
    try:
        plugin_class = service.get_llm_plugin(plugin_id)
        return {
            "id": plugin_id,
            "config_schema": plugin_class.get_config_schema()
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"LLM plugin {plugin_id} not found")

@router.post("/create", response_model=Dict[str, Any])
async def create_llm(
    config: LLMConfig, 
    service: SyntheticDataService = Depends(get_service)
):
    """
    Create an LLM instance.
    """
    try:
        llm = await service.create_llm(config)
        return {"status": "success", "llm_id": config.model_id}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"LLM plugin {config.model_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{llm_id}/info", response_model=Dict[str, Any])
async def get_llm_info(
    llm_id: str, 
    service: SyntheticDataService = Depends(get_service)
):
    """
    Get information about an LLM instance.
    """
    try:
        if llm_id not in service.llm_instances:
            raise KeyError(f"LLM {llm_id} not initialized")
        
        return await service.llm_instances[llm_id].get_info()
    except KeyError:
        raise HTTPException(status_code=404, detail=f"LLM {llm_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GenerateRequest(BaseModel):
    prompt: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

@router.post("/{llm_id}/generate", response_model=Dict[str, Any])
async def generate_text(
    llm_id: str,
    request: GenerateRequest,
    service: SyntheticDataService = Depends(get_service)
):
    """
    Generate text using an LLM.
    """
    try:
        if llm_id not in service.llm_instances:
            raise KeyError(f"LLM {llm_id} not initialized")
        
        kwargs = {}
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        
        response = await service.llm_instances[llm_id].generate(
            request.prompt, 
            **kwargs
        )
        
        return response.dict()
    except KeyError:
        raise HTTPException(status_code=404, detail=f"LLM {llm_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
class BatchGenerateRequest(BaseModel):
    prompts: List[str]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

@router.post("/{llm_id}/generate_batch", response_model=List[Dict[str, Any]])
async def generate_batch(
    llm_id: str,
    request: BatchGenerateRequest,
    service: SyntheticDataService = Depends(get_service)
):
    """
    Generate text for multiple prompts using an LLM.
    """
    try:
        if llm_id not in service.llm_instances:
            raise KeyError(f"LLM {llm_id} not initialized")
        
        kwargs = {}
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        
        responses = await service.llm_instances[llm_id].generate_batch(
            request.prompts, 
            **kwargs
        )
        
        return [response.dict() for response in responses]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"LLM {llm_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 