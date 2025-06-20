from math import ceil, floor
import matplotlib
matplotlib.use('Agg')
import dash
from dash import dcc, html, Input, Output, State, callback, dash_table, no_update, MATCH, ALL
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  # Added missing plt import
from utils.data_loader import load_tournament_data, get_all_teams, get_team_players, get_all_players
from utils.plot_utils_mpl import create_shot_map, create_heatmap, create_progressive_passes_viz, matplotlib_plot_as_base64  # Added missing import

def create_performance_radar_plotly(players_data, chart_title=None):
    """Create a Plotly radar chart for player performance metrics with hover functionality
    
    Parameters:
    -----------
    players_data: list of dicts
        List of dictionaries where each dict contains:
        - player_name: str - Name of the player
        - metrics: dict - Raw metrics for the player
        - normalized_metrics: dict - Normalized metrics (0-100 scale)
        - color_scheme: dict - Optional color scheme for the player
    chart_title: str, optional
        Title for the radar chart
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Radar chart showing performance of one or more players
    """
    if not players_data:
        # Return empty figure if no data provided
        return go.Figure()
    
    # Create a new figure
    fig = go.Figure()
    
    # Get categories from the first player's data (assuming all players have the same metrics)
    first_player = players_data[0]
    categories = list(first_player['normalized_metrics'].keys())
    
    # Track max value to set axis range
    max_value = 0
    
    # Default color schemes if not provided
    default_colors = [
        {'fill': 'rgba(52, 152, 219, 0.4)', 'line': '#3498db', 'marker': '#3498db'},  # Blue
        {'fill': 'rgba(231, 76, 60, 0.4)', 'line': '#e74c3c', 'marker': '#e74c3c'},      # Red
        {'fill': 'rgba(46, 204, 113, 0.4)', 'line': '#2ecc71', 'marker': '#2ecc71'},      # Green
        {'fill': 'rgba(155, 89, 182, 0.4)', 'line': '#9b59b6', 'marker': '#9b59b6'},      # Purple
        {'fill': 'rgba(241, 196, 15, 0.4)', 'line': '#f1c40f', 'marker': '#f1c40f'},      # Yellow
        {'fill': 'rgba(52, 73, 94, 0.4)', 'line': '#34495e', 'marker': '#34495e'}         # Dark Blue
    ]
    
    # Add traces for each player
    for i, player_data in enumerate(players_data):
        player_name = player_data['player_name']
        metrics = player_data['metrics']
        normalized_metrics = player_data['normalized_metrics']
        
        # Use provided color scheme or default
        color_scheme = player_data.get('color_scheme', default_colors[i % len(default_colors)])
        
        # Set up values
        values = list(normalized_metrics.values())
        max_value = max(max_value, max(values))
        
        # Close the loop by appending the first value at the end
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]
        
        # Add the radar chart trace
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            fillcolor=color_scheme['fill'],
            line=dict(
                color=color_scheme['line'],
                width=2
            ),
            hovertemplate='<b>%{theta}</b><br><b>' + player_name + '</b><br>Value: %{r:.1f}%<br>Raw: %{customdata}<extra></extra>',
            customdata=[metrics[cat] for cat in categories_closed],  # Add raw values for hover
            name=player_name
        ))
        
        # Only add markers for single player view to reduce clutter
        if len(players_data) == 1:
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                mode='markers',
                marker=dict(
                    size=8,
                    color=color_scheme['marker'],
                    line=dict(color='white', width=1)
                ),
                hovertemplate='<b>%{theta}</b><br>Player: ' + player_name + '<br>Value: %{r:.1f}%<br>Raw: %{customdata}<extra></extra>',
                customdata=[metrics[cat] for cat in categories],
                showlegend=False
            ))
    
    # Set the chart title
    if chart_title is None:
        if len(players_data) == 1:
            chart_title = f"Performance Radar - {players_data[0]['player_name']}"
        else:
            chart_title = f"Player Comparison - {len(players_data)} Players"
    
    # Configure tick values based on chart type and max value
    if chart_title == "Volume Metrics" or "Volume" in chart_title:
        ticks = [10, 20, 30, ceil(max(40, max_value + 10))]
        range_max = max(40, max_value + 10)
    else:  # Success rates
        ticks = [i for i in range(20,120, 20)]
        range_max = 100+10
    
    # Configure the layout for the radar chart
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, range_max],  # Dynamic range based on values
                tickfont=dict(size=11),  # Slightly larger ticks
                tickvals=ticks,  # Custom ticks
                angle=90,  # Align ticks
                tickangle=90,  # Align tick labels
                gridcolor='rgba(0, 0, 0, 0.05)',  # Lighter grid
                linecolor='rgba(0, 0, 0, 0.05)',  # Lighter axis lines
                showticklabels=True,
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#2c3e50'),
                rotation=90,  # Start at top (12 o'clock)
                direction='clockwise',
                gridcolor='rgba(0, 0, 0, 0.05)',  # Lighter grid
                showticklabels=True,
            ),
            bgcolor='rgba(0, 0, 0, 0.02)'  # Very light background
        ),
        title=dict(
            text=chart_title,
            font=dict(size=18, color='#2c3e50'),
            y=0.98
        ),
        paper_bgcolor='white',  # Match the container background
        plot_bgcolor='white',
        margin=dict(l=30, r=30, t=60, b=100),  # Optimized margins for legend
        height=550,  # Set height to match container
        width=550,  # Set width to match container
        autosize=True,
        showlegend=True,  # Show legend for multiple players
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,  # Position further below the chart to avoid overlap
            xanchor="center",
            x=0.5,    # Center horizontally
            bgcolor='rgba(255, 255, 255, 0.9)',  # Semi-transparent background
            bordercolor='rgba(0, 0, 0, 0.1)',    # Light border
            borderwidth=1,
            font=dict(size=12),
            itemsizing='constant'
        ),
        hoverlabel=dict(
            font=dict(size=12, family='Arial'),
            bgcolor='white'
        )
    )
    
    return fig

def calculate_success_rates(player_events):
    """Calculate success rates for different action types"""
    # Initialize metrics dictionary
    success_metrics = {}
    
    # Calculate pass success rate
    total_passes = len(player_events[player_events['type'] == 'Pass'])
    successful_passes = len(player_events[
        (player_events['type'] == 'Pass') & 
        (player_events['pass_outcome'].isna())  # Successful passes have no outcome
    ])
    success_metrics['Pass Success'] = (successful_passes / total_passes * 100) if total_passes > 0 else 0
    
    # Calculate dribble success rate
    total_dribbles = len(player_events[player_events['type'] == 'Dribble'])
    successful_dribbles = len(player_events[
        (player_events['type'] == 'Dribble') & 
        (player_events['dribble_outcome'].apply(
            lambda x: x == 'Complete' if isinstance(x, str) else False
        ))
    ])
    success_metrics['Dribble Success'] = (successful_dribbles / total_dribbles * 100) if total_dribbles > 0 else 0
    
    # Calculate shot success rate (goals/shots)
    total_shots = len(player_events[player_events['type'] == 'Shot'])
    successful_shots = len(player_events[
        (player_events['type'] == 'Shot') & 
        (player_events['shot_outcome'].apply(
            lambda x: x == 'Goal' if isinstance(x, str) else False
        ))
    ])
    success_metrics['Shot Success'] = (successful_shots / total_shots * 100) if total_shots > 0 else 0
    
    # Calculate duel success rate
    total_duels = len(player_events[player_events['type'] == 'Duel'])
    successful_duels = len(player_events[
        (player_events['type'] == 'Duel') & 
        (player_events['duel_outcome'].apply(
            lambda x: x in ['Success In Play', 'Won', 'Success Out'] if isinstance(x, str) else False
        ))
    ])
    success_metrics['Duel Success'] = (successful_duels / total_duels * 100) if total_duels > 0 else 0
    
    # Calculate interception success rate
    total_interceptions = len(player_events[player_events['type'] == 'Interception'])
    successful_interceptions = len(player_events[
        (player_events['type'] == 'Interception') & 
        (player_events['interception_outcome'].apply(
            lambda x: x in ['Success In Play', 'Won', 'Success Out'] if isinstance(x, str) else False
        ))
    ])
    success_metrics['Interception Success'] = (successful_interceptions / total_interceptions * 100) if total_interceptions > 0 else 0
    
    # Create raw metrics dictionary with the same counts
    raw_metrics = {
        'Pass Success': successful_passes,
        'Dribble Success': successful_dribbles,
        'Shot Success': successful_shots,
        'Duel Success': successful_duels,
        'Interception Success': successful_interceptions
    }
    
    return success_metrics, raw_metrics

def layout():
    return html.Div([
        # Header for player analysis
        html.Div([
            html.H2("🏃‍♂️ Player Performance Dashboard", 
                   style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50'}),
            html.P("Analyze individual player performances throughout Euro 2024", 
                   style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'lineHeight': '1.5'})
        ], style={
            'backgroundColor': 'white', 
            'padding': '25px', 
            'borderRadius': '15px',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
            'marginBottom': '25px'
        }),
        
        # Player selection
        html.Div([
            html.H4("🔍 Player Selection", style={'marginBottom': '20px', 'color': '#2c3e50'}),
            html.Div([
                html.Div([
                    html.Label("Select Team:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='player-team-dropdown',
                        options=[],
                        placeholder="Select a team...",
                        style={'marginBottom': '10px'}
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'paddingRight': '10px'}),
                html.Div([
                    html.Label("Select Player:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='player-dropdown',
                        placeholder="Select a player...",
                        style={'marginBottom': '10px'}
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'paddingLeft': '10px'}),
            ]),
            html.Div([
                html.Label("Compare with Player:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='comparison-player-dropdown',
                    placeholder="Select a player to compare...",
                    style={'marginBottom': '10px'}
                )
            ], style={'width': '100%', 'display': 'block', 'marginTop': '10px'})
        ], style={
            'backgroundColor': 'white', 
            'padding': '20px', 
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        }),
        
        # Player stats summary
        html.Div(id='player-stats-summary', style={'marginBottom': '20px'}),
        
        # Player visualizations
        html.Div([
            html.H4("📊 Player Analysis", style={'marginBottom': '20px', 'color': '#2c3e50'}),
            dcc.Tabs([
                dcc.Tab(label="🎯 Shot Analysis", value="shots-tab", style={'padding': '12px', 'fontWeight': 'bold'}),
                dcc.Tab(label="🔥 Touch Heatmap", value="heatmap-tab", style={'padding': '12px', 'fontWeight': 'bold'}),
                dcc.Tab(label="⚡ Progressive Actions", value="progressive-tab", style={'padding': '12px', 'fontWeight': 'bold'}),
                dcc.Tab(label="📈 Performance Metrics", value="metrics-tab", style={'padding': '12px', 'fontWeight': 'bold'}),
            ], id="player-tabs", value="shots-tab", style={'marginBottom': '20px'}),
            html.Div(id='player-viz-content', style={'marginTop': '20px'})
        ], style={
            'backgroundColor': 'white', 
            'padding': '25px', 
            'borderRadius': '15px',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
            'marginBottom': '25px'
        }),
        
        # # Player comparison
        # html.Div([
        #     html.H4("⚖️ Player Comparison", style={'marginBottom': '20px', 'color': '#2c3e50'}),
        #     html.Div([
        #         html.P([
        #             "Select a player to compare from the 'Performance Metrics' tab to visualize both players on the same radar charts. This provides a more comprehensive comparison across multiple metrics simultaneously."
        #         ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px', 'textAlign': 'center'}),
        #         html.Div([
        #             html.Label("Comparison Metric:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
        #             dcc.Dropdown(
        #                 id='comparison-metric-dropdown',
        #                 options=[
        #                     {'label': 'Goals', 'value': 'goals'},
        #                     {'label': 'Shots', 'value': 'shots'},
        #                     {'label': 'Passes', 'value': 'passes'},
        #                     {'label': 'Dribbles', 'value': 'dribbles'}
        #                 ],
        #                 value='goals',
        #                 style={'marginBottom': '10px'}
        #             )
        #         ], style={'width': '100%', 'display': 'inline-block'}),
        #     ]),
        #     html.Div(id='player-comparison-content', style={'marginTop': '20px'})
        # ], style={
        #     'backgroundColor': 'white', 
        #     'padding': '25px', 
        #     'borderRadius': '15px',
        #     'boxShadow': '0 4px 20px rgba(0,0,0,0.1)'
        # }),
        
    ], style={
        'padding': '20px',
        'backgroundColor': '#f8f9fa',
        'minHeight': '100vh'
    })

@callback(
    Output('player-team-dropdown', 'options'),
    Output('player-team-dropdown', 'value'),
    Input('player-team-dropdown', 'id')
)
def update_team_options(_):
    teams = get_all_teams()
    options = [{'label': team, 'value': team} for team in teams]
    default_team = 'Spain' if 'Spain' in teams else teams[0] if teams else None
    return options, default_team

@callback(
    Output('player-dropdown', 'options'),
    Output('player-dropdown', 'value'),
    Input('player-team-dropdown', 'value')
)
def update_player_options(selected_team):
    if not selected_team:
        return [], None
    
    try:
        # Get team players using the optimized function
        players = get_team_players(selected_team)
        options = [{'label': player, 'value': player} for player in players]
        return options, options[0]['value'] if options else None
        
    except Exception as e:
        print(f"Error loading players: {e}")
        return [], None

@callback(
    Output('comparison-player-dropdown', 'options'),
    Output('comparison-player-dropdown', 'value'),
    Input('player-dropdown', 'value')
)
def update_comparison_options(selected_player):
    if not selected_player:
        return [], None
    
    try:
        # Get all tournament players using the optimized function
        all_players = get_all_players()
        
        # Remove the currently selected player from options
        comparison_players = [p for p in all_players if p != selected_player]
        
        return [{'label': player, 'value': player} for player in comparison_players], None
        
    except Exception as e:
        print(f"Error loading comparison players: {e}")
        return [], None

@callback(
    Output('player-stats-summary', 'children'),
    Input('player-dropdown', 'value')
)
def update_player_summary(selected_player):
    if not selected_player:
        return html.P("Please select a player to view their statistics.")
    
    try:
        events_df = load_tournament_data()
        
        # Filter events for the player
        player_events = events_df[
            events_df['player'].apply(
                lambda x: x.get('name', '') == selected_player if isinstance(x, dict) else str(x) == selected_player
            )
        ]
        
        if player_events.empty:
            return html.P("No data available for this player.")
        
        # Calculate key statistics
        total_events = len(player_events)
        shots = len(player_events[player_events['type'] == 'Shot'])
        goals = len(player_events[
            (player_events['type'] == 'Shot') & 
            (player_events['shot_outcome'].apply(
                lambda x: x.get('name', '') == 'Goal' if isinstance(x, dict) else str(x) == 'Goal'
            ))
        ])
        passes = len(player_events[player_events['type'] == 'Pass'])
        successful_passes = len(player_events[
            (player_events['type'] == 'Pass') & 
            (player_events['pass_outcome'].isna())
        ])
        pass_accuracy = (successful_passes / passes * 100) if passes > 0 else 0
        
        # Get player team
        player_team = player_events['team'].iloc[0]
        team_name = player_team.get('name', 'Unknown') if isinstance(player_team, dict) else str(player_team)
        
        return html.Div([
            html.H4(f"📋 {selected_player} - {team_name}", 
                   style={'textAlign': 'center', 'color': '#3498db', 'marginBottom': '15px', 'fontSize': '24px'}),
            html.Div([
                html.Div([
                    html.H3(f"{goals}", style={'fontSize': '28px', 'color': '#2ecc71', 'margin': '0', 'fontWeight': 'bold', 'textAlign': 'center'}),
                    html.P("Goals", style={'fontSize': '14px', 'color': '#7f8c8d', 'margin': '0', 'textAlign': 'center'})
                ], style={'width': '16.6%', 'display': 'inline-block'}),
                html.Div([
                    html.H3(f"{shots}", style={'fontSize': '28px', 'color': '#3498db', 'margin': '0', 'fontWeight': 'bold', 'textAlign': 'center'}),
                    html.P("Shots", style={'fontSize': '14px', 'color': '#7f8c8d', 'margin': '0', 'textAlign': 'center'})
                ], style={'width': '16.6%', 'display': 'inline-block'}),
                html.Div([
                    html.H3(f"{passes}", style={'fontSize': '28px', 'color': '#f39c12', 'margin': '0', 'fontWeight': 'bold', 'textAlign': 'center'}),
                    html.P("Passes", style={'fontSize': '14px', 'color': '#7f8c8d', 'margin': '0', 'textAlign': 'center'})
                ], style={'width': '16.6%', 'display': 'inline-block'}),
                html.Div([
                    html.H3(f"{pass_accuracy:.1f}%", style={'fontSize': '28px', 'color': '#3498db', 'margin': '0', 'fontWeight': 'bold', 'textAlign': 'center'}),
                    html.P("Pass Accuracy", style={'fontSize': '14px', 'color': '#7f8c8d', 'margin': '0', 'textAlign': 'center'})
                ], style={'width': '16.6%', 'display': 'inline-block'}),
                html.Div([
                    html.H3(f"{total_events}", style={'fontSize': '28px', 'color': '#7f8c8d', 'margin': '0', 'fontWeight': 'bold', 'textAlign': 'center'}),
                    html.P("Total Actions", style={'fontSize': '14px', 'color': '#7f8c8d', 'margin': '0', 'textAlign': 'center'})
                ], style={'width': '16.6%', 'display': 'inline-block'}),
                html.Div([
                    html.H3(f"{(goals/shots*100) if shots > 0 else 0:.1f}%", style={'fontSize': '28px', 'color': '#e74c3c', 'margin': '0', 'fontWeight': 'bold', 'textAlign': 'center'}),
                    html.P("Shot Accuracy", style={'fontSize': '14px', 'color': '#7f8c8d', 'margin': '0', 'textAlign': 'center'})
                ], style={'width': '16.6%', 'display': 'inline-block'}),
            ])
        ], style={
            'backgroundColor': 'white', 
            'padding': '20px', 
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
        })
        
    except Exception as e:
        return html.Div([
            html.P(f"Error loading player data: {str(e)}", className="text-danger")
        ])

@callback(
    Output('player-viz-content', 'children'),
    Input('player-tabs', 'value'),
    Input('player-dropdown', 'value'),
    Input('comparison-player-dropdown', 'value')
)
def update_player_visualizations(active_tab, selected_player, comparison_player):
    if not selected_player:
        return html.P("Please select a player.")
    
    try:
        events_df = load_tournament_data()
        
        if active_tab == "shots-tab":
            shot_map = create_shot_map(events_df, None, selected_player)
            return html.Div([
                html.Div([
                    html.H5("🎯 Shot Analysis", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                    html.Span(" ℹ️", style={
                        'marginLeft': '10px', 
                        'cursor': 'pointer', 
                        'fontSize': '16px',
                        'color': '#3498db'
                    }, title="Shot locations and expected goals (xG) values")
                ]),
                html.P([
                    "This visualization maps all of ", 
                    html.Strong(selected_player), 
                    "'s shots throughout the tournament. Circle size represents the Expected Goals (xG) value of each shot, with larger circles indicating higher-probability chances. Goals are marked with a distinct football icon, while other shots use a striped pattern. This approach allows for immediate identification of shooting patterns, efficiency, and location preferences."
                ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
                html.Details([
                    html.Summary("📖 Visualization Design Rationale", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer', 'marginTop': '15px'}),
                    html.Div([
                        html.P(["• ", html.Strong("Size Encoding:"), " Shot circles are sized proportionally to xG values, allowing for immediate quality assessment beyond just position. This visualization choice emphasizes quality over quantity of chances."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Color and Pattern Differentiation:"), " Goals are distinguished with a clear football icon against missed shots' pattern, creating a pre-attentive visual separation that communicates outcomes without requiring conscious processing."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Spatial Positioning:"), " Shots are mapped to their exact field locations on a standard pitch, preserving the spatial relationships and allowing for analysis of shot distance, angle, and pattern preferences."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Alternatives Considered:"), " While we could have used heat maps or binned shot locations, individual shot plotting preserves the granularity of each attempt while still communicating patterns through visual clustering."], style={'margin': '12px 0', 'fontSize': '13px'})
                    ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                ], style={'marginTop': '10px'}),
                html.Img(style={'width': '100%', 'maxWidth': '800px', 'margin': '0 auto', 'display': 'block'}, src=shot_map),
            ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'})
        
        elif active_tab == "heatmap-tab":
            heatmap = create_heatmap(events_df, selected_player)
            return html.Div([
                html.Div([
                    html.H5("🔥 Touch Heatmap", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                    html.Span(" ℹ️", style={
                        'marginLeft': '10px', 
                        'cursor': 'pointer', 
                        'fontSize': '16px',
                        'color': '#3498db'
                    }, title="Player movement and activity zones")
                ]),
                html.P([
                    "This heatmap visualization reveals ", 
                    html.Strong(selected_player), 
                    "'s spatial distribution across the pitch. Areas of higher activity appear in deeper red, showing where the player spent most time and had the most touches. The pitch is divided into zones with percentage values indicating relative activity in each area. This approach provides insight into positioning tendencies, role execution, and spatial preferences."
                ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
                html.Img(style={'width': '100%', 'maxWidth': '800px', 'margin': '0 auto', 'display': 'block'}, src=heatmap),
                html.Details([
                    html.Summary("📖 Visualization Design Rationale", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer', 'marginTop': '15px'}),
                    html.Div([
                        html.P(["• ", html.Strong("Binned Activity Zones:"), " Rather than a continuous heatmap, we've chosen a gridded approach with percentage labels to quantify activity distribution. This makes the data more interpretable and comparable across players."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Color Intensity Mapping:"), " The white-to-red gradient visually encodes activity intensity, with the perceptually intuitive association of 'hotter' areas indicating higher activity."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Percentage Annotations:"), " Each zone includes a percentage label for precise activity quantification, balancing the qualitative color mapping with exact numerical values."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Alternatives Considered:"), " Continuous kernel density estimation would show smoother gradients but sacrifice quantifiability, while individual event plotting would show exact positions but obscure overall patterns."], style={'margin': '12px 0', 'fontSize': '13px'})
                    ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                ], style={'marginTop': '10px'})
            ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'})
        
        elif active_tab == "progressive-tab":
            # Get player team first
            player_events = events_df[
                events_df['player'].apply(
                    lambda x: x.get('name', '') == selected_player if isinstance(x, dict) else str(x) == selected_player
                )
            ]
            
            if not player_events.empty:
                player_team = player_events['team'].iloc[0]
                team_name = player_team.get('name', 'Unknown') if isinstance(player_team, dict) else str(player_team)
                prog_viz = create_progressive_passes_viz(events_df, team_name)
                return html.Div([
                    html.Div([
                        html.H5("⚡ Progressive Actions", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                        html.Span(" ℹ️", style={
                            'marginLeft': '10px', 
                            'cursor': 'pointer', 
                            'fontSize': '16px',
                            'color': '#3498db'
                        }, title="Forward passes and ball progression metrics")
                    ]),
                    html.P([
                        "This chart shows the distribution of progressive passes across all players on ", 
                        html.Strong(selected_player), 
                        "'s team (", html.Strong(team_name), "). Progressive passes are defined as passes that significantly advance the ball toward the opponent's goal (at least 10 meters forward). The horizontal bar chart ranks each player by their total progressive passes, highlighting key playmakers and ball progressors within the team context."
                    ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
                    html.Img(style={'width': '100%', 'maxWidth': '800px', 'margin': '0 auto', 'display': 'block'}, src=prog_viz),
                    html.Details([
                        html.Summary("📖 Visualization Design Rationale", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer', 'marginTop': '15px'}),
                        html.Div([
                            html.P(["• ", html.Strong("Horizontal Bar Orientation:"), " This layout allows for clear reading of player names while providing a direct visual comparison of progressive pass counts. The length encoding creates an immediate hierarchical understanding."], style={'margin': '12px 0', 'fontSize': '13px'}),
                            html.P(["• ", html.Strong("Team Context:"), " By showing all players, we provide contextual benchmarking for the selected player's contribution to team ball progression, offering both absolute and relative performance measures."], style={'margin': '12px 0', 'fontSize': '13px'}),
                            html.P(["• ", html.Strong("Progressive Pass Definition:"), " We define progressive passes as those that advance the ball at least 10 meters toward the opponent's goal, a standard metric for measuring meaningful forward ball movement."], style={'margin': '12px 0', 'fontSize': '13px'}),
                            html.P(["• ", html.Strong("Alternatives Considered:"), " We could have shown progressive carries alongside passes, or used a pass map showing specific progressive passing lanes, but opted for the cleaner comparison of raw counts for clarity."], style={'margin': '12px 0', 'fontSize': '13px'})
                        ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                    ], style={'marginTop': '10px'})
                ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'})
            else:
                return html.P("No progressive pass data available.")
        
        elif active_tab == "metrics-tab":
            # Create performance radar chart
            player_events = events_df[
                events_df['player'].apply(
                    lambda x: x.get('name', '') == selected_player if isinstance(x, dict) else str(x) == selected_player
                )
            ]
            
            if player_events.empty:
                return html.P("No performance data available.")
            
            # Check if comparison player is selected
            comparison_player_events = None
            
            if comparison_player and comparison_player != selected_player:
                comparison_player_events = events_df[
                    events_df['player'].apply(
                        lambda x: x.get('name', '') == comparison_player if isinstance(x, dict) else str(x) == comparison_player
                    )
                ]
            
            # Calculate metrics for primary player
            metrics = {
                'Goals': len(player_events[
                    (player_events['type'] == 'Shot') & 
                    (player_events['shot_outcome'].apply(
                        lambda x: x.get('name', '') == 'Goal' if isinstance(x, dict) else str(x) == 'Goal'
                    ))
                ]),
                'Shots': len(player_events[player_events['type'] == 'Shot']),
                'Passes': len(player_events[player_events['type'] == 'Pass']),
                'Dribbles': len(player_events[player_events['type'] == 'Dribble']),
                'Duels': len(player_events[player_events['type'] == 'Duel']),
                'Interceptions': len(player_events[player_events['type'] == 'Interception'])
            }
            
            # Normalize metrics for radar chart (0-100 scale)
            max_vals = {'Goals': 3, 'Shots': 25, 'Passes': 562, 'Dribbles': 32, 'Duels': 31, 'Interceptions': 12}
            normalized_metrics = {k: min(100, (v / max_vals[k]) * 100) for k, v in metrics.items()}
            
            # Calculate success rates for primary player
            success_metrics, raw_success_metrics = calculate_success_rates(player_events)
            normalized_success_metrics = {k: min(v, 100) for k, v in success_metrics.items()}
            
            # Setup players data for volume metrics radar
            volume_players_data = [{
                'player_name': selected_player,
                'metrics': metrics,
                'normalized_metrics': normalized_metrics,
                'color_scheme': {
                    'fill': 'rgba(52, 152, 219, 0.4)',  # Blue
                    'line': '#3498db',
                    'marker': '#3498db'
                }
            }]
            
            # Setup players data for success metrics radar
            success_players_data = [{
                'player_name': selected_player,
                'metrics': raw_success_metrics,
                'normalized_metrics': normalized_success_metrics,
                'color_scheme': {
                    'fill': 'rgba(46, 204, 113, 0.4)',  # Green
                    'line': '#2ecc71',
                    'marker': '#2ecc71'
                }
            }]
            
            # Add comparison player data if available
            if comparison_player and comparison_player != selected_player and comparison_player_events is not None and not comparison_player_events.empty:
                # Calculate metrics for comparison player
                comp_metrics = {
                    'Goals': len(comparison_player_events[
                        (comparison_player_events['type'] == 'Shot') & 
                        (comparison_player_events['shot_outcome'].apply(
                            lambda x: x.get('name', '') == 'Goal' if isinstance(x, dict) else str(x) == 'Goal'
                        ))
                    ]),
                    'Shots': len(comparison_player_events[comparison_player_events['type'] == 'Shot']),
                    'Passes': len(comparison_player_events[comparison_player_events['type'] == 'Pass']),
                    'Dribbles': len(comparison_player_events[comparison_player_events['type'] == 'Dribble']),
                    'Duels': len(comparison_player_events[comparison_player_events['type'] == 'Duel']),
                    'Interceptions': len(comparison_player_events[comparison_player_events['type'] == 'Interception'])
                }
                
                # Normalize comparison metrics
                comp_normalized_metrics = {k: min(100, (v / max_vals[k]) * 100) for k, v in comp_metrics.items()}
                
                # Calculate success rates for comparison player
                comp_success_metrics, comp_raw_success_metrics = calculate_success_rates(comparison_player_events)
                comp_normalized_success_metrics = {k: min(v, 100) for k, v in comp_success_metrics.items()}
                
                # Add comparison player to volume radar data
                volume_players_data.append({
                    'player_name': comparison_player,
                    'metrics': comp_metrics,
                    'normalized_metrics': comp_normalized_metrics,
                    'color_scheme': {
                        'fill': 'rgba(231, 76, 60, 0.4)',  # Red
                        'line': '#e74c3c',
                        'marker': '#e74c3c'
                    }
                })
                
                # Add comparison player to success radar data
                success_players_data.append({
                    'player_name': comparison_player,
                    'metrics': comp_raw_success_metrics,
                    'normalized_metrics': comp_normalized_success_metrics,
                    'color_scheme': {
                        'fill': 'rgba(241, 196, 15, 0.4)',  # Yellow
                        'line': '#f1c40f',
                        'marker': '#f1c40f'
                    }
                })
            
            # Create radar charts with clear titles
            volume_chart_title = "Volume Metrics" if len(volume_players_data) == 1 else "Volume Metrics Comparison"
            success_chart_title = "Success Rates" if len(success_players_data) == 1 else "Success Rates Comparison"
            
            # Update font sizes for better readability
            title_font_size = 16
            tickfont_size = 11
            
            volume_fig = create_performance_radar_plotly(volume_players_data, chart_title=volume_chart_title)
            success_fig = create_performance_radar_plotly(success_players_data, chart_title=success_chart_title)
            
            # Determine description based on whether comparison is active
            if len(volume_players_data) > 1:
                description_content = [
                    "These radar charts provide a comparative analysis of ", 
                    html.Strong(selected_player, style={'wordBreak': 'break-word'}), 
                    " and ",
                    html.Strong(comparison_player, style={'wordBreak': 'break-word'}),
                    "'s performance profiles. The left chart compares volume metrics (Goals, Shots, Passes, Dribbles, Duels, and Interceptions), while the right chart contrasts success rates across different action types."
                ]
            else:
                description_content = [
                    "These radar charts provide a comprehensive analysis of ", 
                    html.Strong(selected_player, style={'wordBreak': 'break-word'}), 
                    "'s performance profile. The left chart shows volume metrics (Goals, Shots, Passes, Dribbles, Duels, and Interceptions), while the right chart displays success rates across different action types."
                ]
                
            return html.Div([
                html.Div([
                    html.H5("📈 Player Performance Analysis", style={'color': '#2c3e50', 'marginBottom': '10px', 'textAlign': 'center', 'fontSize': '20px'}),
                    html.Span(" ℹ️", style={
                        'marginLeft': '10px', 
                        'cursor': 'pointer', 
                        'fontSize': '16px',
                        'color': '#3498db'
                    }, title="Multi-dimensional player analysis across key metrics and success rates")
                ]),
                html.P(description_content, style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px', 'textAlign': 'center', 'maxWidth': '1200px', 'margin': '0 auto 15px auto'}),
                
                # Note about comparison selection
                html.Div([
                    html.P(
                        "Use the 'Compare with Player' dropdown above to add another player to these charts",
                        style={'fontStyle': 'italic', 'color': '#7f8c8d', 'textAlign': 'center', 'marginBottom': '20px'}
                    )
                ]),

                # Two radar charts side by side with improved layout
                html.Div([
                    # Header row with metrics labels
                    html.Div([
                        html.Div([
                            html.H6("Volume Metrics", style={'textAlign': 'center', 'marginBottom': '5px', 'color': '#3498db'}),
                            html.P("Raw counts normalized to tournament maximums", style={'fontSize': '12px', 'color': '#7f8c8d', 'textAlign': 'center', 'marginBottom': '10px'}),
                        ], style={'width': '48%', 'display': 'inline-block'}),
                        
                        html.Div([
                            html.H6("Success Rates", style={'textAlign': 'center', 'marginBottom': '5px', 'color': '#2ecc71'}),
                            html.P("Percentage of successful outcomes by action type", style={'fontSize': '12px', 'color': '#7f8c8d', 'textAlign': 'center', 'marginBottom': '10px'}),
                        ], style={'width': '48%', 'display': 'inline-block'}),
                    ], style={'display': 'flex', 'justifyContent': 'space-around', 'width': '100%', 'marginBottom': '10px'}),
                    
                    # Graphs container with even spacing
                    html.Div([
                        # Graph container to center the charts
                        html.Div([
                            dcc.Graph(
                                figure=volume_fig,
                                style={'height': '550px', 'width': '100%', 'minWidth': '450px', 'maxWidth': '600px', 'margin': '0 auto'},
                                config={'displayModeBar': False, 'responsive': True}
                            )
                        ], style={'width': '50%', 'display': 'inline-block', 'textAlign': 'center'}),
                        
                        html.Div([
                            dcc.Graph(
                                figure=success_fig,
                                style={'height': '550px', 'width': '100%', 'minWidth': '450px', 'maxWidth': '600px', 'margin': '0 auto'},
                                config={'displayModeBar': False, 'responsive': True}
                            )
                        ], style={'width': '50%', 'display': 'inline-block', 'textAlign': 'center'}),
                    ], style={'display': 'flex', 'justifyContent': 'center', 'width': '100%', 'marginBottom': '30px'}),
                ], style={'width': '100%', 'padding': '0 20px'}),
                
                # Visualization Design Rationale - Moved below charts
                html.Details([
                    html.Summary("📖 Visualization Design Rationale", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer', 'marginTop': '15px'}),
                    html.Div([
                        html.P(["• ", html.Strong("Dual Radar Approach:"), " By separating volume metrics from success rates, we provide a more nuanced view of player performance that balances quantity and quality of actions."], style={'margin': '8px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Color Distinction:"), " Blue for volume metrics and green for success rates creates a clear visual separation while maintaining a cohesive design language."], style={'margin': '8px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Normalized Scaling:"), " Volume metrics are normalized against tournament maximums, while success rates show actual percentages, providing both relative and absolute performance measures."], style={'margin': '8px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Interactive Elements:"), " Hover functionality on both charts reveals the exact values behind the visualizations, allowing for deeper exploration of the player's statistical profile."], style={'margin': '8px 0', 'fontSize': '13px'})
                    ], style={'paddingLeft': '15px', 'marginTop': '8px', 'marginBottom': '20px'})
                ], style={'marginBottom': '20px', 'border': '1px solid #f0f0f0', 'borderRadius': '5px', 'padding': '10px', 'backgroundColor': '#f9f9f9'})
            ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'overflow': 'hidden', 'maxWidth': '1400px', 'margin': '0 auto'})

            
    except Exception as e:
        return html.P(f"Error creating visualization: {str(e)}")

@callback(
    Output('player-comparison-content', 'children'),
    Input('player-dropdown', 'value'),
    Input('comparison-player-dropdown', 'value'),
    Input('comparison-metric-dropdown', 'value')
)
def update_player_comparison(player1, player2, metric):
    if not player1 or not player2:
        return html.P("Please select players to compare.")
    
    try:
        events_df = load_tournament_data()
        
        # Get events for both players
        player1_events = events_df[
            events_df['player'].apply(
                lambda x: x.get('name', '') == player1 if isinstance(x, dict) else str(x) == player1
            )
        ]
        
        player2_events = events_df[
            events_df['player'].apply(
                lambda x: x.get('name', '') == player2 if isinstance(x, dict) else str(x) == player2
            )
        ]
        
        # Get team names for context
        team1 = player1_events['team'].iloc[0].get('name', 'Unknown') if not player1_events.empty and isinstance(player1_events['team'].iloc[0], dict) else 'Unknown'
        team2 = player2_events['team'].iloc[0].get('name', 'Unknown') if not player2_events.empty and isinstance(player2_events['team'].iloc[0], dict) else 'Unknown'
        
        # Create a message directing users to the Performance Metrics tab
        return html.Div([
            html.Div([
                html.H5("⚖️ Player Comparison", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                html.Span(" ℹ️", style={
                    'marginLeft': '10px', 
                    'cursor': 'pointer', 
                    'fontSize': '16px',
                    'color': '#3498db'
                }, title=f"Multi-dimensional comparison of players")
            ]),
            html.P([
                "For detailed player comparison across multiple metrics simultaneously, please visit the ", 
                html.Strong("'Performance Metrics'"), 
                " tab, where you can view both players on the same radar charts. This provides a more comprehensive comparison than single-metric analysis."
            ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px', 'textAlign': 'center'}),
            html.Div([
                html.Button("Go to Performance Metrics", id="go-to-metrics-tab", n_clicks=0, 
                          style={
                              'backgroundColor': '#3498db',
                              'color': 'white',
                              'border': 'none',
                              'padding': '10px 20px',
                              'borderRadius': '5px',
                              'cursor': 'pointer',
                              'fontWeight': 'bold',
                              'boxShadow': '0 2px 5px rgba(0,0,0,0.1)',
                              'margin': '10px auto',
                              'display': 'block'
                          })
            ]),
            html.P([
                "Current comparison: ", 
                html.Strong(player1), 
                " (", html.Span(team1, style={'color': '#3498db'}), ") and ",
                html.Strong(player2),
                " (", html.Span(team2, style={'color': '#e74c3c'}), ")"
            ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginTop': '20px', 'textAlign': 'center'})
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'})        
    except Exception as e:
        return html.P(f"Error creating comparison: {str(e)}")

# Add callback to navigate to Performance Metrics tab
@callback(
    Output('player-tabs', 'value'),
    Input('go-to-metrics-tab', 'n_clicks'),
    prevent_initial_call=True
)
def go_to_metrics_tab(n_clicks):
    if n_clicks > 0:
        return "metrics-tab"
    return dash.no_update
