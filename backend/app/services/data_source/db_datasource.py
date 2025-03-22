import asyncpg
from typing import List, Dict

from app.services.base import BaseDataSource


class DBDataSource(BaseDataSource):
    async def fetch_data(self, limit: int) -> List[Dict]:
        conn = await asyncpg.connect(self.config.connection_string)
        try:
            # Assuming parameters contains table name
            table_name = self.config.parameters.get("table_name", "data")
            records = await conn.fetch(f"SELECT * FROM {table_name} LIMIT $1", limit)

            return [dict(record) for record in records]
        finally:
            await conn.close()

    async def get_schema(self) -> Dict:
        conn = await asyncpg.connect(self.config.connection_string)
        try:
            table_name = self.config.parameters.get("table_name", "data")
            schema = await conn.fetch(
                "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = $1",
                table_name
            )

            return {row["column_name"]: row["data_type"] for row in schema}
        finally:
            await conn.close()