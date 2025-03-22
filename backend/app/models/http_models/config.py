from pydantic import BaseModel
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4

from app.models import LLMConfig, LLMType, DataSourceConfig


class LLMConfigResponse(BaseModel):
    """Response model for LLM configurations"""
    id: UUID
    name: str
    config: LLMConfig
    is_default: bool = False
    created_at: str
    last_used_at: Optional[str] = None


class LLMConfigCreateRequest(BaseModel):
    """Request model for creating a new LLM configuration"""
    name: str
    config: LLMConfig
    is_default: bool = False


class LLMConfigUpdateRequest(BaseModel):
    """Request model for updating an existing LLM configuration"""
    name: Optional[str] = None
    config: Optional[LLMConfig] = None
    is_default: Optional[bool] = None


class DataSourceConfigResponse(BaseModel):
    """Response model for data source configurations"""
    id: UUID
    name: str
    config: DataSourceConfig
    is_default: bool = False
    created_at: str
    last_used_at: Optional[str] = None


class DataSourceConfigCreateRequest(BaseModel):
    """Request model for creating a new data source configuration"""
    name: str
    config: DataSourceConfig
    is_default: bool = False


class DataSourceConfigUpdateRequest(BaseModel):
    """Request model for updating an existing data source configuration"""
    name: Optional[str] = None
    config: Optional[DataSourceConfig] = None
    is_default: Optional[bool] = None


class ConfigListResponse(BaseModel):
    """Response model for listing all configurations"""
    llm_configs: List[LLMConfigResponse]
    data_source_configs: List[DataSourceConfigResponse] 