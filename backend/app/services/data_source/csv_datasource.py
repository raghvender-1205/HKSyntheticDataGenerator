import pandas as pd
from typing import List, Dict

from app.services.base import BaseDataSource
from app.models import DataSourceConfig


class CSVDataSource(BaseDataSource):
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        
        # Add fallback handling for parameters
        self.parameters = {}
        if hasattr(config, 'parameters') and config.parameters is not None:
            self.parameters = config.parameters
        elif isinstance(config, dict) and 'parameters' in config:
            self.parameters = config['parameters']

    async def fetch_data(self, limit: int) -> List[Dict]:
        df = pd.read_csv(self.config.connection_string)

        return df.head(limit).to_dict('records')

    async def get_schema(self) -> Dict:
        df = pd.read_csv(self.config.connection_string)

        return {"columns": list(df.columns), "types": df.dtypes.to_dict()}