import dash
from dash import dcc, html
from dashboards.layout import create_dashboard_layout
from multiprocessing import freeze_support
import multiprocessing
import atexit
import signal
import os
# Initialize Dash app
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True,
    title="Euro 2024 Dashboard",
    external_stylesheets=[
        "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
    ]
)

# Enable callback exceptions suppression
app.config.suppress_callback_exceptions = True

# Set the layout
app.layout = create_dashboard_layout()

# Function to clean up multiprocessing resources when the app exits
def cleanup_resources():
    """Clean up multiprocessing resources to prevent semaphore leaks"""
    # Explicitly cleanup active processes
    multiprocessing.active_children()
    
    # Try to forcibly clean up any leaked semaphores
    # This is a last resort for leaked resources
    try:
        import resource_tracker
        resource_tracker._ResourceTracker._clean_resources()
    except:
        pass

# Register the cleanup function to run when the program exits
atexit.register(cleanup_resources)

# Handle SIGTERM and SIGINT signals to ensure proper cleanup
def signal_handler(sig, frame):
    cleanup_resources()
    os._exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    
    # Set environment variable to limit semaphores
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
    
    # Run with threaded=True to avoid some multiprocessing issues
    app.run(debug=False, host='0.0.0.0', port=8050, threaded=True)

