from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from teledrive.backend.core.config import settings

# The `connect_args` is needed only for SQLite.
# It's not needed for other databases.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
