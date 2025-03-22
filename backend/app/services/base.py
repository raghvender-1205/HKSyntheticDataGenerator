from abc import ABC, abstractmethod
from typing import List, Dict

from app.models import DataSourceConfig, LLMConfig, DatasetType


class BaseDataSource(ABC):
    def __init__(self, config: DataSourceConfig):
        self.config = config

    @abstractmethod
    async def fetch_data(self, limit: int) -> List[Dict]:
        pass

    @abstractmethod
    async def get_schema(self) -> Dict:
        pass


class BaseLLMService(ABC):
    """
    Base LLM Service to generate synthetic data
    """
    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    async def generate_synthetic_data(
        self,
        base_data: List[Dict],
        sample_size: int,
        dataset_type: DatasetType
    ) -> List[Dict]:
        pass

    @abstractmethod
    def _create_prompt(self, base_data: List[Dict], dataset_type: DatasetType, sample_size: int) -> str:
        pass

    @abstractmethod
    def _format_response(self, result: Dict, dataset_type: DatasetType) -> List[Dict]:
        pass


