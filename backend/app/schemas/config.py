from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

# Base schemas with common fields
class BaseSchema(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# LLM Config schemas
class LLMConfigBase(BaseModel):
    name: str
    config: Dict[str, Any]
    is_default: bool = False

class LLMConfigCreate(LLMConfigBase):
    pass

class LLMConfigUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None

class LLMConfig(LLMConfigBase, BaseSchema):
    last_used_at: Optional[datetime] = None

# Data Source Config schemas
class DataSourceConfigBase(BaseModel):
    name: str
    config: Dict[str, Any]
    is_default: bool = False

class DataSourceConfigCreate(DataSourceConfigBase):
    pass

class DataSourceConfigUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None

class DataSourceConfig(DataSourceConfigBase, BaseSchema):
    last_used_at: Optional[datetime] = None

# Saved Generation schemas
class SavedGenerationBase(BaseModel):
    name: str
    llm_config_id: UUID
    data_source_config_id: UUID
    result: Dict[str, Any]

class SavedGenerationCreate(SavedGenerationBase):
    pass

class SavedGenerationUpdate(BaseModel):
    name: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class SavedGeneration(SavedGenerationBase, BaseSchema):
    last_used_at: Optional[datetime] = None
    llm_config: Optional[LLMConfig] = None
    data_source_config: Optional[DataSourceConfig] = None

# Settings schemas
class SettingsBase(BaseModel):
    name: str
    value: Any

class SettingsCreate(SettingsBase):
    pass

class SettingsUpdate(BaseModel):
    value: Any

class Settings(SettingsBase, BaseSchema):
    pass

# Schemas for generation request
class GenerationRequest(BaseModel):
    llm_config_id: Optional[UUID] = None
    data_source_config_id: Optional[UUID] = None
    llm_config: Optional[Dict[str, Any]] = None
    data_source_config: Optional[Dict[str, Any]] = None
    save_result: bool = False
    save_name: Optional[str] = None

class GenerationResponse(BaseModel):
    id: Optional[UUID] = None
    result: Dict[str, Any]
    saved: bool 