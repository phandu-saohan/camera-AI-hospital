from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Sync engine with auto-fallback for seamless local dev
db_url = getattr(settings, "DATABASE_URL", None)
if not db_url or not isinstance(db_url, str):
    db_url = f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

try:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG,
    )
    with engine.connect():
        pass
except Exception as e:
    logger.warning(f"PostgreSQL at {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT} not reachable ({type(e).__name__}). Using SQLite for local dev mode.")
    engine = create_engine(
        "sqlite:///./dev.db",
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db():
    """Sync database dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Async database dependency."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
