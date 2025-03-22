from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from enum import Enum
from uuid import UUID

class DatasetType(str, Enum):
    """Type of dataset to generate"""
    TABULAR = "tabular"
    TEXT = "text"
    TIME_SERIES = "time_series"
    IMAGE = "image"

class SyntheticDataRequest(BaseModel):
    """Request model for generating synthetic data"""
    llm_config_id: Optional[UUID] = None
    datasource_config_id: Optional[UUID] = None
    llm_config: Optional[Dict[str, Any]] = None
    datasource_config: Optional[Dict[str, Any]] = None
    dataset_type: DatasetType
    sample_size: int = Field(..., ge=1, le=1000)
    output_format: str = "json"
    save_result: bool = False
    save_name: Optional[str] = None

class SyntheticDataResponse(BaseModel):
    """Response model for generated synthetic data"""
    id: Optional[UUID] = None
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    saved: bool = False 