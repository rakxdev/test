import time
import random
from datetime import datetime
from database import add_reading, get_all_modes, get_mode_by_id


class DataSimulator:
    """Simulates sensor data for active modes."""
    
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.running = False
        self.simulation_interval = 2
    
    def generate_value(self, mode_name):
        """Generate a simulated value based on mode type."""
        if mode_name == 'Temperature':
            return round(random.uniform(18.0, 30.0), 2)
        elif mode_name == 'Humidity':
            return round(random.uniform(30.0, 80.0), 2)
        elif mode_name == 'Pressure':
            return round(random.uniform(980.0, 1030.0), 2)
        elif mode_name == 'Light':
            return round(random.uniform(0.0, 1000.0), 2)
        else:
            return round(random.uniform(0.0, 100.0), 2)
    
    def simulate_reading(self, mode):
        """Simulate a single reading for a mode."""
        if mode.get('is_active'):
            value = self.generate_value(mode['name'])
            reading_id = add_reading(mode['id'], value)
            
            reading_data = {
                'id': reading_id,
                'mode_id': mode['id'],
                'mode_name': mode['name'],
                'icon': mode['icon'],
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
            
            if self.socketio:
                self.socketio.emit('new_reading', reading_data)
            
            return reading_data
        return None
    
    def run(self):
        """Run the data simulator (blocking)."""
        self.running = True
        print("Data simulator started")
        
        while self.running:
            modes = get_all_modes()
            for mode in modes:
                if mode.get('is_active'):
                    self.simulate_reading(mode)
            
            time.sleep(self.simulation_interval)
    
    def stop(self):
        """Stop the data simulator."""
        self.running = False
        print("Data simulator stopped")


if __name__ == '__main__':
    simulator = DataSimulator()
    try:
        simulator.run()
    except KeyboardInterrupt:
        simulator.stop()
        print("\nSimulation stopped by user")
