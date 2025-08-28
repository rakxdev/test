from fastapi import FastAPI
from teledrive.backend.db.init_db import init_db
from teledrive.backend.db.session import SessionLocal

app = FastAPI(title="TeleDrive")

@app.post("/create-db-for-real")
def create_db_endpoint():
    """
    A temporary endpoint to create the database tables.
    This is a workaround for environment issues with alembic/scripts.
    """
    try:
        init_db()
        return {"message": "Database and tables created successfully."}
    except Exception as e:
        # Raise HTTP exception in a real app
        return {"message": "An error occurred creating the database.", "error": str(e)}

@app.get("/")
def read_root():
    return {"message": "Welcome to TeleDrive"}
