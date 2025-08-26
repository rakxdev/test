import asyncio
import configparser
import logging
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogFiltersRequest, UpdateDialogFilterRequest
from telethon.tl.types import DialogFilter
from telethon.utils import get_input_peer

# --- Configuration ---
# Set up basic logging to see the script's progress
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from an external file for security
config = configparser.ConfigParser()
config.read('settings.ini')

# Telegram API credentials and session info
API_ID = config.getint('telegram', 'api_id')
API_HASH = config.get('telegram', 'api_hash')
SESSION_NAME = 'chat_organizer_session'

# User-defined folder and chat prefix settings
FOLDER_NAME = 'LOG Channels'
CHAT_PREFIX = 'LOG'
# A unique ID for the folder. If the folder doesn't exist, it will be created with this ID.
# Choose a number that is unlikely to conflict with existing folders (e.g., > 100).
FOLDER_ID = 101

# --- Core Functions ---

async def get_target_chats(client, prefix):
    """
    Iterates through all dialogs and returns a list of chat entities
    whose names start with the given prefix.
    """
    logging.info(f"Scanning for all chats starting with prefix: '{prefix}'")
    target_chats = []
    async for dialog in client.iter_dialogs():
        if dialog.name and dialog.name.startswith(prefix):
            target_chats.append(dialog.entity)
    logging.info(f"Found {len(target_chats)} chats matching the prefix.")
    return target_chats

async def get_or_create_folder(client, folder_name, folder_id):
    """
    Fetches the existing folder by name or returns None if it doesn't exist.
    """
    logging.info("Fetching existing chat folders (Dialog Filters)...")
    all_filters = await client(GetDialogFiltersRequest())

    for f in all_filters.filters:
        if isinstance(f, DialogFilter) and f.title == folder_name:
            logging.info(f"Found existing folder '{folder_name}' with ID {f.id}.")
            return f

    logging.info(f"Folder '{folder_name}' not found. It will be created with ID {folder_id}.")
    return None


async def update_folder_state(client, folder_id, folder_name, desired_peers):
    """
    Creates or updates the specified folder with the provided list of peers.
    """
    logging.info(f"Preparing to update folder '{folder_name}' (ID: {folder_id}).")

    # Construct the DialogFilter object. This object defines the folder's properties.
    # We are only setting the title and the included peers.
    new_filter = DialogFilter(
        id=folder_id,
        title=folder_name,
        pinned_peers=[],
        include_peers=desired_peers,
        exclude_peers=[]
    )

    try:
        await client(UpdateDialogFilterRequest(id=folder_id, filter=new_filter))
        logging.info(f"Successfully updated folder '{folder_name}'. It now contains {len(desired_peers)} chats.")
    except Exception as e:
        logging.error(f"Failed to update folder: {e}")

# --- Main Execution Block ---

async def main():
    """
    The main orchestration function for the script.
    """
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        logging.info("Client connected successfully.")

        # Step 1: Find all chats that should be in the folder.
        target_chats = await get_target_chats(client, CHAT_PREFIX)

        # Step 2: Convert chat entities to InputPeer objects.
        # The API requires InputPeer types for folder manipulation.
        desired_input_peers = [get_input_peer(c) for c in target_chats]

        # Step 3: Get the current state of the folder.
        existing_folder = await get_or_create_folder(client, FOLDER_NAME, FOLDER_ID)

        # Step 4: Compare current state with desired state to determine if an update is needed.
        # This is the core of the idempotent logic.

        # Create sets of peer IDs for easy comparison.
        # The logic to extract IDs is the same for both current and desired peers.
        def get_peer_id(peer):
            if hasattr(peer, 'channel_id'):
                return peer.channel_id
            if hasattr(peer, 'chat_id'):
                return peer.chat_id
            if hasattr(peer, 'user_id'):
                return peer.user_id
            return None

        desired_peer_ids = {get_peer_id(p) for p in desired_input_peers}
        current_peer_ids = set()

        folder_id_to_use = FOLDER_ID
        if existing_folder:
            folder_id_to_use = existing_folder.id
            current_peer_ids = {get_peer_id(p) for p in existing_folder.include_peers}

        if desired_peer_ids == current_peer_ids:
            logging.info("Folder is already up-to-date. No changes needed.")
        else:
            logging.info("Folder state has changed. Proceeding with update.")
            # Step 5: If they differ, send the update request with the complete desired list.
            await update_folder_state(client, folder_id_to_use, FOLDER_NAME, desired_input_peers)

if __name__ == "__main__":
    asyncio.run(main())
