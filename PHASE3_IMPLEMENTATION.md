# Phase 3 Implementation Summary

## Overview
This document describes the Phase 3 implementation of dashboard backend controls and real-time data plumbing with voltage-based simulation and enhanced subscription management.

## Changes Made

### 1. Database Enhancements (`database.py`)

#### Thread Safety
- Added `threading.RLock()` for database operations
- Updated `get_db_connection()` to use `check_same_thread=False` with lock protection
- Ensures safe concurrent access from multiple threads (simulator + web requests)

#### Schema Updates
- Added `voltage` column to `mode_status` table (default: 5.0V, range: 0-10V)
- Voltage affects simulation behavior and reading variation

#### New Database Functions
- `get_current_reading(mode_id)` - Get the most recent reading for a mode
- `set_mode_voltage(mode_id, voltage)` - Set voltage level for a mode with validation
- `get_mode_voltage(mode_id)` - Retrieve voltage setting for a mode
- `get_active_modes()` - Get all currently active modes (optimized for simulator)

#### Updated Functions
- `get_all_modes()` - Now includes `voltage` field
- `get_mode_by_id(mode_id)` - Now includes `voltage` field

### 2. Data Simulator Enhancements (`data_simulator.py`)

#### Thread Safety
- Added `threading.Lock()` for value generation
- Enhanced `run()` method with proper lock management
- Added `is_running()` method to check simulator state

#### Voltage-Based Simulation
- `generate_value()` now accepts `voltage` parameter (0-10V)
- Voltage affects:
  - Signal noise level (higher voltage = more variation)
  - Value drift rate (simulates realistic sensor behavior)
  - Reading range (scaled by voltage factor)
- Maintains base values per mode with realistic drift

#### Realistic Sensor Behavior
- Gaussian noise distribution for natural variation
- Continuous drift simulation (base value changes over time)
- Mode-specific ranges:
  - Temperature: 15.0°C - 35.0°C
  - Humidity: 20.0% - 90.0%
  - Pressure: 980.0 hPa - 1040.0 hPa
  - Light: 0.0 lux - 1200.0 lux

#### Enhanced Error Handling
- Try-catch blocks around database operations
- Error events emitted via SocketIO to both global and room-specific channels
- Graceful degradation on errors

#### WebSocket Events
- Emits `new_reading` (backward compatibility)
- Emits `data_update` (new event for Phase 3)
- Emits to mode-specific rooms: `mode_{mode_id}`
- Emits `error` events on failures

### 3. Flask API Routes (`app.py`)

#### New Routes

##### `/dashboard/<mode_id>` (GET)
- Mode-specific dashboard view
- Passes selected mode to template
- Returns 404 if mode not found

##### `/api/mode/toggle` (POST)
- Simplified toggle endpoint with request body
- Request body:
  ```json
  {
    "mode_id": 1,
    "enforce_single_active": false
  }
  ```
- Returns success status and updated mode information
- Emits both `mode_changed` and `mode_status_changed` events

##### `/api/voltage/set` (POST)
- Set voltage level for a mode
- Request body:
  ```json
  {
    "mode_id": 1,
    "voltage": 7.5
  }
  ```
- Validates voltage range (0-10V)
- Emits `voltage_changed` event
- Returns updated voltage setting

##### `/api/current-reading/<mode_id>` (GET)
- Get the most recent reading for a mode
- Returns full reading data with mode information
- Returns 404 if no readings available

#### Updated Routes
- `/api/modes/<int:mode_id>/toggle` - Still functional for backward compatibility

### 4. Flask-SocketIO Events (`app.py`)

#### Enhanced Connection Management

##### `connect` Event
- Initializes client subscription tracking
- Creates entry in `client_subscriptions` dictionary
- Returns connection confirmation with client ID
- Response:
  ```json
  {
    "status": "connected",
    "message": "Connected to server",
    "client_id": "<session_id>"
  }
  ```

##### `disconnect` Event
- Cleans up client subscriptions
- Leaves all subscribed rooms
- Removes client from subscription tracking

#### New Subscription Events

##### `subscribe_mode` Event
- Subscribe to updates for a specific mode
- Request:
  ```json
  {
    "mode_id": 1
  }
  ```
- Joins room `mode_{mode_id}`
- Tracks subscription in `client_subscriptions`
- Returns confirmation:
  ```json
  {
    "mode_id": 1,
    "mode_name": "Temperature",
    "room": "mode_1"
  }
  ```

##### `unsubscribe_mode` Event
- Unsubscribe from mode updates
- Request:
  ```json
  {
    "mode_id": 1
  }
  ```
- Leaves room `mode_{mode_id}`
- Updates subscription tracking

#### Emitted Events

##### `connection_response`
- Emitted on client connection
- Includes status and client ID

##### `data_update`
- Emitted for each new reading
- Sent to both global namespace and mode-specific room
- Includes full reading data with voltage

##### `mode_changed`
- Emitted when mode status changes
- Includes updated mode information

##### `error`
- Emitted on errors (database, validation, simulator)
- Sent to both global namespace and relevant rooms
- Includes error details and source

##### `voltage_changed`
- Emitted when voltage is updated
- Includes mode_id and new voltage value

##### `subscription_confirmed` / `unsubscription_confirmed`
- Emitted on successful subscription changes

### 5. Session Management

#### Client Subscription Tracking
- `client_subscriptions` dictionary tracks active subscriptions
- Key: client_id (session ID)
- Value: Set of subscribed mode_ids
- Automatic cleanup on disconnect

#### Room-Based Broadcasting
- Each mode has a dedicated room: `mode_{mode_id}`
- Clients can subscribe to specific modes for targeted updates
- Reduces unnecessary data transmission
- Supports scalable real-time updates

## API Usage Examples

### Toggle Mode with Single-Active Constraint
```bash
curl -X POST http://localhost:5000/api/mode/toggle \
  -H "Content-Type: application/json" \
  -d '{"mode_id": 1, "enforce_single_active": true}'
```

### Set Voltage
```bash
curl -X POST http://localhost:5000/api/voltage/set \
  -H "Content-Type: application/json" \
  -d '{"mode_id": 1, "voltage": 7.5}'
```

### Get Current Reading
```bash
curl http://localhost:5000/api/current-reading/1
```

### Get Mode-Specific Dashboard
```
http://localhost:5000/dashboard/1
```

## WebSocket Client Example

```javascript
const socket = io();

socket.on('connect', function() {
    console.log('Connected to server');
    
    // Subscribe to a specific mode
    socket.emit('subscribe_mode', {mode_id: 1});
});

socket.on('subscription_confirmed', function(data) {
    console.log('Subscribed to mode:', data.mode_name);
});

socket.on('data_update', function(data) {
    console.log('New reading:', data.value, 'at voltage:', data.voltage);
});

socket.on('error', function(data) {
    console.error('Error:', data.error);
});

socket.on('voltage_changed', function(data) {
    console.log('Voltage changed for mode', data.mode_id, 'to', data.voltage);
});
```

## Validation and Error Handling

### Voltage Validation
- Must be a number (int or float)
- Range: 0.0 - 10.0V
- Returns 400 Bad Request on invalid values

### Mode Validation
- All endpoints validate mode existence
- Return 404 Not Found for invalid mode_ids

### Request Validation
- Required fields checked before processing
- Returns 400 Bad Request for missing parameters
- Descriptive error messages in response

### Thread Safety
- Database operations protected by RLock
- Simulator state changes protected by Lock
- Safe concurrent access from multiple clients

## Testing

The implementation has been tested for:
- ✅ Database schema updates and migrations
- ✅ Thread-safe database operations
- ✅ Voltage setting and retrieval
- ✅ Current reading retrieval
- ✅ Python syntax validation
- ✅ Module imports and dependencies

## Performance Considerations

### Database Optimization
- Maintains existing indexes on readings table
- Efficient queries using JOIN operations
- Context manager ensures proper connection cleanup

### WebSocket Efficiency
- Room-based broadcasting reduces network traffic
- Clients only receive updates for subscribed modes
- Subscription tracking prevents memory leaks

### Simulator Performance
- Uses `get_active_modes()` instead of filtering all modes
- Thread-safe operation without blocking web requests
- Configurable simulation interval (default: 2 seconds)

## Backward Compatibility

All Phase 2 functionality is maintained:
- Original `/api/modes/<int:mode_id>/toggle` endpoint still works
- Existing `mode_status_changed` event still emitted
- `new_reading` event still emitted (in addition to `data_update`)
- Dashboard and home routes unchanged

## Database Migration

To migrate existing databases:
```bash
python database.py
```

The `init_db()` function uses `IF NOT EXISTS` clauses, so running it on existing databases is safe. The voltage column has a default value of 5.0V for backward compatibility.

## Future Enhancements

Potential improvements for future phases:
- Configurable voltage ranges per mode
- Historical voltage tracking
- Advanced simulation modes (sinusoidal, step, etc.)
- WebSocket authentication and authorization
- Rate limiting for API endpoints
- Metrics and monitoring endpoints
- Unit and integration tests
