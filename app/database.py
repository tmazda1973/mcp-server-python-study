from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DATABASE_URL = (
    settings.DATABASE_URL or "postgresql://postgres:postgres@localhost:5432/postgres"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

__all__ = [
    "get_db",
]


def get_db():
    """
    データベースセッションを取得する
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
