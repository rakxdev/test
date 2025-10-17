from flask import Flask, render_template, jsonify, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import eventlet
from database import (
    init_db, get_all_modes, get_mode_by_id, 
    update_mode_status, add_reading, get_recent_readings,
    get_all_readings, get_current_reading, set_mode_voltage,
    get_mode_voltage, get_filtered_records, get_statistics
)
from data_simulator import DataSimulator

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', manage_session=False)

simulator = DataSimulator(socketio=socketio)
simulator_thread = None

client_subscriptions = {}


def init_app():
    """Initialize the application."""
    init_db()


@app.route('/')
def home():
    """Home page route."""
    modes = get_all_modes()
    return render_template('home.html', modes=modes)


@app.route('/dashboard')
def dashboard():
    """Dashboard page route."""
    modes = get_all_modes()
    return render_template('dashboard.html', modes=modes)


@app.route('/records')
def records():
    """Records page route."""
    modes = get_all_modes()
    return render_template('records.html', modes=modes)


@app.route('/api/modes')
def api_get_modes():
    """API endpoint to get all modes."""
    modes = get_all_modes()
    return jsonify(modes)


@app.route('/api/modes/<int:mode_id>')
def api_get_mode(mode_id):
    """API endpoint to get a specific mode."""
    mode = get_mode_by_id(mode_id)
    if mode:
        return jsonify(mode)
    return jsonify({'error': 'Mode not found'}), 404


@app.route('/api/modes/<int:mode_id>/toggle', methods=['POST'])
def api_toggle_mode(mode_id):
    """API endpoint to toggle mode status."""
    mode = get_mode_by_id(mode_id)
    if not mode:
        return jsonify({'error': 'Mode not found'}), 404
    
    data = request.get_json() or {}
    enforce_single = data.get('enforce_single_active', False)
    new_status = not mode['is_active']
    
    update_mode_status(mode_id, new_status, enforce_single_active=enforce_single)
    
    updated_modes = get_all_modes()
    socketio.emit('mode_status_changed', {
        'mode_id': mode_id,
        'is_active': new_status,
        'all_modes': updated_modes
    })
    
    return jsonify({'mode_id': mode_id, 'is_active': new_status, 'all_modes': updated_modes})


@app.route('/api/readings/<int:mode_id>')
def api_get_readings(mode_id):
    """API endpoint to get readings for a mode."""
    limit = request.args.get('limit', 100, type=int)
    readings = get_recent_readings(mode_id, limit)
    return jsonify(readings)


@app.route('/dashboard/<int:mode_id>')
def dashboard_mode(mode_id):
    """Dashboard page route for a specific mode."""
    mode = get_mode_by_id(mode_id)
    if not mode:
        return render_template('error.html', message='Mode not found'), 404
    
    modes = get_all_modes()
    return render_template('mode-dashboard.html', modes=modes, selected_mode=mode)


@app.route('/api/mode/toggle', methods=['POST'])
def api_toggle_mode_simple():
    """Simplified API endpoint to toggle mode status."""
    data = request.get_json()
    
    if not data or 'mode_id' not in data:
        return jsonify({'error': 'mode_id is required'}), 400
    
    mode_id = data['mode_id']
    mode = get_mode_by_id(mode_id)
    
    if not mode:
        return jsonify({'error': 'Mode not found'}), 404
    
    enforce_single = data.get('enforce_single_active', False)
    new_status = not mode['is_active']
    
    try:
        update_mode_status(mode_id, new_status, enforce_single_active=enforce_single)
        
        updated_modes = get_all_modes()
        socketio.emit('mode_changed', {
            'mode_id': mode_id,
            'is_active': new_status,
            'all_modes': updated_modes
        })
        
        socketio.emit('mode_status_changed', {
            'mode_id': mode_id,
            'is_active': new_status,
            'all_modes': updated_modes
        })
        
        return jsonify({
            'success': True,
            'mode_id': mode_id,
            'is_active': new_status,
            'all_modes': updated_modes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/voltage/set', methods=['POST'])
def api_set_voltage():
    """API endpoint to set voltage for a mode."""
    data = request.get_json()
    
    if not data or 'mode_id' not in data or 'voltage' not in data:
        return jsonify({'error': 'mode_id and voltage are required'}), 400
    
    mode_id = data['mode_id']
    voltage = data['voltage']
    
    mode = get_mode_by_id(mode_id)
    if not mode:
        return jsonify({'error': 'Mode not found'}), 404
    
    try:
        voltage_value = float(voltage)
        set_mode_voltage(mode_id, voltage_value)
        
        socketio.emit('voltage_changed', {
            'mode_id': mode_id,
            'voltage': voltage_value
        })
        
        return jsonify({
            'success': True,
            'mode_id': mode_id,
            'voltage': voltage_value
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/current-reading/<int:mode_id>')
def api_get_current_reading(mode_id):
    """API endpoint to get the current/latest reading for a mode."""
    mode = get_mode_by_id(mode_id)
    if not mode:
        return jsonify({'error': 'Mode not found'}), 404
    
    reading = get_current_reading(mode_id)
    if reading:
        return jsonify(reading)
    
    return jsonify({
        'mode_id': mode_id,
        'mode_name': mode['name'],
        'message': 'No readings available yet'
    }), 404


@app.route('/api/records')
def api_get_records():
    """API endpoint to get filtered and paginated records."""
    try:
        mode_id = request.args.get('mode_id', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        min_value = request.args.get('min_value', type=float)
        max_value = request.args.get('max_value', type=float)
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        aggregation = request.args.get('aggregation', 'raw')
        
        if limit < 1 or limit > 10000:
            return jsonify({'error': 'Limit must be between 1 and 10000'}), 400
        
        if offset < 0:
            return jsonify({'error': 'Offset must be non-negative'}), 400
        
        if mode_id is not None:
            mode = get_mode_by_id(mode_id)
            if not mode:
                return jsonify({'error': f'Mode {mode_id} not found'}), 404
        
        if aggregation not in ['raw', '1min', '5min', '15min', '60min']:
            return jsonify({'error': 'Invalid aggregation interval. Must be one of: raw, 1min, 5min, 15min, 60min'}), 400
        
        if start_time and end_time and start_time > end_time:
            return jsonify({'error': 'start_time must be before end_time'}), 400
        
        if min_value is not None and max_value is not None and min_value > max_value:
            return jsonify({'error': 'min_value must be less than or equal to max_value'}), 400
        
        records = get_filtered_records(
            mode_id=mode_id,
            start_time=start_time,
            end_time=end_time,
            min_value=min_value,
            max_value=max_value,
            limit=limit,
            offset=offset,
            aggregation=aggregation
        )
        
        return jsonify({
            'records': records,
            'count': len(records),
            'limit': limit,
            'offset': offset,
            'filters': {
                'mode_id': mode_id,
                'start_time': start_time,
                'end_time': end_time,
                'min_value': min_value,
                'max_value': max_value,
                'aggregation': aggregation
            }
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/api/statistics')
def api_get_statistics():
    """API endpoint to get statistics for readings."""
    try:
        mode_id = request.args.get('mode_id', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        min_value = request.args.get('min_value', type=float)
        max_value = request.args.get('max_value', type=float)
        
        if mode_id is not None:
            mode = get_mode_by_id(mode_id)
            if not mode:
                return jsonify({'error': f'Mode {mode_id} not found'}), 404
        
        if start_time and end_time and start_time > end_time:
            return jsonify({'error': 'start_time must be before end_time'}), 400
        
        if min_value is not None and max_value is not None and min_value > max_value:
            return jsonify({'error': 'min_value must be less than or equal to max_value'}), 400
        
        statistics = get_statistics(
            mode_id=mode_id,
            start_time=start_time,
            end_time=end_time,
            min_value=min_value,
            max_value=max_value
        )
        
        return jsonify({
            'statistics': statistics,
            'filters': {
                'mode_id': mode_id,
                'start_time': start_time,
                'end_time': end_time,
                'min_value': min_value,
                'max_value': max_value
            }
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@socketio.on('connect')
def handle_connect():
    """Handle client connection with session initialization."""
    from flask_socketio import request as socketio_request
    client_id = socketio_request.sid
    client_subscriptions[client_id] = set()
    print(f'Client connected: {client_id}')
    emit('connection_response', {
        'status': 'connected',
        'message': 'Connected to server',
        'client_id': client_id
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection and cleanup subscriptions."""
    from flask_socketio import request as socketio_request
    client_id = socketio_request.sid
    
    if client_id in client_subscriptions:
        for mode_id in client_subscriptions[client_id]:
            leave_room(f'mode_{mode_id}')
        del client_subscriptions[client_id]
    
    print(f'Client disconnected: {client_id}')


@socketio.on('subscribe_mode')
def handle_subscribe_mode(data):
    """Handle client subscription to a specific mode."""
    from flask_socketio import request as socketio_request
    client_id = socketio_request.sid
    
    if not data or 'mode_id' not in data:
        emit('error', {'error': 'mode_id is required for subscription'})
        return
    
    mode_id = data['mode_id']
    mode = get_mode_by_id(mode_id)
    
    if not mode:
        emit('error', {'error': f'Mode {mode_id} not found'})
        return
    
    room = f'mode_{mode_id}'
    join_room(room)
    
    if client_id not in client_subscriptions:
        client_subscriptions[client_id] = set()
    client_subscriptions[client_id].add(mode_id)
    
    emit('subscription_confirmed', {
        'mode_id': mode_id,
        'mode_name': mode['name'],
        'room': room
    })
    
    print(f'Client {client_id} subscribed to mode {mode_id}')


@socketio.on('unsubscribe_mode')
def handle_unsubscribe_mode(data):
    """Handle client unsubscription from a specific mode."""
    from flask_socketio import request as socketio_request
    client_id = socketio_request.sid
    
    if not data or 'mode_id' not in data:
        emit('error', {'error': 'mode_id is required for unsubscription'})
        return
    
    mode_id = data['mode_id']
    room = f'mode_{mode_id}'
    leave_room(room)
    
    if client_id in client_subscriptions:
        client_subscriptions[client_id].discard(mode_id)
    
    emit('unsubscription_confirmed', {'mode_id': mode_id})
    print(f'Client {client_id} unsubscribed from mode {mode_id}')


@socketio.on('start_simulator')
def handle_start_simulator():
    """Start the data simulator."""
    global simulator_thread
    if simulator_thread is None or not simulator_thread.is_alive():
        simulator_thread = eventlet.spawn(simulator.run)
        emit('simulator_status', {'running': True}, broadcast=True)


@socketio.on('stop_simulator')
def handle_stop_simulator():
    """Stop the data simulator."""
    simulator.stop()
    emit('simulator_status', {'running': False}, broadcast=True)


if __name__ == '__main__':
    init_app()
    print("Starting Flask-SocketIO server...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
