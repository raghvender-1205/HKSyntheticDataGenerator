from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import settings

# SQLite database URL - we'll use SQLite for simplicity
# Use SQLite for development with async support
SQLALCHEMY_DATABASE_URL = settings.database_url or "sqlite+aiosqlite:///./synthetic_data.db"

# Create async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {},
    echo=True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
async def get_db():
    """
    Dependency that provides a database session
    Yields a database session and ensures it's closed after use
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 