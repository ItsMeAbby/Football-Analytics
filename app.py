import dash
from dash import dcc, html
from dashboards.layout import create_dashboard_layout
from multiprocessing import freeze_support
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

if __name__ == '__main__':
    # Use freeze_support for Windows compatibility
    freeze_support()
    app.run(debug=False, host='0.0.0.0', port=8050)

