import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
import sys

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models for autogenerate
try:
    from app.db.base import Base
    import app.models  # noqa: F401 - triggers all imports
    target_metadata = Base.metadata
except Exception as e:
    print(f"Warning: Could not import models: {e}")
    target_metadata = None

# Get DATABASE_URL from environment
database_url = os.getenv("DATABASE_URL") or (
    f"postgresql+psycopg2://"
    f"{os.getenv('POSTGRES_USER', 'postgres')}:"
    f"{os.getenv('POSTGRES_PASSWORD', 'postgres')}@"
    f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
    f"{os.getenv('POSTGRES_PORT', '5432')}/"
    f"{os.getenv('POSTGRES_DB', 'ai_hospital_camera')}"
)
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
