from teledrive.backend.db.base import Base
from teledrive.backend.db.session import engine

# Import all models here so that Base has them registered
from teledrive.backend.models.user import User
from teledrive.backend.models.file import File, Folder, FileChunk

def init_db():
    print("Creating all database tables...")
    # This will create tables for all models that inherit from Base
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()
