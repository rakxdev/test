import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'app.db')


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database with schema and seed data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create modes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                icon TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create readings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode_id INTEGER NOT NULL,
                value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mode_id) REFERENCES modes (id)
            )
        ''')
        
        # Create mode_status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mode_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode_id INTEGER NOT NULL UNIQUE,
                is_active BOOLEAN DEFAULT 0,
                last_activated TIMESTAMP,
                last_deactivated TIMESTAMP,
                FOREIGN KEY (mode_id) REFERENCES modes (id)
            )
        ''')
        
        # Create index on readings timestamp for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_readings_timestamp 
            ON readings(timestamp)
        ''')
        
        # Create index on readings mode_id
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_readings_mode_id 
            ON readings(mode_id)
        ''')
        
        # Seed initial mode metadata
        seed_modes(cursor)
        
        conn.commit()


def seed_modes(cursor):
    """Seed initial mode metadata."""
    modes = [
        ('Temperature', 'Monitor temperature readings', '🌡️'),
        ('Humidity', 'Monitor humidity levels', '💧'),
        ('Pressure', 'Monitor atmospheric pressure', '🔽'),
        ('Light', 'Monitor light intensity', '💡'),
    ]
    
    for name, description, icon in modes:
        cursor.execute(
            'SELECT id FROM modes WHERE name = ?',
            (name,)
        )
        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO modes (name, description, icon) VALUES (?, ?, ?)',
                (name, description, icon)
            )
            mode_id = cursor.lastrowid
            cursor.execute(
                'INSERT INTO mode_status (mode_id, is_active) VALUES (?, ?)',
                (mode_id, 0)
            )


def get_all_modes():
    """Get all modes with their status."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.*, ms.is_active, ms.last_activated, ms.last_deactivated
            FROM modes m
            LEFT JOIN mode_status ms ON m.id = ms.mode_id
            ORDER BY m.id
        ''')
        return [dict(row) for row in cursor.fetchall()]


def get_mode_by_id(mode_id):
    """Get a specific mode by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.*, ms.is_active, ms.last_activated, ms.last_deactivated
            FROM modes m
            LEFT JOIN mode_status ms ON m.id = ms.mode_id
            WHERE m.id = ?
        ''', (mode_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_mode_status(mode_id, is_active):
    """Update the status of a mode."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        if is_active:
            cursor.execute('''
                UPDATE mode_status 
                SET is_active = 1, last_activated = ?
                WHERE mode_id = ?
            ''', (timestamp, mode_id))
        else:
            cursor.execute('''
                UPDATE mode_status 
                SET is_active = 0, last_deactivated = ?
                WHERE mode_id = ?
            ''', (timestamp, mode_id))


def add_reading(mode_id, value):
    """Add a new reading for a mode."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO readings (mode_id, value) VALUES (?, ?)',
            (mode_id, value)
        )
        return cursor.lastrowid


def get_recent_readings(mode_id, limit=100):
    """Get recent readings for a specific mode."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM readings
            WHERE mode_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (mode_id, limit))
        return [dict(row) for row in cursor.fetchall()]


def get_all_readings(limit=1000):
    """Get all readings across all modes."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, m.name as mode_name, m.icon
            FROM readings r
            JOIN modes m ON r.mode_id = m.id
            ORDER BY r.timestamp DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]


if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
