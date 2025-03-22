from pydantic import BaseModel
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4

from app.models import LLMConfig, LLMType, DataSourceConfig, DatasetType


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


class SavedGenerationConfig(BaseModel):
    """Model for a saved generation configuration"""
    id: UUID
    name: str
    llm_config_id: UUID
    data_source_config_id: UUID
    dataset_type: DatasetType
    sample_size: int
    created_at: str
    last_used_at: Optional[str] = None


class SavedGenerationCreateRequest(BaseModel):
    """Request model for creating a saved generation configuration"""
    name: str
    llm_config_id: UUID
    data_source_config_id: UUID
    dataset_type: DatasetType
    sample_size: int


class SavedGenerationUpdateRequest(BaseModel):
    """Request model for updating a saved generation configuration"""
    name: Optional[str] = None
    llm_config_id: Optional[UUID] = None
    data_source_config_id: Optional[UUID] = None
    dataset_type: Optional[DatasetType] = None
    sample_size: Optional[int] = None 