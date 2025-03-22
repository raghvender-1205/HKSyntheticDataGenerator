from pydantic import BaseModel, Field

from app.models.data_source import DataSourceConfig
from app.models.llm import LLMConfig
from app.models.dataset import DatasetType

class SyntheticDataRequest(BaseModel):
    data_source: DataSourceConfig
    llm_config: LLMConfig
    dataset_type: DatasetType
    sample_size: int = Field(..., ge=1)
    output_format: str = "json"

