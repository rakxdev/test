import asyncio
from telethon import TelegramClient as TC
from telethon.sessions import StringSession

from teledrive.backend.core.config import settings

class TelegramClient:
    """
    A service class to handle all interactions with the Telegram API using Telethon.
    """
    def __init__(self):
        self.api_id = settings.API_ID
        self.api_hash = settings.API_HASH
        self.channel_id = settings.CHANNEL_ID

        # Using a session name will create a .session file to store authentication.
        # This avoids logging in every time the application starts.
        self.client = TC(settings.SESSION_NAME, self.api_id, self.api_hash)

    async def _connect(self):
        """Ensures the client is connected before performing an operation."""
        if not self.client.is_connected():
            # This will use the .session file to login if it exists,
            # otherwise it will prompt for credentials on the console the first time.
            await self.client.connect()
            if not await self.client.is_user_authorized():
                # This part is for the very first run.
                # You will be asked for your phone number, password, and 2FA code on the console.
                print("First time login: Please enter your Telegram credentials when prompted.")
                await self.client.send_code_request(settings.PHONE_NUMBER) # You'd need to add PHONE_NUMBER to your .env
                # await self.client.sign_in(settings.PHONE_NUMBER, input('Enter code: '))

    async def disconnect(self):
        """Disconnects the client."""
        if self.client.is_connected():
            await self.client.disconnect()

    async def upload_chunk(self, chunk_data: bytes, caption: str) -> int:
        """
        Uploads a single file chunk to the storage channel and returns the message ID.
        """
        await self._connect()
        message = await self.client.send_file(
            self.channel_id,
            chunk_data,
            caption=caption,
            allow_cache=False,
            # The 'file_name' attribute can be helpful for Telegram clients
            attributes=[]
        )
        return message.id

    async def download_chunk(self, message_id: int) -> bytes:
        """
        Downloads a single file chunk from the storage channel by its message ID.
        """
        await self._connect()
        message = await self.client.get_messages(self.channel_id, ids=message_id)
        if message and message.media:
            # Download the media associated with the message into memory as bytes
            return await self.client.download_media(message, file=bytes)
        return b""

    async def delete_chunks(self, message_ids: list[int]) -> bool:
        """
        Deletes one or more file chunks from the storage channel.
        """
        await self._connect()
        await self.client.delete_messages(self.channel_id, message_ids)
        return True

# A single, shared instance of the Telegram client to be used across the application.
# The connection will be managed by the methods above.
telegram_client = TelegramClient()
