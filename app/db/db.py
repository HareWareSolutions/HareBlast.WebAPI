from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager

DATABASE_URL_HAREWARE = "postgresql+asyncpg://postgres:HareWare%402024@localhost/harewarebase"
DATABASE_URL_EMPRESA_TESTE = "postgresql+asyncpg://postgres:HareWare%402024@localhost/empresateste"


def get_database_url(env: str = "hareware"):
    if env == "hareware":
        return DATABASE_URL_HAREWARE
    elif env == "12345678000190":
        return DATABASE_URL_EMPRESA_TESTE
    else:
        raise ValueError(f"Ambiente {env} não reconhecido!")


def get_engine_and_session(env: str = "hareware"):
    DATABASE_URL = get_database_url(env)
    engine = create_async_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(
        engine, class_=AsyncSession, autocommit=False, autoflush=False
    )
    return engine, SessionLocal


Base = declarative_base()


@asynccontextmanager
async def get_db(env: str = "hareware"):
    engine, SessionLocal = get_engine_and_session(env)
    async with SessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e
        finally:
            await db.close()
