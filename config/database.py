from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from config.config import DATABASE_URL

Base = declarative_base()

engine = create_async_engine(DATABASE_URL)


async_session = async_sessionmaker(engine,class_=AsyncSession,expire_on_commit=False,autoflush=True)



async def get_db():

    async with async_session() as session:
        yield session