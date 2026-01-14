// Main JavaScript file for Rural Hailing

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    console.log('Rural Hailing app loaded');
    
    // Initialize WebSocket connection for real-time updates
    initializeWebSocket();
});

// Initialize WebSocket connection
function initializeWebSocket() {
    // Check if user is authenticated before connecting
    if (window.userAuthenticated) {
        // Connect to WebSocket for notifications and ride updates
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = `${protocol}${window.location.host}/ws/ride-tracking/`;
        
        const socket = new WebSocket(wsUrl);
        
        socket.onopen = function(event) {
            console.log('WebSocket connected');
        };
        
        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('Received message:', data);
            
            // Handle different types of messages
            if (data.type === 'location_update') {
                updateRideLocation(data.latitude, data.longitude, data.ride_id);
            } else if (data.type === 'ride_status_update') {
                updateRideStatus(data.ride_id, data.status);
            } else if (data.type === 'notification') {
                showNotification(data.message);
            }
        };
        
        socket.onclose = function(event) {
            console.log('WebSocket disconnected');
            // Attempt to reconnect after 3 seconds
            setTimeout(initializeWebSocket, 3000);
        };
        
        socket.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
        
        // Store socket reference
        window.rideSocket = socket;
    }
}

// Update ride location on map
function updateRideLocation(latitude, longitude, rideId) {
    console.log(`Updating location for ride ${rideId}: ${latitude}, ${longitude}`);
    
    // Update map if it exists
    if (window.map) {
        updateMapMarker(latitude, longitude);
    }
    
    // Update UI elements showing location
    const locationElement = document.getElementById('current-location');
    if (locationElement) {
        locationElement.textContent = `Current Location: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
    }
}

// Update ride status in UI
function updateRideStatus(rideId, status) {
    console.log(`Updating status for ride ${rideId}: ${status}`);
    
    // Update status badge
    const statusElement = document.getElementById(`ride-status-${rideId}`);
    if (statusElement) {
        statusElement.className = `ride-status status-${status}`;
        statusElement.textContent = status.replace('_', ' ').toUpperCase();
    }
    
    // Show notification based on status
    switch(status) {
        case 'accepted':
            showNotification('Your ride has been accepted by a driver!', 'success');
            break;
        case 'arriving':
            showNotification('Your driver is arriving now!', 'info');
            break;
        case 'picked_up':
            showNotification('You have been picked up. Enjoy your ride!', 'info');
            break;
        case 'completed':
            showNotification('Your ride has been completed!', 'success');
            break;
    }
}

// Show notification to user
function showNotification(message, type = 'info') {
    // Create notification element
    const notificationDiv = document.createElement('div');
    notificationDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notificationDiv.style.top = '20px';
    notificationDiv.style.right = '20px';
    notificationDiv.style.zIndex = '9999';
    notificationDiv.setAttribute('role', 'alert');
    
    notificationDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to body
    document.body.appendChild(notificationDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notificationDiv.parentNode) {
            notificationDiv.parentNode.removeChild(notificationDiv);
        }
    }, 5000);
}

// Update map marker (placeholder function)
function updateMapMarker(lat, lng) {
    // This would update the map marker in a real implementation
    console.log(`Moving marker to: ${lat}, ${lng}`);
}

// Utility function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to handle ride cancellation
async function cancelRide(rideId) {
    if (!confirm('Are you sure you want to cancel this ride?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/rides/${rideId}/cancel/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Ride cancelled successfully', 'success');
            // Update UI to reflect cancellation
            updateRideStatus(rideId, 'cancelled');
        } else {
            showNotification(`Error cancelling ride: ${data.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error cancelling ride:', error);
        showNotification('Error cancelling ride', 'danger');
    }
}

// Function to complete ride (for drivers)
async function completeRide(rideId) {
    if (!confirm('Are you sure you want to mark this ride as completed?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/rides/${rideId}/complete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Ride completed successfully', 'success');
            // Update UI to reflect completion
            updateRideStatus(rideId, 'completed');
        } else {
            showNotification(`Error completing ride: ${data.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error completing ride:', error);
        showNotification('Error completing ride', 'danger');
    }
}