import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager
import threading

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'app.db')
db_lock = threading.RLock()


@contextmanager
def get_db_connection():
    """Context manager for database connections with thread safety."""
    with db_lock:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
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
                voltage REAL DEFAULT 5.0,
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
        
        # Create composite index for efficient filtered queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_readings_mode_timestamp 
            ON readings(mode_id, timestamp)
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
            SELECT m.*, ms.is_active, ms.voltage, ms.last_activated, ms.last_deactivated
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
            SELECT m.*, ms.is_active, ms.voltage, ms.last_activated, ms.last_deactivated
            FROM modes m
            LEFT JOIN mode_status ms ON m.id = ms.mode_id
            WHERE m.id = ?
        ''', (mode_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_mode_status(mode_id, is_active, enforce_single_active=False):
    """Update the status of a mode."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        if is_active:
            if enforce_single_active:
                cursor.execute('''
                    UPDATE mode_status 
                    SET is_active = 0, last_deactivated = ?
                    WHERE mode_id != ?
                ''', (timestamp, mode_id))
            
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


def get_current_reading(mode_id):
    """Get the most recent reading for a specific mode."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, m.name as mode_name, m.icon, m.description
            FROM readings r
            JOIN modes m ON r.mode_id = m.id
            WHERE r.mode_id = ?
            ORDER BY r.timestamp DESC
            LIMIT 1
        ''', (mode_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def set_mode_voltage(mode_id, voltage):
    """Set the voltage for a specific mode."""
    if not isinstance(voltage, (int, float)) or voltage < 0 or voltage > 10:
        raise ValueError("Voltage must be a number between 0 and 10")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE mode_status 
            SET voltage = ?
            WHERE mode_id = ?
        ''', (voltage, mode_id))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Mode with ID {mode_id} not found")
        
        return True


def get_mode_voltage(mode_id):
    """Get the voltage setting for a specific mode."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT voltage FROM mode_status WHERE mode_id = ?
        ''', (mode_id,))
        row = cursor.fetchone()
        return row['voltage'] if row else None


def get_active_modes():
    """Get all currently active modes."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.*, ms.is_active, ms.voltage, ms.last_activated, ms.last_deactivated
            FROM modes m
            JOIN mode_status ms ON m.id = ms.mode_id
            WHERE ms.is_active = 1
            ORDER BY m.id
        ''')
        return [dict(row) for row in cursor.fetchall()]


def get_filtered_records(mode_id=None, start_time=None, end_time=None, 
                        min_value=None, max_value=None, limit=100, offset=0,
                        aggregation=None):
    """
    Get filtered and optionally aggregated records with pagination.
    
    Args:
        mode_id: Filter by mode ID
        start_time: Filter by start datetime (ISO format string)
        end_time: Filter by end datetime (ISO format string)
        min_value: Filter by minimum value
        max_value: Filter by maximum value
        limit: Maximum number of records to return
        offset: Number of records to skip
        aggregation: Aggregation interval ('raw', '1min', '5min', '15min', '60min')
    
    Returns:
        List of dictionaries containing reading data
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        params = []
        where_clauses = []
        
        if aggregation and aggregation != 'raw':
            interval_map = {
                '1min': 60,
                '5min': 300,
                '15min': 900,
                '60min': 3600
            }
            
            if aggregation not in interval_map:
                raise ValueError(f"Invalid aggregation interval: {aggregation}")
            
            interval_seconds = interval_map[aggregation]
            
            query = '''
                SELECT 
                    r.mode_id,
                    m.name as mode_name,
                    m.icon,
                    AVG(r.value) as value,
                    MIN(r.value) as min_value,
                    MAX(r.value) as max_value,
                    COUNT(r.id) as count,
                    datetime((strftime('%s', r.timestamp) / ?) * ?, 'unixepoch') as timestamp
                FROM readings r
                JOIN modes m ON r.mode_id = m.id
            '''
            params.extend([interval_seconds, interval_seconds])
        else:
            query = '''
                SELECT 
                    r.id,
                    r.mode_id,
                    m.name as mode_name,
                    m.icon,
                    r.value,
                    r.timestamp
                FROM readings r
                JOIN modes m ON r.mode_id = m.id
            '''
        
        if mode_id is not None:
            where_clauses.append('r.mode_id = ?')
            params.append(mode_id)
        
        if start_time:
            where_clauses.append('r.timestamp >= ?')
            params.append(start_time)
        
        if end_time:
            where_clauses.append('r.timestamp <= ?')
            params.append(end_time)
        
        if min_value is not None:
            where_clauses.append('r.value >= ?')
            params.append(min_value)
        
        if max_value is not None:
            where_clauses.append('r.value <= ?')
            params.append(max_value)
        
        if where_clauses:
            query += ' WHERE ' + ' AND '.join(where_clauses)
        
        if aggregation and aggregation != 'raw':
            query += ' GROUP BY r.mode_id, datetime((strftime(\'%s\', r.timestamp) / ?) * ?)'
            params.extend([interval_seconds, interval_seconds])
        
        query += ' ORDER BY r.timestamp DESC'
        query += ' LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_statistics(mode_id=None, start_time=None, end_time=None, 
                   min_value=None, max_value=None):
    """
    Calculate statistics for readings with optional filtering.
    
    Args:
        mode_id: Filter by mode ID
        start_time: Filter by start datetime (ISO format string)
        end_time: Filter by end datetime (ISO format string)
        min_value: Filter by minimum value
        max_value: Filter by maximum value
    
    Returns:
        Dictionary containing statistics (min, max, avg, count) per mode
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        params = []
        where_clauses = []
        
        query = '''
            SELECT 
                r.mode_id,
                m.name as mode_name,
                m.icon,
                COUNT(r.id) as count,
                AVG(r.value) as average,
                MIN(r.value) as minimum,
                MAX(r.value) as maximum,
                MIN(r.timestamp) as first_reading,
                MAX(r.timestamp) as last_reading
            FROM readings r
            JOIN modes m ON r.mode_id = m.id
        '''
        
        if mode_id is not None:
            where_clauses.append('r.mode_id = ?')
            params.append(mode_id)
        
        if start_time:
            where_clauses.append('r.timestamp >= ?')
            params.append(start_time)
        
        if end_time:
            where_clauses.append('r.timestamp <= ?')
            params.append(end_time)
        
        if min_value is not None:
            where_clauses.append('r.value >= ?')
            params.append(min_value)
        
        if max_value is not None:
            where_clauses.append('r.value <= ?')
            params.append(max_value)
        
        if where_clauses:
            query += ' WHERE ' + ' AND '.join(where_clauses)
        
        query += ' GROUP BY r.mode_id, m.name, m.icon'
        query += ' ORDER BY r.mode_id'
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        if mode_id is not None:
            return results[0] if results else None
        
        return results


if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
