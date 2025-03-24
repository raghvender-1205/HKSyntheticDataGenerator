from datetime import datetime
import uuid
from typing import Optional
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .db import Base

# UUID function that works with both PostgreSQL and SQLite
def get_uuid():
    return str(uuid.uuid4())

class LLMConfigModel(Base):
    """
    Database model for LLM configurations
    """
    __tablename__ = "llm_configs"

    id = Column(String, primary_key=True, default=get_uuid)
    name = Column(String, nullable=False, index=True)
    config = Column(JSON, nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    saved_generations = relationship("SavedGenerationModel", back_populates="llm_config")

class DataSourceConfigModel(Base):
    """
    Database model for data source configurations
    """
    __tablename__ = "datasource_configs"

    id = Column(String, primary_key=True, default=get_uuid)
    name = Column(String, nullable=False, index=True)
    config = Column(JSON, nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    saved_generations = relationship("SavedGenerationModel", back_populates="data_source_config")

class SavedGenerationModel(Base):
    """
    Database model for saved generation configurations
    """
    __tablename__ = "saved_generations"

    id = Column(String, primary_key=True, default=get_uuid)
    name = Column(String, nullable=False, index=True)
    llm_config_id = Column(String, ForeignKey("llm_configs.id"), nullable=False)
    data_source_config_id = Column(String, ForeignKey("datasource_configs.id"), nullable=False)
    dataset_type = Column(String, nullable=False)
    sample_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    llm_config = relationship("LLMConfigModel", back_populates="saved_generations")
    data_source_config = relationship("DataSourceConfigModel", back_populates="saved_generations")

class SettingsModel(Base):
    """
    Database model for application settings
    """
    __tablename__ = "settings"

    id = Column(String, primary_key=True, default=get_uuid)
    name = Column(String, nullable=False, unique=True, index=True)
    value = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 