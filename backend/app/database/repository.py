from datetime import datetime
from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from uuid import UUID

from app.database.models import LLMConfigModel, DataSourceConfigModel, SavedGenerationModel, SettingsModel

# Generic type for our models
T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    Base repository class with common database operations
    """
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    async def get(self, id: str) -> Optional[T]:
        """Get a single record by ID"""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalars().first()

    async def get_all(self) -> List[T]:
        """Get all records"""
        result = await self.session.execute(
            select(self.model_class)
        )
        return result.scalars().all()

    async def create(self, **kwargs) -> T:
        """Create a new record"""
        obj = self.model_class(**kwargs)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: str, **kwargs) -> Optional[T]:
        """Update a record"""
        await self.session.execute(
            update(self.model_class)
            .where(self.model_class.id == id)
            .values(**kwargs)
        )
        await self.session.commit()
        return await self.get(id)

    async def delete(self, id: str) -> bool:
        """Delete a record"""
        await self.session.execute(
            delete(self.model_class)
            .where(self.model_class.id == id)
        )
        await self.session.commit()
        return True

class LLMConfigRepository(BaseRepository[LLMConfigModel]):
    """Repository for LLM configurations"""
    def __init__(self, session: AsyncSession):
        super().__init__(session, LLMConfigModel)

    async def get_default(self) -> Optional[LLMConfigModel]:
        """Get the default LLM configuration"""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.is_default == True)
        )
        return result.scalars().first()

    async def mark_as_used(self, id: str) -> Optional[LLMConfigModel]:
        """Mark a configuration as used"""
        return await self.update(id, last_used_at=datetime.utcnow())

    async def set_as_default(self, id: str) -> Optional[LLMConfigModel]:
        """Set a configuration as the default"""
        # First unset any existing default
        await self.session.execute(
            update(self.model_class)
            .where(self.model_class.is_default == True)
            .values(is_default=False)
        )
        # Then set the new default
        return await self.update(id, is_default=True)

class DataSourceConfigRepository(BaseRepository[DataSourceConfigModel]):
    """Repository for data source configurations"""
    def __init__(self, session: AsyncSession):
        super().__init__(session, DataSourceConfigModel)

    async def get_default(self) -> Optional[DataSourceConfigModel]:
        """Get the default data source configuration"""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.is_default == True)
        )
        return result.scalars().first()

    async def mark_as_used(self, id: str) -> Optional[DataSourceConfigModel]:
        """Mark a configuration as used"""
        return await self.update(id, last_used_at=datetime.utcnow())

    async def set_as_default(self, id: str) -> Optional[DataSourceConfigModel]:
        """Set a configuration as the default"""
        # First unset any existing default
        await self.session.execute(
            update(self.model_class)
            .where(self.model_class.is_default == True)
            .values(is_default=False)
        )
        # Then set the new default
        return await self.update(id, is_default=True)

class SavedGenerationRepository(BaseRepository[SavedGenerationModel]):
    """Repository for saved generation configurations"""
    def __init__(self, session: AsyncSession):
        super().__init__(session, SavedGenerationModel)

    async def mark_as_used(self, id: str) -> Optional[SavedGenerationModel]:
        """Mark a configuration as used"""
        return await self.update(id, last_used_at=datetime.utcnow())

class SettingsRepository(BaseRepository[SettingsModel]):
    """Repository for application settings"""
    def __init__(self, session: AsyncSession):
        super().__init__(session, SettingsModel)

    async def get_by_name(self, name: str) -> Optional[SettingsModel]:
        """Get a setting by name"""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.name == name)
        )
        return result.scalars().first()

    async def set_value(self, name: str, value: Any) -> SettingsModel:
        """Set a setting value by name"""
        setting = await self.get_by_name(name)
        if setting:
            return await self.update(setting.id, value=value, updated_at=datetime.utcnow())
        else:
            return await self.create(name=name, value=value) 