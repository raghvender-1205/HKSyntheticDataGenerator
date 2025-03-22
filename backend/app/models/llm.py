from pydantic import BaseModel
from typing import Dict, Optional, Union
from enum import Enum

class LLMType(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    CUSTOM = "custom"

class LLMConfig(BaseModel):
    type: LLMType
    api_key: str
    model_name: str
    parameters: Optional[Dict[str, Union[str, int, float]]] = None