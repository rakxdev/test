TeleDrive Setup Instructions

**IMPORTANT**: This project could not be tested due to a faulty execution environment. These are the steps to run it on your own machine.

---
1. PREREQUISITES:
   - Python 3.9+
   - A Telegram account and your API_ID / API_HASH from my.telegram.org

---
2. SETUP TELEGRAM CHANNEL:
   - Create a new, private Telegram channel.
   - Forward a message from the channel to a bot like @userinfobot to get the channel's ID (e.g., -1001234567890).

---
3. SETUP PROJECT:
   - Create and activate a Python virtual environment:
     python -m venv venv
     source venv/bin/activate

   - Install dependencies:
     pip install -r teledrive/requirements.txt

   - Create your .env file:
     - Go into the `teledrive/` directory.
     - Copy `.env.example` to a new file named `.env`.
     - Edit `.env` and fill in your credentials: API_ID, API_HASH, PHONE_NUMBER, CHANNEL_ID.

---
4. CREATE DATABASE:
   - From the project root directory, run:
     python -m teledrive.backend.db.init_db

---
5. RUN THE SERVER:
   - From the project root directory, run:
     uvicorn teledrive.backend.main:app --host 0.0.0.0 --port 8000

   - FIRST TIME ONLY: Watch the console. You will be prompted to enter your phone number, password, and 2FA code to log in to Telegram. This creates a session file for future runs.

---
6. ACCESS THE APP:
   - Open http://localhost:8000 in your browser.
