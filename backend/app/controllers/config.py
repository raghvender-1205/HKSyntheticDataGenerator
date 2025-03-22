from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException

from app.models import LLMConfig, DataSourceConfig
from app.models.http_models.config import (
    LLMConfigResponse, 
    DataSourceConfigResponse,
    ConfigListResponse,
    SavedGenerationConfig
)


class ConfigController:
    """Controller for managing configurations"""
    
    # In-memory storage for configurations (in a real app, use a database)
    _llm_configs: Dict[UUID, Dict] = {}
    _datasource_configs: Dict[UUID, Dict] = {}
    _saved_generations: Dict[UUID, Dict] = {}
    
    @classmethod
    async def get_all_configs(cls) -> ConfigListResponse:
        """Get all available configurations"""
        llm_configs = [
            LLMConfigResponse(**config)
            for config in cls._llm_configs.values()
        ]
        
        data_source_configs = [
            DataSourceConfigResponse(**config)
            for config in cls._datasource_configs.values()
        ]
        
        return ConfigListResponse(
            llm_configs=llm_configs,
            data_source_configs=data_source_configs
        )
    
    @classmethod
    async def get_llm_config(cls, config_id: UUID) -> LLMConfigResponse:
        """Get an LLM configuration by ID"""
        if config_id not in cls._llm_configs:
            raise HTTPException(404, "LLM configuration not found")
        
        return LLMConfigResponse(**cls._llm_configs[config_id])
    
    @classmethod
    async def create_llm_config(
        cls,
        name: str,
        config: LLMConfig,
        is_default: bool = False
    ) -> LLMConfigResponse:
        """Create a new LLM configuration"""
        # Generate a new UUID for the config
        config_id = uuid4()
        current_time = datetime.utcnow().isoformat()
        
        # If this is set as default, unset any existing default
        if is_default:
            for key in cls._llm_configs:
                if cls._llm_configs[key]["is_default"]:
                    cls._llm_configs[key]["is_default"] = False
        
        # Create the new config record
        config_data = {
            "id": config_id,
            "name": name,
            "config": config,
            "is_default": is_default,
            "created_at": current_time,
            "last_used_at": None
        }
        
        cls._llm_configs[config_id] = config_data
        return LLMConfigResponse(**config_data)
    
    @classmethod
    async def update_llm_config(
        cls,
        config_id: UUID,
        name: Optional[str] = None,
        config: Optional[LLMConfig] = None,
        is_default: Optional[bool] = None
    ) -> LLMConfigResponse:
        """Update an existing LLM configuration"""
        if config_id not in cls._llm_configs:
            raise HTTPException(404, "LLM configuration not found")
        
        config_data = cls._llm_configs[config_id]
        
        # Update fields if provided
        if name is not None:
            config_data["name"] = name
        
        if config is not None:
            config_data["config"] = config
        
        if is_default is not None:
            # If setting as default, unset any existing default
            if is_default and not config_data["is_default"]:
                for key in cls._llm_configs:
                    if cls._llm_configs[key]["is_default"]:
                        cls._llm_configs[key]["is_default"] = False
            
            config_data["is_default"] = is_default
        
        cls._llm_configs[config_id] = config_data
        return LLMConfigResponse(**config_data)
    
    @classmethod
    async def delete_llm_config(cls, config_id: UUID) -> None:
        """Delete an LLM configuration"""
        if config_id not in cls._llm_configs:
            raise HTTPException(404, "LLM configuration not found")
        
        # Check if this was the default configuration
        was_default = cls._llm_configs[config_id]["is_default"]
        
        # Delete the configuration
        del cls._llm_configs[config_id]
        
        # If this was the default and we have other configs, set a new default
        if was_default and cls._llm_configs:
            # Pick the first config as the new default
            first_key = next(iter(cls._llm_configs))
            cls._llm_configs[first_key]["is_default"] = True
    
    @classmethod
    async def get_default_llm_config(cls) -> Optional[LLMConfigResponse]:
        """Get the default LLM configuration"""
        for config in cls._llm_configs.values():
            if config["is_default"]:
                return LLMConfigResponse(**config)
        
        # If no default is set but we have configs, return the first one
        if cls._llm_configs:
            first_key = next(iter(cls._llm_configs))
            return LLMConfigResponse(**cls._llm_configs[first_key])
        
        return None
    
    @classmethod
    async def get_datasource_config(cls, config_id: UUID) -> DataSourceConfigResponse:
        """Get a data source configuration by ID"""
        if config_id not in cls._datasource_configs:
            raise HTTPException(404, "Data source configuration not found")
        
        return DataSourceConfigResponse(**cls._datasource_configs[config_id])
    
    @classmethod
    async def create_datasource_config(
        cls,
        name: str,
        config: DataSourceConfig,
        is_default: bool = False
    ) -> DataSourceConfigResponse:
        """Create a new data source configuration"""
        # Generate a new UUID for the config
        config_id = uuid4()
        current_time = datetime.utcnow().isoformat()
        
        # If this is set as default, unset any existing default
        if is_default:
            for key in cls._datasource_configs:
                if cls._datasource_configs[key]["is_default"]:
                    cls._datasource_configs[key]["is_default"] = False
        
        # Create the new config record
        config_data = {
            "id": config_id,
            "name": name,
            "config": config,
            "is_default": is_default,
            "created_at": current_time,
            "last_used_at": None
        }
        
        cls._datasource_configs[config_id] = config_data
        return DataSourceConfigResponse(**config_data)
    
    @classmethod
    async def update_datasource_config(
        cls,
        config_id: UUID,
        name: Optional[str] = None,
        config: Optional[DataSourceConfig] = None,
        is_default: Optional[bool] = None
    ) -> DataSourceConfigResponse:
        """Update an existing data source configuration"""
        if config_id not in cls._datasource_configs:
            raise HTTPException(404, "Data source configuration not found")
        
        config_data = cls._datasource_configs[config_id]
        
        # Update fields if provided
        if name is not None:
            config_data["name"] = name
        
        if config is not None:
            config_data["config"] = config
        
        if is_default is not None:
            # If setting as default, unset any existing default
            if is_default and not config_data["is_default"]:
                for key in cls._datasource_configs:
                    if cls._datasource_configs[key]["is_default"]:
                        cls._datasource_configs[key]["is_default"] = False
            
            config_data["is_default"] = is_default
        
        cls._datasource_configs[config_id] = config_data
        return DataSourceConfigResponse(**config_data)
    
    @classmethod
    async def delete_datasource_config(cls, config_id: UUID) -> None:
        """Delete a data source configuration"""
        if config_id not in cls._datasource_configs:
            raise HTTPException(404, "Data source configuration not found")
        
        # Check if this was the default configuration
        was_default = cls._datasource_configs[config_id]["is_default"]
        
        # Delete the configuration
        del cls._datasource_configs[config_id]
        
        # If this was the default and we have other configs, set a new default
        if was_default and cls._datasource_configs:
            # Pick the first config as the new default
            first_key = next(iter(cls._datasource_configs))
            cls._datasource_configs[first_key]["is_default"] = True
    
    @classmethod
    async def get_default_datasource_config(cls) -> Optional[DataSourceConfigResponse]:
        """Get the default data source configuration"""
        for config in cls._datasource_configs.values():
            if config["is_default"]:
                return DataSourceConfigResponse(**config)
        
        # If no default is set but we have configs, return the first one
        if cls._datasource_configs:
            first_key = next(iter(cls._datasource_configs))
            return DataSourceConfigResponse(**cls._datasource_configs[first_key])
        
        return None
        
    @classmethod
    async def get_all_saved_generations(cls) -> List[SavedGenerationConfig]:
        """Get all saved generation configurations"""
        return [SavedGenerationConfig(**config) for config in cls._saved_generations.values()]
    
    @classmethod
    async def get_saved_generation(cls, config_id: UUID) -> SavedGenerationConfig:
        """Get a saved generation configuration by ID"""
        if config_id not in cls._saved_generations:
            raise HTTPException(404, "Saved generation configuration not found")
        
        return SavedGenerationConfig(**cls._saved_generations[config_id])
    
    @classmethod
    async def create_saved_generation(
        cls,
        name: str,
        llm_config_id: UUID,
        data_source_config_id: UUID,
        dataset_type: str,
        sample_size: int
    ) -> SavedGenerationConfig:
        """Create a new saved generation configuration"""
        # Validate that the referenced configurations exist
        if llm_config_id not in cls._llm_configs:
            raise HTTPException(404, "LLM configuration not found")
        
        if data_source_config_id not in cls._datasource_configs:
            raise HTTPException(404, "Data source configuration not found")
        
        # Generate a new UUID for the config
        config_id = uuid4()
        current_time = datetime.utcnow().isoformat()
        
        # Create the new config record
        config_data = {
            "id": config_id,
            "name": name,
            "llm_config_id": llm_config_id,
            "data_source_config_id": data_source_config_id,
            "dataset_type": dataset_type,
            "sample_size": sample_size,
            "created_at": current_time,
            "last_used_at": None
        }
        
        cls._saved_generations[config_id] = config_data
        return SavedGenerationConfig(**config_data)
    
    @classmethod
    async def update_saved_generation(
        cls,
        config_id: UUID,
        name: Optional[str] = None,
        llm_config_id: Optional[UUID] = None,
        data_source_config_id: Optional[UUID] = None,
        dataset_type: Optional[str] = None,
        sample_size: Optional[int] = None
    ) -> SavedGenerationConfig:
        """Update an existing saved generation configuration"""
        if config_id not in cls._saved_generations:
            raise HTTPException(404, "Saved generation configuration not found")
        
        config_data = cls._saved_generations[config_id]
        
        # Update fields if provided
        if name is not None:
            config_data["name"] = name
        
        if llm_config_id is not None:
            # Validate that the referenced configuration exists
            if llm_config_id not in cls._llm_configs:
                raise HTTPException(404, "LLM configuration not found")
            config_data["llm_config_id"] = llm_config_id
        
        if data_source_config_id is not None:
            # Validate that the referenced configuration exists
            if data_source_config_id not in cls._datasource_configs:
                raise HTTPException(404, "Data source configuration not found")
            config_data["data_source_config_id"] = data_source_config_id
        
        if dataset_type is not None:
            config_data["dataset_type"] = dataset_type
        
        if sample_size is not None:
            config_data["sample_size"] = sample_size
        
        cls._saved_generations[config_id] = config_data
        return SavedGenerationConfig(**config_data)
    
    @classmethod
    async def delete_saved_generation(cls, config_id: UUID) -> None:
        """Delete a saved generation configuration"""
        if config_id not in cls._saved_generations:
            raise HTTPException(404, "Saved generation configuration not found")
        
        # Delete the configuration
        del cls._saved_generations[config_id]
        
    @classmethod
    async def mark_config_as_used(cls, llm_id: UUID, datasource_id: UUID) -> None:
        """Mark the LLM and data source configurations as last used"""
        current_time = datetime.utcnow().isoformat()
        
        if llm_id in cls._llm_configs:
            cls._llm_configs[llm_id]["last_used_at"] = current_time
            
        if datasource_id in cls._datasource_configs:
            cls._datasource_configs[datasource_id]["last_used_at"] = current_time 