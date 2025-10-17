from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import eventlet
from database import (
    init_db, get_all_modes, get_mode_by_id, 
    update_mode_status, add_reading, get_recent_readings,
    get_all_readings
)
from data_simulator import DataSimulator

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

simulator = DataSimulator(socketio=socketio)
simulator_thread = None


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
    readings = get_all_readings(limit=1000)
    return render_template('records.html', readings=readings)


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


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('connection_response', {'data': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')


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
