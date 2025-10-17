import time
import random
import math
from datetime import datetime
import threading
from database import add_reading, get_active_modes, get_mode_by_id


class DataSimulator:
    """Simulates sensor data for active modes with voltage-based variation."""
    
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.running = False
        self.simulation_interval = 2
        self.lock = threading.Lock()
        self.base_values = {}
    
    def generate_value(self, mode_name, voltage=5.0):
        """Generate a simulated value based on mode type and voltage.
        
        Args:
            mode_name: Name of the sensor mode
            voltage: Voltage level (0-10V) affecting the reading range and variation
        
        Returns:
            Simulated sensor value
        """
        voltage_factor = voltage / 5.0
        noise = random.gauss(0, 0.5 * voltage_factor)
        
        if mode_name not in self.base_values:
            if mode_name == 'Temperature':
                self.base_values[mode_name] = 24.0
            elif mode_name == 'Humidity':
                self.base_values[mode_name] = 55.0
            elif mode_name == 'Pressure':
                self.base_values[mode_name] = 1013.0
            elif mode_name == 'Light':
                self.base_values[mode_name] = 500.0
            else:
                self.base_values[mode_name] = 50.0
        
        base = self.base_values[mode_name]
        drift = random.uniform(-0.3, 0.3) * voltage_factor
        self.base_values[mode_name] += drift
        
        if mode_name == 'Temperature':
            min_val, max_val = 15.0, 35.0
            value = base + noise * 2
        elif mode_name == 'Humidity':
            min_val, max_val = 20.0, 90.0
            value = base + noise * 3
        elif mode_name == 'Pressure':
            min_val, max_val = 980.0, 1040.0
            value = base + noise * 5
        elif mode_name == 'Light':
            min_val, max_val = 0.0, 1200.0
            value = base + noise * 20
        else:
            min_val, max_val = 0.0, 100.0
            value = base + noise * 5
        
        value = max(min_val, min(max_val, value))
        self.base_values[mode_name] = value
        
        return round(value, 2)
    
    def simulate_reading(self, mode):
        """Simulate a single reading for a mode with voltage consideration."""
        if mode.get('is_active'):
            voltage = mode.get('voltage', 5.0)
            
            with self.lock:
                value = self.generate_value(mode['name'], voltage)
            
            try:
                reading_id = add_reading(mode['id'], value)
                
                reading_data = {
                    'id': reading_id,
                    'mode_id': mode['id'],
                    'mode_name': mode['name'],
                    'icon': mode['icon'],
                    'value': value,
                    'voltage': voltage,
                    'timestamp': datetime.now().isoformat()
                }
                
                if self.socketio:
                    self.socketio.emit('new_reading', reading_data)
                    self.socketio.emit('data_update', reading_data)
                    self.socketio.emit('data_update', reading_data, room=f'mode_{mode["id"]}')
                
                return reading_data
            except Exception as e:
                error_data = {
                    'error': str(e),
                    'mode_id': mode['id'],
                    'mode_name': mode['name']
                }
                if self.socketio:
                    self.socketio.emit('error', error_data)
                    self.socketio.emit('error', error_data, room=f'mode_{mode["id"]}')
                print(f"Error simulating reading for {mode['name']}: {e}")
                return None
        return None
    
    def run(self):
        """Run the data simulator (blocking) with thread-safe operation."""
        with self.lock:
            if self.running:
                print("Data simulator already running")
                return
            self.running = True
        
        print("Data simulator started")
        
        try:
            while self.running:
                try:
                    modes = get_active_modes()
                    for mode in modes:
                        if not self.running:
                            break
                        self.simulate_reading(mode)
                    
                    time.sleep(self.simulation_interval)
                except Exception as e:
                    print(f"Error in simulator loop: {e}")
                    if self.socketio:
                        self.socketio.emit('error', {'error': str(e), 'source': 'simulator'})
                    time.sleep(self.simulation_interval)
        finally:
            with self.lock:
                self.running = False
            print("Data simulator stopped")
    
    def stop(self):
        """Stop the data simulator."""
        with self.lock:
            self.running = False
        print("Stopping data simulator...")
    
    def is_running(self):
        """Check if the simulator is currently running."""
        with self.lock:
            return self.running


if __name__ == '__main__':
    simulator = DataSimulator()
    try:
        simulator.run()
    except KeyboardInterrupt:
        simulator.stop()
        print("\nSimulation stopped by user")
