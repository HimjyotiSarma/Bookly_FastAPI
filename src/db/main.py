from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.config import settings
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

engine = AsyncEngine(
    create_engine(
        url = settings.DATABASE_URL,
        echo= True
    )
)
# Initialize Database

async def init_db():
    async with engine.begin() as conn:
        # from src.books.models import Book

        await conn.run_sync(SQLModel.metadata.create_all)


# Define New Session Maker

async def get_session():
    Session= sessionmaker(
        bind=engine,
        class_= AsyncSession,
        expire_on_commit=False
    )

    async with Session() as session:
        yield session