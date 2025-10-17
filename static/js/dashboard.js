/**
 * Dashboard Controller for Mode-Specific Dashboard
 * Handles WebSocket connections, real-time data updates, and UI controls
 */

class DashboardController {
    constructor(modeId, modeName, modeIcon) {
        this.modeId = modeId;
        this.modeName = modeName;
        this.modeIcon = modeIcon;
        this.socket = null;
        this.isConnected = false;
        this.dataCount = 0;
        this.lastUpdateTime = null;
        this.updateRateTracker = [];
        this.voltageDebounceTimer = null;
        this.voltageDebounceDelay = 500; // 500ms debounce
        
        // DOM elements
        this.elements = {};
        
        // Unit mappings for different modes
        this.unitMap = {
            'Temperature': '°C',
            'Humidity': '%',
            'Pressure': 'hPa',
            'Light': 'lux'
        };
    }

    /**
     * Initialize the dashboard
     */
    init() {
        this.cacheElements();
        this.setupWebSocket();
        this.setupEventListeners();
        this.updateTheme();
        this.setUnit();
    }

    /**
     * Cache DOM elements for better performance
     */
    cacheElements() {
        this.elements = {
            // Connection indicators
            wsConnectionStatus: document.getElementById('wsConnectionStatus'),
            wsConnectionText: document.getElementById('wsConnectionText'),
            dataStreamIndicator: document.getElementById('dataStreamIndicator'),
            dataStreamText: document.getElementById('dataStreamText'),
            
            // Controls
            powerToggle: document.getElementById('powerToggle'),
            voltageSlider: document.getElementById('voltageSlider'),
            voltageValue: document.getElementById('voltageValue'),
            voltageFeedback: document.getElementById('voltageFeedback'),
            modeStatus: document.getElementById('modeStatus'),
            
            // Readouts
            currentValue: document.getElementById('currentValue'),
            valueUnit: document.getElementById('valueUnit'),
            lastUpdated: document.getElementById('lastUpdated'),
            displayVoltage: document.getElementById('displayVoltage'),
            updateRate: document.getElementById('updateRate'),
            dataPoints: document.getElementById('dataPoints'),
            
            // Container
            container: document.querySelector('.mode-dashboard-container')
        };
    }

    /**
     * Setup WebSocket connection
     */
    setupWebSocket() {
        this.socket = io();
        
        // Connection events
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.handleConnection();
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.handleDisconnection();
        });
        
        this.socket.on('connection_response', (data) => {
            console.log('Connection response:', data);
            this.subscribeToMode();
        });
        
        // Subscription events
        this.socket.on('subscription_confirmed', (data) => {
            console.log('Subscription confirmed:', data);
            this.showFeedback('Subscribed to ' + data.mode_name, 'success');
        });
        
        // Data events
        this.socket.on('data_update', (data) => {
            if (data.mode_id === this.modeId) {
                this.handleDataUpdate(data);
            }
        });
        
        // Mode status events
        this.socket.on('mode_changed', (data) => {
            if (data.mode_id === this.modeId) {
                this.handleModeChanged(data);
            }
        });
        
        // Voltage events
        this.socket.on('voltage_changed', (data) => {
            if (data.mode_id === this.modeId) {
                this.handleVoltageChanged(data);
            }
        });
        
        // Error events
        this.socket.on('error', (data) => {
            console.error('Socket error:', data);
            this.showFeedback('Error: ' + data.error, 'error');
        });
    }

    /**
     * Subscribe to mode updates
     */
    subscribeToMode() {
        this.socket.emit('subscribe_mode', { mode_id: this.modeId });
    }

    /**
     * Setup event listeners for UI controls
     */
    setupEventListeners() {
        // Power toggle
        if (this.elements.powerToggle) {
            this.elements.powerToggle.addEventListener('change', (e) => {
                this.handlePowerToggle(e.target.checked);
            });
        }
        
        // Voltage slider with debounce
        if (this.elements.voltageSlider) {
            this.elements.voltageSlider.addEventListener('input', (e) => {
                // Update display immediately
                this.updateVoltageDisplay(e.target.value);
                
                // Debounce API call
                this.debouncedVoltageUpdate(e.target.value);
            });
        }
    }

    /**
     * Handle connection established
     */
    handleConnection() {
        this.isConnected = true;
        this.updateConnectionStatus(true);
    }

    /**
     * Handle connection lost
     */
    handleDisconnection() {
        this.isConnected = false;
        this.updateConnectionStatus(false);
    }

    /**
     * Update connection status UI
     */
    updateConnectionStatus(connected) {
        if (this.elements.wsConnectionStatus && this.elements.wsConnectionText) {
            if (connected) {
                this.elements.wsConnectionStatus.className = 'status-dot connected';
                this.elements.wsConnectionText.textContent = 'Connected';
            } else {
                this.elements.wsConnectionStatus.className = 'status-dot disconnected';
                this.elements.wsConnectionText.textContent = 'Disconnected';
            }
        }
    }

    /**
     * Update data stream indicator
     */
    updateDataStreamStatus(active) {
        if (this.elements.dataStreamIndicator && this.elements.dataStreamText) {
            if (active) {
                this.elements.dataStreamIndicator.className = 'stream-indicator active';
                this.elements.dataStreamText.textContent = 'Receiving data';
            } else {
                this.elements.dataStreamIndicator.className = 'stream-indicator inactive';
                this.elements.dataStreamText.textContent = 'No data';
            }
        }
    }

    /**
     * Handle data update from WebSocket
     */
    handleDataUpdate(data) {
        this.updateDataStreamStatus(true);
        
        // Update current value
        if (this.elements.currentValue) {
            const valueNumber = this.elements.currentValue.querySelector('.value-number');
            if (valueNumber) {
                valueNumber.textContent = parseFloat(data.value).toFixed(2);
                
                // Add pulse animation
                this.elements.currentValue.classList.add('pulse');
                setTimeout(() => {
                    this.elements.currentValue.classList.remove('pulse');
                }, 500);
            }
        }
        
        // Update timestamp
        if (this.elements.lastUpdated) {
            const timestamp = new Date(data.timestamp);
            this.elements.lastUpdated.textContent = 'Last updated: ' + timestamp.toLocaleTimeString();
        }
        
        // Update voltage display if provided
        if (data.voltage !== undefined && this.elements.displayVoltage) {
            this.elements.displayVoltage.textContent = parseFloat(data.voltage).toFixed(1);
        }
        
        // Update data count and rate
        this.dataCount++;
        if (this.elements.dataPoints) {
            this.elements.dataPoints.textContent = this.dataCount;
        }
        
        this.updateRate();
        
        this.lastUpdateTime = Date.now();
    }

    /**
     * Calculate and update data rate
     */
    updateRate() {
        const now = Date.now();
        this.updateRateTracker.push(now);
        
        // Keep only last 10 seconds of updates
        this.updateRateTracker = this.updateRateTracker.filter(time => now - time < 10000);
        
        // Calculate rate in Hz
        const rate = this.updateRateTracker.length / 10;
        
        if (this.elements.updateRate) {
            this.elements.updateRate.textContent = rate.toFixed(2);
        }
    }

    /**
     * Handle mode changed event
     */
    handleModeChanged(data) {
        const isActive = data.is_active;
        
        // Update power toggle
        if (this.elements.powerToggle) {
            this.elements.powerToggle.checked = isActive;
        }
        
        // Update voltage slider state
        if (this.elements.voltageSlider) {
            this.elements.voltageSlider.disabled = !isActive;
        }
        
        // Update status badge
        this.updateStatusBadge(isActive);
        
        // Update data stream status
        if (!isActive) {
            this.updateDataStreamStatus(false);
        }
    }

    /**
     * Handle voltage changed event
     */
    handleVoltageChanged(data) {
        if (data.voltage !== undefined) {
            if (this.elements.voltageSlider) {
                this.elements.voltageSlider.value = data.voltage;
            }
            this.updateVoltageDisplay(data.voltage);
            this.showFeedback('Voltage updated to ' + data.voltage.toFixed(1) + 'V', 'success');
        }
    }

    /**
     * Handle power toggle change
     */
    async handlePowerToggle(isActive) {
        try {
            const response = await fetch('/api/mode/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    mode_id: this.modeId,
                    enforce_single_active: false
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to toggle mode');
            }
            
            const data = await response.json();
            console.log('Mode toggled:', data);
            
            // Update UI
            this.updateStatusBadge(isActive);
            
            // Enable/disable voltage slider
            if (this.elements.voltageSlider) {
                this.elements.voltageSlider.disabled = !isActive;
            }
            
            this.showFeedback(isActive ? 'Mode activated' : 'Mode deactivated', 'success');
            
        } catch (error) {
            console.error('Error toggling mode:', error);
            this.showFeedback('Failed to toggle mode', 'error');
            
            // Revert toggle on error
            if (this.elements.powerToggle) {
                this.elements.powerToggle.checked = !isActive;
            }
        }
    }

    /**
     * Debounced voltage update
     */
    debouncedVoltageUpdate(voltage) {
        // Clear existing timer
        if (this.voltageDebounceTimer) {
            clearTimeout(this.voltageDebounceTimer);
        }
        
        // Show pending feedback
        this.showFeedback('Updating voltage...', 'info');
        
        // Set new timer
        this.voltageDebounceTimer = setTimeout(() => {
            this.updateVoltage(voltage);
        }, this.voltageDebounceDelay);
    }

    /**
     * Update voltage via API
     */
    async updateVoltage(voltage) {
        try {
            const response = await fetch('/api/voltage/set', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    mode_id: this.modeId,
                    voltage: parseFloat(voltage)
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to set voltage');
            }
            
            const data = await response.json();
            console.log('Voltage updated:', data);
            
            this.showFeedback('Voltage set to ' + parseFloat(voltage).toFixed(1) + 'V', 'success');
            
        } catch (error) {
            console.error('Error setting voltage:', error);
            this.showFeedback('Failed to set voltage', 'error');
        }
    }

    /**
     * Update voltage display
     */
    updateVoltageDisplay(voltage) {
        if (this.elements.voltageValue) {
            this.elements.voltageValue.textContent = parseFloat(voltage).toFixed(1);
        }
    }

    /**
     * Update status badge
     */
    updateStatusBadge(isActive) {
        if (this.elements.modeStatus) {
            const badge = isActive 
                ? '<span class="status-badge active">Active</span>'
                : '<span class="status-badge inactive">Inactive</span>';
            this.elements.modeStatus.innerHTML = badge;
        }
    }

    /**
     * Show feedback message
     */
    showFeedback(message, type = 'info') {
        if (this.elements.voltageFeedback) {
            this.elements.voltageFeedback.textContent = message;
            this.elements.voltageFeedback.className = 'voltage-feedback ' + type;
            
            // Clear feedback after 3 seconds
            setTimeout(() => {
                if (this.elements.voltageFeedback.textContent === message) {
                    this.elements.voltageFeedback.textContent = '';
                    this.elements.voltageFeedback.className = 'voltage-feedback';
                }
            }, 3000);
        }
    }

    /**
     * Update theme based on mode
     */
    updateTheme() {
        if (this.elements.container) {
            // Remove any existing theme classes
            this.elements.container.classList.remove('theme-temperature', 'theme-humidity', 'theme-pressure', 'theme-light');
            
            // Add appropriate theme class
            const themeClass = 'theme-' + this.modeName.toLowerCase();
            this.elements.container.classList.add(themeClass);
        }
    }

    /**
     * Set unit based on mode
     */
    setUnit() {
        const unit = this.unitMap[this.modeName] || '';
        if (this.elements.valueUnit) {
            this.elements.valueUnit.textContent = unit;
        }
    }

    /**
     * Cleanup when leaving page
     */
    destroy() {
        if (this.socket) {
            this.socket.emit('unsubscribe_mode', { mode_id: this.modeId });
            this.socket.disconnect();
        }
        
        if (this.voltageDebounceTimer) {
            clearTimeout(this.voltageDebounceTimer);
        }
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.dashboardController) {
        window.dashboardController.destroy();
    }
});
