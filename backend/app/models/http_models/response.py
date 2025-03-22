from pydantic import BaseModel
from typing import List, Dict

class SyntheticDataResponse(BaseModel):
    data: List[Dict]
    metadata: Dict
    generated_str: str