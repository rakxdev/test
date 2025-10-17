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
- **Phase 4**: Mode-specific dashboards with control panels, digital readouts, and color-coded themes
- **Phase 4**: Real-time WebSocket integration with connection indicators
- **Phase 4**: Debounced voltage slider control (500ms) with visual feedback
- **Phase 5**: Real-time Chart.js scrolling visualization with multiple datasets
- **Phase 5**: Chart controls: pause/resume, clear, PNG export, time range selector
- **Phase 5**: 60-second scrolling window with auto-scaling and old data pruning

## Project Structure

```
.
├── app.py                      # Main Flask application with SocketIO
├── database.py                 # Database schema and operations
├── data_simulator.py           # Sensor data simulator
├── requirements.txt            # Python dependencies
├── static/
│   ├── css/
│   │   ├── style.css           # Global application styles
│   │   └── dashboard.css       # Mode dashboard styles (Phase 4, 5)
│   └── js/
│       ├── main.js             # Common utilities
│       ├── home.js             # Home page logic
│       ├── chart-handler.js    # Chart.js utilities (Phase 5)
│       └── dashboard.js        # Mode dashboard controller (Phase 4, 5)
└── templates/
    ├── base.html               # Base template
    ├── home.html               # Home page with mode selection
    ├── dashboard.html          # All-modes dashboard
    ├── mode-dashboard.html     # Mode-specific dashboard (Phase 4)
    └── records.html            # Historical records
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

### Getting Started
1. Navigate to the **Home** page and select a sensor mode
2. Click "View [Mode Name] Dashboard" to access a mode-specific dashboard (**Phase 4**)
3. Or click "View Dashboard" to see all modes at once

### Mode-Specific Dashboard (Phase 4 & 5)
1. **Power Control**: Toggle the mode on/off using the power switch
2. **Voltage Control**: Adjust voltage (0-10V) using the slider - changes are debounced (500ms)
3. **Monitor Metrics**: View real-time sensor readings, voltage, update rate, and data count
4. **Connection Status**: Check WebSocket connection and data stream indicators
5. **Theme**: Dashboard uses color-coded theme based on sensor type
6. **Real-Time Chart** (Phase 5): View scrolling visualization with three datasets (value, voltage, power)
7. **Chart Controls** (Phase 5): Pause/resume updates, clear data, export as PNG, adjust time window

### General Operations
1. Click "Start Simulator" to begin generating sensor data
2. Toggle individual sensor modes on/off
3. Adjust voltage levels (0-10V) to control simulation behavior
4. View real-time updates as data streams in
5. Check the **Records** page for historical data

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

See [PHASE3_IMPLEMENTATION.md](PHASE3_IMPLEMENTATION.md), [PHASE4_IMPLEMENTATION.md](PHASE4_IMPLEMENTATION.md), and [PHASE5_IMPLEMENTATION.md](PHASE5_IMPLEMENTATION.md) for detailed implementation documentation.

## Tech Stack

- Flask 3.0.0
- Flask-SocketIO 5.3.6
- SQLite3
- Eventlet for async support
- Vanilla JavaScript ES6 (no frameworks)
- Socket.IO client
- Chart.js 4.4.0 with date-fns adapter (Phase 5)
- CSS3 with Custom Properties
