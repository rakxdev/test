from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="TeleDrive")

# This serves the main HTML file from the root URL
@app.get("/")
async def read_index():
    return FileResponse('teledrive/frontend/index.html')

# This mounts the entire frontend directory at the root.
# It will automatically handle requests for /style.css, /script.js, etc.
# This must be mounted AFTER the specific root path to avoid conflicts.
app.mount("/", StaticFiles(directory="teledrive/frontend"), name="static")
