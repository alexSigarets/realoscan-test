from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


import os
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("BASE")



Base = declarative_base()

DATABASE_URL = BASE


engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session