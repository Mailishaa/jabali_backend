import os
from dotenv import load_dotenv
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from database import Base

from rejesha_green.models.activity import Activity
from rejesha_green.models.community_forest_association import CommunityForestAssociation
from rejesha_green.models.forest_zone import ForestZone
from rejesha_green.models.incident import IncidentReport
from rejesha_green.models.permit import Permit
from rejesha_green.models.reforestation_log import TreeSurvivalLog
from rejesha_green.models.registration_payment import RegistrationPayment
from rejesha_green.models.user import User


load_dotenv()

config = context.config

database_url = os.getenv("DATABASE_URL")

# Heroku can provide a URL beginning with postgres://.
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql+psycopg2://",
        1
    )

config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%")
)


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
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
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()