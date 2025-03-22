import asyncpg
from typing import List, Dict

from app.services.base import BaseDataSource
from app.models import DataSourceConfig


class DBDataSource(BaseDataSource):
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        
        # Add fallback handling for parameters
        self.parameters = {}
        if hasattr(config, 'parameters') and config.parameters is not None:
            self.parameters = config.parameters
        elif isinstance(config, dict) and 'parameters' in config:
            self.parameters = config['parameters']
        
        # Assuming parameters contains table name
        table_name = self.parameters.get("table_name", "data")
        self.table_name = table_name

    async def fetch_data(self, limit: int) -> List[Dict]:
        conn = await asyncpg.connect(self.config.connection_string)
        try:
            records = await conn.fetch(f"SELECT * FROM {self.table_name} LIMIT $1", limit)

            return [dict(record) for record in records]
        finally:
            await conn.close()

    async def get_schema(self) -> Dict:
        conn = await asyncpg.connect(self.config.connection_string)
        try:
            schema = await conn.fetch(
                "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = $1",
                self.table_name
            )

            return {row["column_name"]: row["data_type"] for row in schema}
        finally:
            await conn.close()