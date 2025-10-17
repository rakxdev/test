# Sensor Monitor Application

A real-time sensor monitoring application built with Flask and Flask-SocketIO.

## Features

- Real-time sensor data monitoring (Temperature, Humidity, Pressure, Light)
- WebSocket-based live updates with room-based subscriptions
- Voltage-controlled simulation (0-10V) with realistic sensor behavior
- SQLite database for data persistence with thread-safe operations
- Advanced data simulator with Gaussian noise and drift
- RESTful API with validation and error handling
- Responsive web interface with mode-specific views

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
- **mode_status**: Current activation status, voltage settings, and timestamps for each mode

## Usage

1. Navigate to the **Home** page and select a sensor mode
2. Click "View Dashboard" to access the real-time dashboard
3. Click "Start Simulator" to begin generating sensor data
4. Toggle individual sensor modes on/off
5. Adjust voltage levels (0-10V) to control simulation behavior
6. View real-time updates as data streams in
7. Check the **Records** page for historical data

## API Endpoints

### Mode Management
- `GET /api/modes` - Get all modes
- `GET /api/modes/<mode_id>` - Get specific mode
- `POST /api/modes/<mode_id>/toggle` - Toggle mode status
- `POST /api/mode/toggle` - Toggle mode with body params

### Voltage Control
- `POST /api/voltage/set` - Set voltage for a mode (0-10V)

### Readings
- `GET /api/readings/<mode_id>` - Get recent readings
- `GET /api/current-reading/<mode_id>` - Get latest reading

### WebSocket Events
- `connect` / `disconnect` - Connection management
- `subscribe_mode` / `unsubscribe_mode` - Subscribe to mode updates
- `data_update` - Real-time reading updates
- `mode_changed` - Mode status changes
- `voltage_changed` - Voltage updates
- `error` - Error notifications

See [PHASE3_IMPLEMENTATION.md](PHASE3_IMPLEMENTATION.md) for detailed API documentation.

## Tech Stack

- Flask 3.0.0
- Flask-SocketIO 5.3.6
- SQLite3
- Eventlet for async support
- Vanilla JavaScript (no frameworks)
