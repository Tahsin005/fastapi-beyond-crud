from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from src.config import Config
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = (
    f"postgresql+asyncpg://{Config.POSTGRES_USER}:"
    f"{Config.POSTGRES_PASSWORD}@localhost:5432/{Config.POSTGRES_DB}"
)

engine = create_async_engine(DATABASE_URL, echo=True)

async def init_db():
    async with engine.begin() as conn:
        from src.db.models import Book
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with Session() as session:
        yield session