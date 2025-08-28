import datetime
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from teledrive.backend.db.base import Base
from teledrive.backend.models.user import User


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    parent_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    parent = relationship("Folder", remote_side=[id], back_populates="children")
    children = relationship("Folder", back_populates="parent")

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="folders")

    files = relationship("File", back_populates="folder", cascade="all, delete-orphan")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    size = Column(BigInteger, nullable=False)
    mime_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    folder = relationship("Folder", back_populates="files")

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="files")

    chunks = relationship("FileChunk", back_populates="file", cascade="all, delete-orphan")


class FileChunk(Base):
    __tablename__ = "file_chunks"

    id = Column(Integer, primary_key=True, index=True)
    telegram_message_id = Column(BigInteger, nullable=False)
    chunk_order = Column(Integer, nullable=False)

    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    file = relationship("File", back_populates="chunks")
