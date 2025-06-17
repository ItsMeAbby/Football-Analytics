
# dashboards/layout.py
from dash import html, dcc
from components import match_overview_simple as match_overview, player_dashboard, tactical_view, event_explorer

def create_dashboard_layout():
    return html.Div([
        # Navigation header
        html.Div([
            html.H1("⚽ UEFA Euro 2024 Analytics Dashboard", 
                   style={
                       'textAlign': 'center',
                       'color': 'white',
                       'padding': '20px',
                       'margin': '0',
                       'background': 'linear-gradient(45deg, #3498db, #2ecc71)',
                       'borderRadius': '0'
                   })
        ], style={'marginBottom': '20px'}),
        
        # Main content with tabs
        html.Div([
            dcc.Tabs([
                dcc.Tab(
                    label="🏟️ Match Overview", 
                    children=match_overview.layout(),
                    style={'padding': '10px', 'fontWeight': 'bold'},
                    selected_style={'padding': '10px', 'fontWeight': 'bold', 'backgroundColor': '#3498db', 'color': 'white'}
                ),
                dcc.Tab(
                    label="🏃‍♂️ Player Dashboard", 
                    children=player_dashboard.layout(),
                    style={'padding': '10px', 'fontWeight': 'bold'},
                    selected_style={'padding': '10px', 'fontWeight': 'bold', 'backgroundColor': '#3498db', 'color': 'white'}
                ),
                dcc.Tab(
                    label="⚡ Tactical Analysis", 
                    children=tactical_view.layout(),
                    style={'padding': '10px', 'fontWeight': 'bold'},
                    selected_style={'padding': '10px', 'fontWeight': 'bold', 'backgroundColor': '#3498db', 'color': 'white'}
                ),
                dcc.Tab(
                    label="🔍 Event Explorer", 
                    children=event_explorer.layout(),
                    style={'padding': '10px', 'fontWeight': 'bold'},
                    selected_style={'padding': '10px', 'fontWeight': 'bold', 'backgroundColor': '#3498db', 'color': 'white'}
                ),
            ], 
            style={'marginBottom': '20px'},
            colors={
                "border": "#3498db",
                "primary": "#2ecc71",
                "background": "#f8f9fa"
            })
        ], style={
            'backgroundColor': 'white', 
            'padding': '10px', 
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
        }),
        
        # Footer
        html.Footer([
            html.Hr(),
            html.P([
                "📊 Data provided by StatsBomb | ",
                html.A("Euro 2024 Analytics", href="#", style={'color': '#3498db', 'textDecoration': 'none'}),
                " | Built with Dash & Plotly"
            ], style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '14px'})
        ], style={'marginTop': '40px'})
        
    ], style={
        'padding': '20px',
        'backgroundColor': '#f8f9fa',
        'minHeight': '100vh',
        'fontFamily': 'Arial, sans-serif'
    })