import matplotlib
matplotlib.use('Agg')
import dash
from dash import dcc, html, Input, Output, callback, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  # Added missing plt import
from utils.data_loader import load_tournament_data, get_all_teams, get_team_players, get_all_players
from utils.plot_utils_mpl import create_shot_map, create_heatmap, create_progressive_passes_viz, matplotlib_plot_as_base64  # Added missing import

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
            ])
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
        
        # Player comparison
        html.Div([
            html.H4("⚖️ Player Comparison", style={'marginBottom': '20px', 'color': '#2c3e50'}),
            html.Div([
                html.Div([
                    html.Label("Compare with Player:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='comparison-player-dropdown',
                        placeholder="Select a player to compare...",
                        style={'marginBottom': '10px'}
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'paddingRight': '10px'}),
                html.Div([
                    html.Label("Comparison Metric:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='comparison-metric-dropdown',
                        options=[
                            {'label': 'Goals', 'value': 'goals'},
                            {'label': 'Shots', 'value': 'shots'},
                            {'label': 'Passes', 'value': 'passes'},
                            {'label': 'Dribbles', 'value': 'dribbles'}
                        ],
                        value='goals',
                        style={'marginBottom': '10px'}
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'paddingLeft': '10px'}),
            ]),
            html.Div(id='player-comparison-content', style={'marginTop': '20px'})
        ], style={
            'backgroundColor': 'white', 
            'padding': '25px', 
            'borderRadius': '15px',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.1)'
        }),
        
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
    Input('player-team-dropdown', 'value')
)
def update_comparison_options(selected_team):
    if not selected_team:
        return []
    
    try:
        # Get all tournament players using the optimized function
        players = get_all_players()
        return [{'label': player, 'value': player} for player in players]
        
    except Exception as e:
        print(f"Error loading comparison players: {e}")
        return []

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
    Input('player-dropdown', 'value')
)
def update_player_visualizations(active_tab, selected_player):
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
                    html.Summary("📖 Visualization Design Rationale", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                    html.Div([
                        html.P(["• ", html.Strong("Size Encoding:"), " Shot circles are sized proportionally to xG values, allowing for immediate quality assessment beyond just position. This visualization choice emphasizes quality over quantity of chances."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Color and Pattern Differentiation:"), " Goals are distinguished with a clear football icon against missed shots' pattern, creating a pre-attentive visual separation that communicates outcomes without requiring conscious processing."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Spatial Positioning:"), " Shots are mapped to their exact field locations on a standard pitch, preserving the spatial relationships and allowing for analysis of shot distance, angle, and pattern preferences."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Alternatives Considered:"), " While we could have used heat maps or binned shot locations, individual shot plotting preserves the granularity of each attempt while still communicating patterns through visual clustering."], style={'margin': '12px 0', 'fontSize': '13px'})
                    ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                ], style={'marginTop': '10px'}),
                html.Img(style={'width': '100%', 'maxWidth': '800px', 'margin': '0 auto', 'display': 'block'}, src=shot_map)
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
                html.Details([
                    html.Summary("📖 Visualization Design Rationale", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                    html.Div([
                        html.P(["• ", html.Strong("Binned Activity Zones:"), " Rather than a continuous heatmap, we've chosen a gridded approach with percentage labels to quantify activity distribution. This makes the data more interpretable and comparable across players."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Color Intensity Mapping:"), " The white-to-red gradient visually encodes activity intensity, with the perceptually intuitive association of 'hotter' areas indicating higher activity."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Percentage Annotations:"), " Each zone includes a percentage label for precise activity quantification, balancing the qualitative color mapping with exact numerical values."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Alternatives Considered:"), " Continuous kernel density estimation would show smoother gradients but sacrifice quantifiability, while individual event plotting would show exact positions but obscure overall patterns."], style={'margin': '12px 0', 'fontSize': '13px'})
                    ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                ], style={'marginTop': '10px'}),
                html.Img(style={'width': '100%', 'maxWidth': '800px', 'margin': '0 auto', 'display': 'block'}, src=heatmap)
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
                    html.Details([
                        html.Summary("📖 Visualization Design Rationale", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                        html.Div([
                            html.P(["• ", html.Strong("Horizontal Bar Orientation:"), " This layout allows for clear reading of player names while providing a direct visual comparison of progressive pass counts. The length encoding creates an immediate hierarchical understanding."], style={'margin': '12px 0', 'fontSize': '13px'}),
                            html.P(["• ", html.Strong("Team Context:"), " By showing all players, we provide contextual benchmarking for the selected player's contribution to team ball progression, offering both absolute and relative performance measures."], style={'margin': '12px 0', 'fontSize': '13px'}),
                            html.P(["• ", html.Strong("Progressive Pass Definition:"), " We define progressive passes as those that advance the ball at least 10 meters toward the opponent's goal, a standard metric for measuring meaningful forward ball movement."], style={'margin': '12px 0', 'fontSize': '13px'}),
                            html.P(["• ", html.Strong("Alternatives Considered:"), " We could have shown progressive carries alongside passes, or used a pass map showing specific progressive passing lanes, but opted for the cleaner comparison of raw counts for clarity."], style={'margin': '12px 0', 'fontSize': '13px'})
                        ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                    ], style={'marginTop': '10px'}),
                    html.Img(style={'width': '100%', 'maxWidth': '800px', 'margin': '0 auto', 'display': 'block'}, src=prog_viz)
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
            
            # Calculate metrics
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
                'Tackles': len(player_events[player_events['type'] == 'Tackle']),
                'Interceptions': len(player_events[player_events['type'] == 'Interception'])
            }
            
            # Normalize metrics for radar chart (0-100 scale)
            max_vals = {'Goals': 10, 'Shots': 50, 'Passes': 500, 'Dribbles': 50, 'Tackles': 30, 'Interceptions': 20}
            normalized_metrics = {k: min(100, (v / max_vals[k]) * 100) for k, v in metrics.items()}
            
            # Create matplotlib radar chart instead of plotly
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
            
            # Number of variables
            categories = list(normalized_metrics.keys())
            N = len(categories)
            
            # What will be the angle of each axis in the plot (divide the plot / number of variables)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Close the loop
            
            # Values to plot
            values = list(normalized_metrics.values())
            values += values[:1]  # Close the loop
            
            # Draw the plot
            ax.plot(angles, values, linewidth=2, linestyle='solid', color='#3498db')
            ax.fill(angles, values, color='#3498db', alpha=0.4)
            
            # Fix axis to go in the right order and start at 12 o'clock
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)
            
            # Draw axis lines for each angle and label
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=12)
            
            # Draw ylabels (0-100 scale) - use a smaller scale to make the radar more visible
            max_scale = max(40, max(values) + 10)  # Dynamic scale based on actual values
            ax.set_yticks([10, 20, 30, max_scale])
            ax.set_yticklabels(['10', '20', '30', f'{int(max_scale)}'], fontsize=10)
            ax.set_ylim(0, max_scale)  # Limit the scale to make radar plot more visible
            
            # Add title
            plt.title(f"Performance Radar - {selected_player}", size=15, color='#2c3e50', y=1.08)
            
            # Add raw values as text annotations
            for i, category in enumerate(categories):
                raw_value = metrics[category]
                angle_rad = angles[i]
                # Calculate position slightly outside the data point
                x = (values[i] + 5) * np.cos(angle_rad)
                y = (values[i] + 5) * np.sin(angle_rad)
                plt.text(angle_rad, values[i] + 5, f"{raw_value}", 
                         ha='center', va='center', fontsize=9, 
                         bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
            
            radar_chart = matplotlib_plot_as_base64(fig)
            
            return html.Div([
                html.Div([
                    html.H5("📈 Performance Metrics", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                    html.Span(" ℹ️", style={
                        'marginLeft': '10px', 
                        'cursor': 'pointer', 
                        'fontSize': '16px',
                        'color': '#3498db'
                    }, title="Multi-dimensional player analysis across key metrics")
                ]),
                html.P([
                    "This radar chart provides a multi-dimensional analysis of ", 
                    html.Strong(selected_player), 
                    "'s performance across six key metrics: Goals, Shots, Passes, Dribbles, Tackles, and Interceptions. Each metric is normalized on a 0-100 scale relative to tournament maximums, with raw values shown as numerical annotations. The radar's shape reveals the player's profile and strengths across different aspects of the game."
                ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
                html.Details([
                    html.Summary("📖 Visualization Design Rationale", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                    html.Div([
                        html.P(["• ", html.Strong("Radar Chart Format:"), " This visualization type efficiently communicates a player's multi-dimensional profile in a compact format. The distinctive shape creates a memorable 'signature' of player characteristics that's immediately recognizable."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Normalized Scaling:"), " Each metric is normalized on a 0-100 scale against reasonable tournament maximums, allowing for fair comparison across different statistical categories with vastly different raw ranges."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Dual Information Display:"), " The chart combines the visual shape with numerical annotations showing exact counts, balancing the pattern-recognition benefits of the radar with precise quantitative information."], style={'margin': '12px 0', 'fontSize': '13px'}),
                        html.P(["• ", html.Strong("Alternatives Considered:"), " Bar charts would better show exact values but lose the profile shape, while spider charts with more metrics would provide greater detail but potentially overwhelm with complexity."], style={'margin': '12px 0', 'fontSize': '13px'})
                    ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                ], style={'marginTop': '10px'}),
                html.Img(style={'width': '100%', 'maxWidth': '800px', 'margin': '0 auto', 'display': 'block'}, src=radar_chart)
            ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'})

            
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
        
        # Calculate metrics based on selection
        if metric == 'goals':
            p1_value = len(player1_events[
                (player1_events['type'] == 'Shot') & 
                (player1_events['shot_outcome'].apply(
                    lambda x: x.get('name', '') == 'Goal' if isinstance(x, dict) else str(x) == 'Goal'
                ))
            ])
            p2_value = len(player2_events[
                (player2_events['type'] == 'Shot') & 
                (player2_events['shot_outcome'].apply(
                    lambda x: x.get('name', '') == 'Goal' if isinstance(x, dict) else str(x) == 'Goal'
                ))
            ])
            title = "Goals Comparison"
            metric_description = "total goals scored in the tournament"
            
        elif metric == 'shots':
            p1_value = len(player1_events[player1_events['type'] == 'Shot'])
            p2_value = len(player2_events[player2_events['type'] == 'Shot'])
            title = "Shots Comparison"
            metric_description = "shot attempts throughout the tournament"
            
        elif metric == 'passes':
            p1_value = len(player1_events[player1_events['type'] == 'Pass'])
            p2_value = len(player2_events[player2_events['type'] == 'Pass'])
            title = "Passes Comparison"
            metric_description = "passes attempted during the tournament"
            
        elif metric == 'dribbles':
            p1_value = len(player1_events[player1_events['type'] == 'Dribble'])
            p2_value = len(player2_events[player2_events['type'] == 'Dribble'])
            title = "Dribbles Comparison"
            metric_description = "dribble attempts in the tournament"
        
        # Create matplotlib comparison chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Define colors with better contrast
        colors = ['#3498db', '#e74c3c']
        
        # Create the bar chart
        bars = ax.bar([player1, player2], [p1_value, p2_value], color=colors, width=0.6)
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Add team labels below player names
        ax.text(0, -0.5, f"({team1})", ha='center', va='top', fontsize=10, color='#7f8c8d')
        ax.text(1, -0.5, f"({team2})", ha='center', va='top', fontsize=10, color='#7f8c8d')
        
        # Customize the chart
        ax.set_ylabel(metric.capitalize(), fontsize=12)
        ax.set_title(title, fontsize=16, pad=20)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(0.5)
        ax.spines['bottom'].set_linewidth(0.5)
        ax.tick_params(axis='x', labelsize=12)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_ylim(0, max(p1_value, p2_value) * 1.2)  # Add 20% padding above the highest bar
        
        # Set background color
        fig.set_facecolor('white')
        ax.set_facecolor('#f8f9fa')
        
        # Add grid lines for better readability
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        
        # Convert to base64 for display
        comparison_chart = matplotlib_plot_as_base64(fig)
        
        return html.Div([
            html.Div([
                html.H5("⚖️ Player Comparison", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                html.Span(" ℹ️", style={
                    'marginLeft': '10px', 
                    'cursor': 'pointer', 
                    'fontSize': '16px',
                    'color': '#3498db'
                }, title=f"Direct comparison of {metric} between players")
            ]),
            html.P([
                "This chart directly compares ", 
                html.Strong(player1), 
                " (", html.Span(team1, style={'color': '#3498db'}), ") and ",
                html.Strong(player2),
                " (", html.Span(team2, style={'color': '#e74c3c'}), ") in terms of ",
                html.Span(metric_description),
                ". The bar heights represent the raw count values, providing a clear visual and numerical comparison between these players' performance in this specific metric."
            ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
            html.Details([
                html.Summary("📖 Visualization Design Rationale", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                html.Div([
                    html.P(["• ", html.Strong("Direct Comparison Format:"), " Bar charts provide the clearest visual comparison between two discrete values, allowing for immediate assessment of relative performance in this specific metric."], style={'margin': '12px 0', 'fontSize': '13px'}),
                    html.P(["• ", html.Strong("Color Differentiation:"), " Distinct colors for each player maintain their identity across the dashboard while providing sufficient contrast for accessibility and visual distinction."], style={'margin': '12px 0', 'fontSize': '13px'}),
                    html.P(["• ", html.Strong("Dual Labeling:"), " The combination of player names and team affiliations provides complete context for interpretation, especially when comparing players from different teams."], style={'margin': '12px 0', 'fontSize': '13px'}),
                    html.P(["• ", html.Strong("Alternatives Considered:"), " While a radar chart could compare multiple metrics simultaneously, the single-metric bar chart provides greater precision and clarity for focused comparison on the selected dimension."], style={'margin': '12px 0', 'fontSize': '13px'})
                ], style={'paddingLeft': '15px', 'marginTop': '8px'})
            ], style={'marginTop': '10px'}),
            html.Img(style={'width': '100%', 'maxWidth': '800px', 'margin': '0 auto', 'display': 'block'}, src=comparison_chart)
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'})

        
    except Exception as e:
        return html.P(f"Error creating comparison: {str(e)}")
