const socket = io();

socket.on('connect', function() {
    console.log('Connected to server');
});

socket.on('mode_status_changed', function(data) {
    console.log('Mode status changed:', data);
    updateModeCards(data.all_modes);
});

function updateModeCards(modes) {
    modes.forEach(mode => {
        const card = document.querySelector(`.mode-selection-card[data-mode-id="${mode.id}"]`);
        const toggle = document.querySelector(`.mode-toggle[data-mode-id="${mode.id}"]`);
        const statusElement = card.querySelector('.mode-card-status');
        const statusText = statusElement.querySelector('span:last-child');
        
        if (mode.is_active) {
            card.classList.add('active');
            toggle.checked = true;
            statusElement.classList.add('active');
            statusText.textContent = 'Active';
        } else {
            card.classList.remove('active');
            toggle.checked = false;
            statusElement.classList.remove('active');
            statusText.textContent = 'Inactive';
        }
    });
    
    updateDashboardButton(modes);
}

function updateDashboardButton(modes) {
    const viewDashboardBtn = document.getElementById('viewDashboardBtn');
    const hasActiveMode = modes.some(mode => mode.is_active);
    
    if (hasActiveMode) {
        viewDashboardBtn.disabled = false;
    } else {
        viewDashboardBtn.disabled = true;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const toggles = document.querySelectorAll('.mode-toggle');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('change', async function(e) {
            const modeId = this.dataset.modeId;
            const isChecked = this.checked;
            
            try {
                const response = await fetch(`/api/modes/${modeId}/toggle`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        enforce_single_active: true
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Failed to toggle mode');
                }
                
                const data = await response.json();
                console.log('Mode toggled successfully:', data);
                
            } catch (error) {
                console.error('Error toggling mode:', error);
                this.checked = !isChecked;
            }
        });
    });
    
    const viewDashboardBtn = document.getElementById('viewDashboardBtn');
    if (viewDashboardBtn) {
        viewDashboardBtn.addEventListener('click', function() {
            if (!this.disabled) {
                window.location.href = '/dashboard';
            }
        });
    }
    
    const modeCards = document.querySelectorAll('.mode-selection-card');
    modeCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.toggle-switch')) {
                const toggle = this.querySelector('.mode-toggle');
                if (toggle && !toggle.disabled) {
                    toggle.click();
                }
            }
        });
    });
});
