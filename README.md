# Sensor Monitor Application

A real-time sensor monitoring application built with Flask and Flask-SocketIO.

## Features

- Real-time sensor data monitoring (Temperature, Humidity, Pressure, Light)
- WebSocket-based live updates
- SQLite database for data persistence
- Data simulator for testing
- Responsive web interface

## Project Structure

```
.
├── app.py              # Main Flask application with SocketIO
├── database.py         # Database schema and operations
├── data_simulator.py   # Sensor data simulator
├── requirements.txt    # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css   # Application styles
│   └── js/
│       └── main.js     # Client-side JavaScript
└── templates/
    ├── base.html       # Base template
    ├── home.html       # Home page
    ├── dashboard.html  # Real-time dashboard
    └── records.html    # Historical records
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database:
```bash
python database.py
```

3. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Database Schema

### Tables

- **modes**: Sensor mode definitions (Temperature, Humidity, Pressure, Light)
- **readings**: Sensor reading values with timestamps
- **mode_status**: Current activation status of each mode

## Usage

1. Navigate to the **Dashboard** page
2. Click "Start Simulator" to begin generating sensor data
3. Toggle individual sensor modes on/off
4. View real-time updates as data streams in
5. Check the **Records** page for historical data

## Tech Stack

- Flask 3.0.0
- Flask-SocketIO 5.3.6
- SQLite3
- Eventlet for async support
- Vanilla JavaScript (no frameworks)
