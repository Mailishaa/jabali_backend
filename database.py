import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from rejesha_green.config import settings

database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)

# Heroku may provide postgres:// instead of postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1,
    )


engine = create_engine(
    database_url,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


Base = declarative_base()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()