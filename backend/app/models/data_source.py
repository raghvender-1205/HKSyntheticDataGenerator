from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Optional

class DataSourceType(str, Enum):
    CSV = "csv"
    DATABASE = "database"
    API = "api"
    PDF = "pdf"
    WEB_URL = "web_url"

class DataSourceConfig(BaseModel):
    type: DataSourceType
    connection_string: str
    source_path: Optional[str] = None
    parameters: Optional[Dict[str, str]] = None