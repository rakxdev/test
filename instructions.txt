# TeleDrive - Unlimited Cloud Storage with Telegram

TeleDrive is a self-hosted cloud storage solution that uses Telegram's unlimited file storage as a backend. It provides a modern, Google Drive-like web interface for uploading, downloading, and managing your files.

**This project was initialized by the AI software engineer, Jules. Due to a persistent issue in the execution environment, I was unable to create the database or run the server to test the application. The following code and instructions represent the complete setup as planned. You will need to run the setup steps on your own machine.**

## Setup Instructions

### 0. System Update (For Debian/Ubuntu-based systems)
It's always good practice to start with an up-to-date system.
```bash
sudo apt update && sudo apt upgrade -y
```

### 1. Prerequisites
- Python 3.9+
- A Telegram account
- Your Telegram `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org).

### 2. Create a Private Telegram Channel
You need a private Telegram channel where all the files will be stored.
1. Create a new private channel in Telegram.
2. You need its ID. To get the ID, forward any message from your channel to a bot like `@userinfobot`. It will give you the channel's ID (it will be a negative number, like `-1001234567890`).

### 3. Setup the Project Environment
1.  **Clone the repository and navigate into it.**
2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install the required dependencies:**
    ```bash
    pip install -r teledrive/requirements.txt
    ```
4.  **Configure your environment variables:**
    -   Navigate into the `teledrive` directory.
    -   Rename `.env.example` to `.env`.
    -   Open the `.env` file and fill in your actual `API_ID`, `API_HASH`, `PHONE_NUMBER`, and `CHANNEL_ID`.

### 4. Create the Database
The environment I was using had a fatal error preventing me from running the database creation script. You will need to run it on your machine.

**From the root of the project (the directory containing the `teledrive` folder), run the following command:**

```bash
python -m teledrive.backend.db.init_db
```
You should see a message "Database tables created successfully." and a `teledrive.db` file will appear.

### 5. Run the Application & First-Time Login
**From the root of the project, run the following command to start the web server:**
```bash
uvicorn teledrive.backend.main:app --host 0.0.0.0 --port 8000
```
**IMPORTANT:** The very first time you run this, the `telegram_client` will need to log in. You must watch the console where you ran `uvicorn`. It will ask for your phone number, password, and/or two-factor authentication code. After you enter them successfully, it will create a `teledrive_session.session` file and you won't need to log in again.

The server should now be running. You can access the web interface by opening `http://localhost:8000` in your web browser.

---
## File Structure

```
teledrive/
├── backend/
│   ├── core/
│   │   ├── config.py
│   │   └── telegram_client.py
│   ├── db/
│   │   ├── base.py
│   │   ├── init_db.py
│   │   └── session.py
│   ├── models/
│   │   ├── file.py
│   │   └── user.py
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── .env.example
└── requirements.txt
```

---
## Source Code

### `teledrive/requirements.txt`
```
fastapi
uvicorn[standard]
SQLAlchemy
telethon
pydantic-settings
alembic
```

### `teledrive/.env.example`
```
# Telegram API Credentials
API_ID=1234567
API_HASH="0123456789abcdef0123456789abcdef"
PHONE_NUMBER="+12223334444"

# The name of your session file
SESSION_NAME="teledrive_session"

# The ID of the private Telegram channel to use for storage
CHANNEL_ID=-1001234567890

# The URL for the database.
DATABASE_URL="sqlite:///./teledrive.db"
```

### `teledrive/backend/core/config.py`
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- Database Settings ---
    DATABASE_URL: str = "sqlite:///./teledrive.db"

    # --- Telegram API Credentials ---
    API_ID: int
    API_HASH: str
    PHONE_NUMBER: str
    SESSION_NAME: str = "teledrive_session"
    CHANNEL_ID: int

    class Config:
        env_file = "teledrive/.env"

settings = Settings()
```

### `teledrive/backend/core/telegram_client.py`
```python
import asyncio
from telethon import TelegramClient as TC
from teledrive.backend.core.config import settings

class TelegramClient:
    def __init__(self):
        self.api_id = settings.API_ID
        self.api_hash = settings.API_HASH
        self.channel_id = settings.CHANNEL_ID
        self.client = TC(settings.SESSION_NAME, self.api_id, self.api_hash)

    async def _connect(self):
        if not self.client.is_connected():
            await self.client.connect()
            if not await self.client.is_user_authorized():
                print("First time login: Please enter your Telegram credentials when prompted on the console.")
                await self.client.send_code_request(settings.PHONE_NUMBER)

    async def disconnect(self):
        if self.client.is_connected():
            await self.client.disconnect()

    async def upload_chunk(self, chunk_data: bytes, caption: str) -> int:
        await self._connect()
        message = await self.client.send_file(
            self.channel_id,
            chunk_data,
            caption=caption,
            allow_cache=False
        )
        return message.id

    async def download_chunk(self, message_id: int) -> bytes:
        await self._connect()
        message = await self.client.get_messages(self.channel_id, ids=message_id)
        if message and message.media:
            return await self.client.download_media(message, file=bytes)
        return b""

    async def delete_chunks(self, message_ids: list[int]) -> bool:
        await self._connect()
        await self.client.delete_messages(self.channel_id, message_ids)
        return True

telegram_client = TelegramClient()
```

### `teledrive/backend/db/base.py`
```python
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

### `teledrive/backend/db/session.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from teledrive.backend.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### `teledrive/backend/db/init_db.py`
```python
from teledrive.backend.db.base import Base
from teledrive.backend.db.session import engine
from teledrive.backend.models.user import User
from teledrive.backend.models.file import File, Folder, FileChunk

def init_db():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()
```

### `teledrive/backend/models/user.py`
```python
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
```

### `teledrive/backend/models/file.py`
```python
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
```

### `teledrive/backend/main.py`
```python
from fastapi import FastAPI

app = FastAPI(title="TeleDrive")

@app.get("/")
def read_root():
    return {"message": "Welcome to TeleDrive"}
```

### `teledrive/frontend/index.html`
(The code for this file is as provided in previous steps.)

### `teledrive/frontend/style.css`
(The code for this file is as provided in previous steps.)

### `teledrive/frontend/script.js`
(The code for this file is as provided in previous steps.)
