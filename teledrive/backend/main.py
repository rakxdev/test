from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="TeleDrive")

# This assumes the server is run from the project root, where the `teledrive` dir is.
FRONTEND_DIR = "teledrive/frontend"

# Mount the static directory to serve CSS, JS, etc.
# The path "/static" is arbitrary, but we need to make sure the HTML references it if needed.
# Since the HTML uses relative paths ("style.css"), a more direct mounting is better.
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

@app.get("/")
async def read_index():
    """
    Serves the main index.html file.
    """
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))

# Add a catch-all for any other path to serve the index.html, useful for client-side routing
@app.get("/{catchall:path}")
async def read_index_catchall(catchall: str):
    # This helps with page reloads on routes managed by a frontend framework
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))
