import pandas as pd
from typing import List, Dict

from app.services.base import BaseDataSource


class CSVDataSource(BaseDataSource):
    async def fetch_data(self, limit: int) -> List[Dict]:
        df = pd.read_csv(self.config.connection_string)

        return df.head(limit).to_dict('records')

    async def get_schema(self) -> Dict:
        df = pd.read_csv(self.config.connection_string)

        return {"columns": list(df.columns), "types": df.dtypes.to_dict()}