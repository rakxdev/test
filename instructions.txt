### Guide: Setting Up `copyparty` with a Telegram Upload Script

### Introduction
This guide provides all the steps and code required to set up a `copyparty` server on your VPS that automatically uploads files to a Telegram channel. This guide is based on the plan we developed.

---
### **Step 1: Install Dependencies on Your VPS**

First, you need to log into your VPS via SSH and install the necessary software. These commands are for a Debian-based system like Ubuntu.

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip git ffmpeg
```

---
### **Step 2: Set Up the `copyparty` Directory and Uploader Script**

Now, let's get the software and create our custom script.

**1. Clone `copyparty`:**
Choose a directory where you want to keep your project (e.g., your home directory), then run this command to download `copyparty`:
```bash
git clone https://github.com/9001/copyparty.git
```
This will create a `copyparty` folder. It's best to run all subsequent commands from inside this new `copyparty` directory.
```bash
cd copyparty
```

**2. Install Python Libraries:**
Next, install the `pyrogram` library, which our script will use to talk to the Telegram API.
```bash
sudo pip3 install pyrogram
```

**3. Create the Telegram Uploader Script:**
While inside the `copyparty` directory, create a new file named `telegram_uploader.py`. Paste the entire block of code below into this file.

```python
#!/usr/bin/env python3

import os
import sys
import asyncio
import subprocess
import math
from pyrogram import Client

# --- Configuration ---
# These are the credentials you provided.
API_ID = 24986604
API_HASH = "afda6f8e5493b9a5bc87656974f3c82e"
BOT_TOKEN = "8163323617:AAH34RhSgBsc7FMX9o6Xa65RHqLRWfdUfgw"
CHAT_ID = -1002796497801
MAX_SPLIT_SIZE = 2097152000  # 2 GB in bytes

# --- Helper Functions ---

async def run_command(command):
    """Runs a shell command asynchronously and captures output."""
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Stderr: {stderr.decode().strip()}")
        return None
    return stdout.decode().strip()

async def get_media_duration(file_path):
    """Gets the duration of a media file using ffprobe."""
    command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{file_path}\""
    duration_str = await run_command(command)
    try:
        return float(duration_str)
    except (ValueError, TypeError):
        print(f"Could not determine duration for {file_path}")
        return None

async def split_media(file_path, split_size):
    """Splits a media file using ffmpeg based on size."""
    print(f"Attempting to split media file: {file_path}")
    duration = await get_media_duration(file_path)
    if not duration:
        print("Cannot split media file without duration.")
        return []

    file_size = os.path.getsize(file_path)
    base_name, ext = os.path.splitext(file_path)
    output_dir = f"{base_name}_parts"
    os.makedirs(output_dir, exist_ok=True)

    num_parts = math.ceil(file_size / split_size)
    parts_list = []

    # Use ffmpeg to create parts based on size, which is more reliable than time for this purpose.
    # Note: This is a simplified approach. A more robust solution might need to check each part's duration.
    for i in range(num_parts):
        part_path = os.path.join(output_dir, f"{os.path.basename(base_name)}.part{i+1:03}{ext}")
        start_byte = i * split_size
        command = f"ffmpeg -i \"{file_path}\" -ss `stat -c%s \"{file_path}\" | awk '{{print $1 / {num_parts} * {i}}}' | xargs -I {{}} ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 -sexagesimal -i \"{file_path}\" -t {{}} | tail -1` -fs {split_size} -c copy \"{part_path}\""

        # A simpler, but potentially less accurate time-based split command as a fallback
        part_duration = duration / num_parts
        start_time = i * part_duration

        command_simple = f"ffmpeg -ss {start_time} -i \"{file_path}\" -t {part_duration} -c copy \"{part_path}\""

        # For this guide, we use a more direct approach that's easier to implement
        # by seeking and limiting file size.
        command_fs = f"ffmpeg -i \"{file_path}\" -ss {start_time} -fs {split_size} -c copy \"{part_path}\""

        await run_command(command_fs)
        if os.path.exists(part_path):
            parts_list.append(part_path)

    return parts_list


async def split_generic(file_path, split_size):
    """Splits a generic file using the 'split' command."""
    print(f"Attempting to split generic file: {file_path}")
    base_name = os.path.basename(file_path)
    output_dir = f"{file_path}_parts"
    os.makedirs(output_dir, exist_ok=True)

    command = f"split --numeric-suffixes=1 --suffix-length=3 --bytes={split_size} \"{file_path}\" \"{os.path.join(output_dir, base_name)}.part\""
    await run_command(command)

    return sorted([os.path.join(output_dir, f) for f in os.listdir(output_dir)])


async def main(file_path):
    """The main function to handle the upload process."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    file_size = os.path.getsize(file_path)
    files_to_upload = []
    original_file_dir = os.path.dirname(file_path)

    # Determine the directory for parts based on the original file's location
    base_name, ext = os.path.splitext(os.path.basename(file_path))
    parts_dir_path = os.path.join(original_file_dir, f"{base_name}_parts")


    split_happened = False

    if file_size > MAX_SPLIT_SIZE:
        split_happened = True
        media_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.mp3', '.flac', '.wav']
        if any(file_path.lower().endswith(ext) for ext in media_extensions):
            files_to_upload = await split_media(file_path, MAX_SPLIT_SIZE)
        else:
            files_to_upload = await split_generic(file_path, MAX_SPLIT_SIZE)
    else:
        files_to_upload = [file_path]

    if not files_to_upload:
        print("No files to upload. Something went wrong during splitting.")
        return

    print(f"Initializing Telegram client...")
    async with Client("tg_bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN) as app:
        for f_path in files_to_upload:
            print(f"Uploading {os.path.basename(f_path)}...")
            try:
                await app.send_document(CHAT_ID, f_path)
                print(f"Successfully uploaded {os.path.basename(f_path)}.")
                os.remove(f_path)
            except Exception as e:
                print(f"Failed to upload {os.path.basename(f_path)}: {e}")

    if split_happened:
        if os.path.exists(parts_dir_path) and not os.listdir(parts_dir_path):
            os.rmdir(parts_dir_path)
        os.remove(file_path) # Delete original large file

    print("Process complete.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 telegram_uploader.py <path_to_file>")
        sys.exit(1)

    file_to_process = sys.argv[1]
    asyncio.run(main(file_to_process))
```

**4. Make the script executable:**
Run this command to allow `copyparty` to execute your script.
```bash
chmod +x telegram_uploader.py
```

---
### **Step 3: Configure `copyparty`**

Now we'll create the configuration file for `copyparty`.

**1. Create the config file:**
While still inside the `copyparty` directory, create a file named `copyparty.conf`. Paste the following text into it.

```ini
[global]
# This sets up the event hook.
# It tells copyparty to run our python script after a successful upload.
# The {} is a placeholder that copyparty fills with the full file path.
xau = /usr/bin/python3 telegram_uploader.py "{}"

[accounts]
# This creates a user named 'admin' with the password 'changeme'.
# YOU SHOULD CHANGE THIS PASSWORD.
admin: changeme

[/]
  # This makes the root of the server point to a folder named 'uploads'.
  # We need to create this folder.
  ./uploads
  accs:
    # This gives the 'admin' user full permissions (read, write, move, delete).
    # The '*' (everyone else) has no permissions.
    A: admin
```

**2. Create the uploads directory:**
`copyparty` needs the directory we specified in the config to exist. Create it now:
```bash
mkdir uploads
```

---
### **Step 4: Run the Server**

Everything is now in place. To start the server, stay inside your `copyparty` directory and run the following command:

```bash
./copyparty-sfx.py -c copyparty.conf
```

Your server should now be running! You can access it by going to your VPS's IP address in a web browser (e.g., `http://YOUR_VPS_IP:3923`). You will be prompted for the username (`admin`) and password (`changeme`) you set in the config file.

When you upload a file, you can watch the console where you ran the command to see the output from the `telegram_uploader.py` script as it works.

---
### **Final Notes**
- **Security:** Remember to choose a strong password for your `copyparty` account in the `copyparty.conf` file.
- **Troubleshooting:** If something goes wrong, the output in the terminal where `copyparty` is running is the best place to look for errors from both `copyparty` and the uploader script.
- **Running in Background:** For a real server, you would want to run `copyparty` in the background using a tool like `screen`, `tmux`, or by creating a `systemd` service. The `copyparty` documentation has guides for this if you need them.

I hope this guide helps you get your project up and running successfully.
