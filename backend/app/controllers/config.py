from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from fastapi import HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError

from app.database import (
    LLMConfigRepository, DataSourceConfigRepository,
    SavedGenerationRepository, SettingsRepository,
    get_llm_config_repository, get_datasource_config_repository,
    get_saved_generation_repository, get_settings_repository
)

from app.schemas import (
    LLMConfig, LLMConfigCreate, LLMConfigUpdate,
    DataSourceConfig, DataSourceConfigCreate, DataSourceConfigUpdate,
    SavedGeneration, SavedGenerationCreate, SavedGenerationUpdate,
    GenerationRequest, GenerationResponse
)

class ConfigController:
    """Controller for managing configurations using database repositories"""
    
    @staticmethod
    async def get_all_configs(
        llm_repo: LLMConfigRepository,
        datasource_repo: DataSourceConfigRepository
    ):
        """Get all available configurations"""
        try:
            llm_configs = await llm_repo.get_all()
            datasource_configs = await datasource_repo.get_all()
            
            return {
                "llm_configs": llm_configs,
                "data_source_configs": datasource_configs
            }
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error retrieving configurations: {str(e)}"
            )
    
    @staticmethod
    async def get_llm_config(
        config_id: UUID,
        llm_repo: LLMConfigRepository
    ) -> LLMConfig:
        """Get an LLM configuration by ID"""
        try:
            config = await llm_repo.get(str(config_id))
            if not config:
                raise HTTPException(404, "LLM configuration not found")
            return config
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error retrieving LLM configuration: {str(e)}"
            )
    
    @staticmethod
    async def create_llm_config(
        config: LLMConfigCreate,
        llm_repo: LLMConfigRepository
    ) -> LLMConfig:
        """Create a new LLM configuration"""
        try:
            # If this is set as default, we need to handle that logic
            if config.is_default:
                # Get the current default, if any
                default_config = await llm_repo.get_default()
                if default_config:
                    # Unset it as default
                    await llm_repo.update(str(default_config.id), is_default=False)
            
            # Create the new config
            return await llm_repo.create(
                name=config.name,
                config=config.config,
                is_default=config.is_default
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error creating LLM configuration: {str(e)}"
            )
    
    @staticmethod
    async def update_llm_config(
        config_id: UUID,
        config: LLMConfigUpdate,
        llm_repo: LLMConfigRepository
    ) -> LLMConfig:
        """Update an existing LLM configuration"""
        try:
            # Check if the config exists
            existing_config = await llm_repo.get(str(config_id))
            if not existing_config:
                raise HTTPException(404, "LLM configuration not found")
            
            # Create a dict of updates, only including non-None values
            updates = {k: v for k, v in config.model_dump().items() if v is not None}
            
            # Handle default flag separately if needed
            if config.is_default is not None and config.is_default:
                # Get the current default, if any and it's not this config
                default_config = await llm_repo.get_default()
                if default_config and default_config.id != config_id:
                    # Unset it as default
                    await llm_repo.update(str(default_config.id), is_default=False)
            
            # Update the config
            return await llm_repo.update(str(config_id), **updates)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error updating LLM configuration: {str(e)}"
            )
    
    @staticmethod
    async def delete_llm_config(
        config_id: UUID,
        llm_repo: LLMConfigRepository
    ) -> None:
        """Delete an LLM configuration"""
        try:
            # Check if the config exists
            existing_config = await llm_repo.get(str(config_id))
            if not existing_config:
                raise HTTPException(404, "LLM configuration not found")
            
            # If this was the default, we'll need to set a new default
            was_default = existing_config.is_default
            
            # Delete the config
            await llm_repo.delete(str(config_id))
            
            # If this was the default, set a new one
            if was_default:
                # Get all remaining configs
                configs = await llm_repo.get_all()
                if configs:
                    # Set the first one as default
                    await llm_repo.set_as_default(str(configs[0].id))
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error deleting LLM configuration: {str(e)}"
            )
    
    @staticmethod
    async def get_default_llm_config(
        llm_repo: LLMConfigRepository
    ) -> Optional[LLMConfig]:
        """Get the default LLM configuration"""
        try:
            default_config = await llm_repo.get_default()
            if not default_config:
                # If no default is set but we have configs, set the first one
                configs = await llm_repo.get_all()
                if configs:
                    # Set the first one as default
                    default_config = await llm_repo.set_as_default(str(configs[0].id))
            
            return default_config
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error retrieving default LLM configuration: {str(e)}"
            )
    
    @staticmethod
    async def get_datasource_config(
        config_id: UUID,
        datasource_repo: DataSourceConfigRepository
    ) -> DataSourceConfig:
        """Get a data source configuration by ID"""
        try:
            config = await datasource_repo.get(str(config_id))
            if not config:
                raise HTTPException(404, "Data source configuration not found")
            return config
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error retrieving data source configuration: {str(e)}"
            )
    
    @staticmethod
    async def create_datasource_config(
        config: DataSourceConfigCreate,
        datasource_repo: DataSourceConfigRepository
    ) -> DataSourceConfig:
        """Create a new data source configuration"""
        try:
            # If this is set as default, we need to handle that logic
            if config.is_default:
                # Get the current default, if any
                default_config = await datasource_repo.get_default()
                if default_config:
                    # Unset it as default
                    await datasource_repo.update(str(default_config.id), is_default=False)
            
            # Create the new config
            return await datasource_repo.create(
                name=config.name,
                config=config.config,
                is_default=config.is_default
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error creating data source configuration: {str(e)}"
            )
    
    @staticmethod
    async def update_datasource_config(
        config_id: UUID,
        config: DataSourceConfigUpdate,
        datasource_repo: DataSourceConfigRepository
    ) -> DataSourceConfig:
        """Update an existing data source configuration"""
        try:
            # Check if the config exists
            existing_config = await datasource_repo.get(str(config_id))
            if not existing_config:
                raise HTTPException(404, "Data source configuration not found")
            
            # Create a dict of updates, only including non-None values
            updates = {k: v for k, v in config.model_dump().items() if v is not None}
            
            # Handle default flag separately if needed
            if config.is_default is not None and config.is_default:
                # Get the current default, if any and it's not this config
                default_config = await datasource_repo.get_default()
                if default_config and default_config.id != config_id:
                    # Unset it as default
                    await datasource_repo.update(str(default_config.id), is_default=False)
            
            # Update the config
            return await datasource_repo.update(str(config_id), **updates)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error updating data source configuration: {str(e)}"
            )
    
    @staticmethod
    async def delete_datasource_config(
        config_id: UUID,
        datasource_repo: DataSourceConfigRepository
    ) -> None:
        """Delete a data source configuration"""
        try:
            # Check if the config exists
            existing_config = await datasource_repo.get(str(config_id))
            if not existing_config:
                raise HTTPException(404, "Data source configuration not found")
            
            # If this was the default, we'll need to set a new default
            was_default = existing_config.is_default
            
            # Delete the config
            await datasource_repo.delete(str(config_id))
            
            # If this was the default, set a new one
            if was_default:
                # Get all remaining configs
                configs = await datasource_repo.get_all()
                if configs:
                    # Set the first one as default
                    await datasource_repo.set_as_default(str(configs[0].id))
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error deleting data source configuration: {str(e)}"
            )
    
    @staticmethod
    async def get_default_datasource_config(
        datasource_repo: DataSourceConfigRepository
    ) -> Optional[DataSourceConfig]:
        """Get the default data source configuration"""
        try:
            default_config = await datasource_repo.get_default()
            if not default_config:
                # If no default is set but we have configs, set the first one
                configs = await datasource_repo.get_all()
                if configs:
                    # Set the first one as default
                    default_config = await datasource_repo.set_as_default(str(configs[0].id))
            
            return default_config
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error retrieving default data source configuration: {str(e)}"
            )
    
    @staticmethod
    async def get_all_saved_generations(
        saved_repo: SavedGenerationRepository
    ) -> List[SavedGeneration]:
        """Get all saved generation configurations"""
        try:
            return await saved_repo.get_all()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error retrieving saved generations: {str(e)}"
            )
    
    @staticmethod
    async def get_saved_generation(
        config_id: UUID,
        saved_repo: SavedGenerationRepository
    ) -> SavedGeneration:
        """Get a saved generation configuration by ID"""
        try:
            config = await saved_repo.get(str(config_id))
            if not config:
                raise HTTPException(404, "Saved generation not found")
            return config
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error retrieving saved generation: {str(e)}"
            )
    
    @staticmethod
    async def create_saved_generation(
        config: SavedGenerationCreate,
        saved_repo: SavedGenerationRepository,
        llm_repo: LLMConfigRepository,
        datasource_repo: DataSourceConfigRepository
    ) -> SavedGeneration:
        """Create a new saved generation"""
        try:
            # Validate that referenced configs exist
            llm_config = await llm_repo.get(str(config.llm_config_id))
            if not llm_config:
                raise HTTPException(404, "LLM configuration not found")
            
            datasource_config = await datasource_repo.get(str(config.data_source_config_id))
            if not datasource_config:
                raise HTTPException(404, "Data source configuration not found")
            
            # Create the new saved generation
            return await saved_repo.create(
                **config.model_dump()
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error creating saved generation: {str(e)}"
            )
    
    @staticmethod
    async def update_saved_generation(
        config_id: UUID,
        config: SavedGenerationUpdate,
        saved_repo: SavedGenerationRepository
    ) -> SavedGeneration:
        """Update an existing saved generation"""
        try:
            # Check if the config exists
            existing_config = await saved_repo.get(str(config_id))
            if not existing_config:
                raise HTTPException(404, "Saved generation not found")
            
            # Create a dict of updates, only including non-None values
            updates = {k: v for k, v in config.model_dump().items() if v is not None}
            
            # Update the config
            return await saved_repo.update(str(config_id), **updates)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error updating saved generation: {str(e)}"
            )
    
    @staticmethod
    async def delete_saved_generation(
        config_id: UUID,
        saved_repo: SavedGenerationRepository
    ) -> None:
        """Delete a saved generation"""
        try:
            # Check if the config exists
            existing_config = await saved_repo.get(str(config_id))
            if not existing_config:
                raise HTTPException(404, "Saved generation not found")
            
            # Delete the config
            await saved_repo.delete(str(config_id))
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error deleting saved generation: {str(e)}"
            )
    
    @staticmethod
    async def mark_config_as_used(
        llm_id: UUID,
        datasource_id: UUID,
        llm_repo: LLMConfigRepository,
        datasource_repo: DataSourceConfigRepository
    ) -> None:
        """Mark the LLM and data source configurations as last used"""
        try:
            # Mark LLM config as used
            if llm_id:
                await llm_repo.mark_as_used(str(llm_id))
            
            # Mark data source config as used
            if datasource_id:
                await datasource_repo.mark_as_used(str(datasource_id))
        except SQLAlchemyError as e:
            # Don't fail the request if marking as used fails
            # Just log the error
            print(f"Error marking configs as used: {str(e)}")
            
    @staticmethod
    async def get_all_settings(
        settings_repo: SettingsRepository
    ) -> dict:
        """Get all application settings"""
        try:
            # Get all settings
            settings_models = await settings_repo.get_all()
            
            # Convert to a dictionary
            settings_dict = {}
            for setting in settings_models:
                settings_dict[setting.name] = setting.value
            
            # If no settings are found, return default settings
            if not settings_dict:
                settings_dict = {
                    "theme": "light",
                    "language": "en",
                    "notifications_enabled": True,
                    "api_keys": {
                        "openai": "",
                        "gemini": ""
                    }
                }
                
                # Save default settings
                for name, value in settings_dict.items():
                    await settings_repo.create(name=name, value=value)
            
            return settings_dict
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error retrieving settings: {str(e)}"
            )
    
    @staticmethod
    async def update_settings(
        settings: dict,
        settings_repo: SettingsRepository
    ) -> dict:
        """Update application settings"""
        try:
            # Update each setting
            for name, value in settings.items():
                # Check if setting exists
                setting = await settings_repo.get_by_name(name)
                if setting:
                    # Update existing setting
                    await settings_repo.update(str(setting.id), value=value)
                else:
                    # Create new setting
                    await settings_repo.create(name=name, value=value)
            
            # Return updated settings
            return await ConfigController.get_all_settings(settings_repo)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error updating settings: {str(e)}"
            ) 