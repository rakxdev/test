from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from teledrive.backend.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    files = relationship("File", back_populates="owner")
    folders = relationship("Folder", back_populates="owner")
