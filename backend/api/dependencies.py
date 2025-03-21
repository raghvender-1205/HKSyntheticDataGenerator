from fastapi import Depends
from functools import lru_cache
from typing import Annotated

from core.service import SyntheticDataService

@lru_cache()
def get_service() -> SyntheticDataService:
    """
    Get a singleton instance of the SyntheticDataService.
    """
    return SyntheticDataService() 