# Telegram Chat Organizer

This script automates the organization of your Telegram chats. It identifies chats based on a specific prefix in their title (e.g., "LOG") and moves them into a designated chat folder.

## Features

-   Automatically finds chats with a specific prefix.
-   Creates a chat folder if it doesn't exist.
-   Adds the identified chats to the specified folder.
-   Idempotent design: running the script multiple times won't create duplicate entries or cause errors.

## Prerequisites

-   Python 3.6+
-   A Telegram account.
-   `api_id` and `api_hash` from Telegram. You can get them from [my.telegram.org](https://my.telegram.org).

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure your credentials:**
    -   Rename the `settings.ini.example` to `settings.ini`.
    -   Open `settings.ini` and fill in your details:
        ```ini
        [telegram]
        api_id = YOUR_API_ID
        api_hash = YOUR_API_HASH
        phone_number = YOUR_PHONE_NUMBER
        ```
    > **Security Note:** Your `api_id` and `api_hash` are sensitive. Do not share them or commit the `settings.ini` file to version control. The provided `.gitignore` file already excludes it.

## Usage

1.  **Run the script:**
    ```bash
    python organizer_script.py
    ```
    The first time you run the script, you will be prompted to enter your phone number, a login code sent to your Telegram account, and your two-factor authentication password (if enabled). This will create a `chat_organizer_session.session` file that will be used for subsequent logins.

2.  **Customize the script (optional):**
    You can change the folder name and chat prefix by editing these lines in `organizer_script.py`:
    ```python
    FOLDER_NAME = 'LOG Channels'
    CHAT_PREFIX = 'LOG'
    ```

## Scheduling (for advanced users)

You can run this script automatically using `cron` on Linux or macOS.

1.  Open your crontab for editing:
    ```bash
    crontab -e
    ```

2.  Add the following line to run the script every hour:
    ```
    0 * * * * /usr/bin/python3 /path/to/your/project/organizer_script.py >> /path/to/your/project/cron.log 2>&1
    ```
    Make sure to replace `/path/to/your/project/` with the absolute path to the script's directory.

## How it Works

This script uses the [Telethon](https://github.com/LonamiWebs/Telethon) library to interact with the Telegram Client API. It authenticates as a user, iterates through all chats, and uses "Dialog Filters" (the API equivalent of Chat Folders) to organize them.
