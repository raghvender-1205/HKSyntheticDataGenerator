from datetime import datetime
from fastapi import HTTPException

from app.models import SyntheticDataRequest, SyntheticDataResponse
from app.services.data_source import CSVDataSource, DBDataSource
from app.services.llm_service import OpenAILLMService, GeminiLLMService


class SyntheticDataController:
    @staticmethod
    async def generate_synthetic_data(request: SyntheticDataRequest) -> SyntheticDataResponse:
        try:
            # Data Source Factory
            if request.data_source.type == "csv":
                data_source = CSVDataSource(request.data_source)
            elif request.data_source.type == "database":
                data_source = DBDataSource(request.data_source)
            else:
                raise HTTPException(400, "Unsupported data source type")

            # LLM Factory
            if request.llm_config.type == "openai":
                llm = OpenAILLMService(request.llm_config)
            elif request.llm_config.type == "gemini":
                llm = GeminiLLMService(request.llm_config)
            else:
                raise HTTPException(400, "Unsupported LLM type")

            base_data = await data_source.fetch_data(limit=10) # TODO: Send from request (s
            synthetic_data = await llm.generate_synthetic_data(
                base_data,
                request.sample_size,
                request.dataset_type
            )

            return SyntheticDataResponse(
                data=synthetic_data,
                metadata={
                    "source_type": request.data_source.type,
                    "llm_type": request.llm_config.type,
                    "dataset_type": request.dataset_type
                },
                generated_at=datetime.utcnow().isoformat()
            )
        except Exception as e:
            raise HTTPException(500, f"Error generating synthetic data: {str(e)}")