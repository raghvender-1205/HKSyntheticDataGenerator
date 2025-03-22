from datetime import datetime
from fastapi import HTTPException, Depends
from uuid import uuid4

from app.schemas import SyntheticDataRequest, SyntheticDataResponse
from app.services.data_source import CSVDataSource, DBDataSource, PDFDataSource
from app.services.llm_service import OpenAILLMService, GeminiLLMService, CustomLLMService

from app.database import (
    LLMConfigRepository, DataSourceConfigRepository,
    SavedGenerationRepository
)

class SyntheticDataController:
    @staticmethod
    async def generate_synthetic_data(
        request: SyntheticDataRequest,
        llm_repo: LLMConfigRepository,
        datasource_repo: DataSourceConfigRepository,
        saved_repo: SavedGenerationRepository
    ) -> SyntheticDataResponse:
        try:
            # Fetch configurations if IDs are provided
            data_source_config = None
            llm_config = None
            
            if request.datasource_config_id:
                datasource_model = await datasource_repo.get(str(request.datasource_config_id))
                if not datasource_model:
                    raise HTTPException(404, "Data source configuration not found")
                data_source_config = datasource_model.config
                data_source_type = data_source_config.get("type", "unknown")
            else:
                # Use the provided config directly
                data_source_config = request.datasource_config
                if not data_source_config:
                    raise HTTPException(400, "Either datasource_config_id or datasource_config must be provided")
                data_source_type = data_source_config.get("type", "unknown")
            
            if request.llm_config_id:
                llm_model = await llm_repo.get(str(request.llm_config_id))
                if not llm_model:
                    raise HTTPException(404, "LLM configuration not found")
                llm_config = llm_model.config
                llm_type = llm_config.get("type", "unknown")
            else:
                # Use the provided config directly
                llm_config = request.llm_config
                if not llm_config:
                    raise HTTPException(400, "Either llm_config_id or llm_config must be provided")
                llm_type = llm_config.get("type", "unknown")

            # Data Source Factory
            if data_source_type == "csv":
                # Ensure parameters exists for CSV data source
                if isinstance(data_source_config, dict):
                    if 'parameters' not in data_source_config:
                        data_source_config['parameters'] = {}
                data_source = CSVDataSource(data_source_config)
            elif data_source_type == "database":
                # Ensure parameters exists for DB data source
                if isinstance(data_source_config, dict):
                    if 'parameters' not in data_source_config:
                        data_source_config['parameters'] = {}
                data_source = DBDataSource(data_source_config)
            elif data_source_type == "pdf":
                # Ensure source_path and parameters exist for PDF data source
                if isinstance(data_source_config, dict):
                    if 'source_path' not in data_source_config:
                        data_source_config['source_path'] = "data/uploads"
                    if 'parameters' not in data_source_config:
                        data_source_config['parameters'] = {
                            "extract_metadata": "true",
                            "extract_layout": "true"
                        }
                data_source = PDFDataSource(data_source_config)
            else:
                raise HTTPException(400, "Unsupported data source type")

            # LLM Factory
            if llm_type == "openai":
                llm = OpenAILLMService(llm_config)
            elif llm_type == "gemini":
                llm = GeminiLLMService(llm_config)
            elif llm_type == "custom":
                llm = CustomLLMService(llm_config)
            else:
                raise HTTPException(400, "Unsupported LLM type")

            # Generate data
            base_data = await data_source.fetch_data(limit=10)  # TODO: Send from request
            synthetic_data = await llm.generate_synthetic_data(
                base_data,
                request.sample_size,
                request.dataset_type
            )

            # Create response
            response = SyntheticDataResponse(
                data=synthetic_data,
                metadata={
                    "source_type": data_source_type,
                    "llm_type": llm_type,
                    "dataset_type": request.dataset_type,
                    "generated_at": datetime.utcnow().isoformat()
                },
                saved=False
            )
            
            # Save the generation if requested
            if request.save_result:
                # Create a saved generation record
                saved_id = uuid4()
                saved_generation = await saved_repo.create(
                    id=str(saved_id),
                    name=request.save_name or f"Generation {datetime.utcnow().isoformat()}",
                    llm_config_id=str(request.llm_config_id) if request.llm_config_id else None,
                    datasource_config_id=str(request.datasource_config_id) if request.datasource_config_id else None,
                    result={
                        "data": synthetic_data,
                        "metadata": response.metadata
                    }
                )
                response.id = saved_id
                response.saved = True

            return response
        except HTTPException as e:
            # Re-raise HTTP exceptions
            raise e
        except Exception as e:
            raise HTTPException(500, f"Error generating synthetic data: {str(e)}")