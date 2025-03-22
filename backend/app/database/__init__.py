from .db import Base, engine, get_db, AsyncSessionLocal
from .models import LLMConfigModel, DataSourceConfigModel, SavedGenerationModel, SettingsModel
from .repository import (
    LLMConfigRepository, 
    DataSourceConfigRepository, 
    SavedGenerationRepository, 
    SettingsRepository
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

__all__ = [
    "Base", "engine", "get_db", "AsyncSessionLocal",
    "LLMConfigModel", "DataSourceConfigModel", "SavedGenerationModel", "SettingsModel",
    "LLMConfigRepository", "DataSourceConfigRepository", "SavedGenerationRepository", "SettingsRepository",
    "get_llm_config_repository", "get_datasource_config_repository", 
    "get_saved_generation_repository", "get_settings_repository"
]

# Repository dependencies for dependency injection
async def get_llm_config_repository(db: AsyncSession = Depends(get_db)) -> LLMConfigRepository:
    return LLMConfigRepository(db)

async def get_datasource_config_repository(db: AsyncSession = Depends(get_db)) -> DataSourceConfigRepository:
    return DataSourceConfigRepository(db)

async def get_saved_generation_repository(db: AsyncSession = Depends(get_db)) -> SavedGenerationRepository:
    return SavedGenerationRepository(db)

async def get_settings_repository(db: AsyncSession = Depends(get_db)) -> SettingsRepository:
    return SettingsRepository(db) 