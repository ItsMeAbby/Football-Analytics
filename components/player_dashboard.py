import matplotlib
matplotlib.use('Agg')
import dash
from dash import dcc, html, Input, Output, callback, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.data_loader import load_tournament_data, get_all_teams
from utils.plot_utils_mpl import create_shot_map, create_heatmap, create_progressive_passes_viz

def layout():
    return html.Div([
        # Header
        html.Div([
            html.H2("🏃‍♂️ Player Performance Dashboard", className="text-center mb-4"),
            html.P("Analyze individual player performances throughout Euro 2024", 
                   className="text-center text-muted")
        ], className="mb-4"),
        
        # Player selection
        html.Div([
            html.H4("🔍 Player Selection", className="mb-3"),
            html.Div([
                html.Div([
                    html.Label("Select Team:", className="fw-bold"),
                    dcc.Dropdown(
                        id='player-team-dropdown',
                        options=[],
                        placeholder="Select a team...",
                        className="mb-2"
                    )
                ], className="col-md-6"),
                html.Div([
                    html.Label("Select Player:", className="fw-bold"),
                    dcc.Dropdown(
                        id='player-dropdown',
                        placeholder="Select a player...",
                        className="mb-2"
                    )
                ], className="col-md-6"),
            ], className="row")
        ], className="card p-3 mb-4"),
        
        # Player stats summary
        html.Div(id='player-stats-summary', className="mb-4"),
        
        # Player visualizations
        html.Div([
            html.H4("📊 Player Analysis", className="mb-3"),
            dcc.Tabs([
                dcc.Tab(label="🎯 Shot Analysis", value="shots-tab"),
                dcc.Tab(label="🔥 Touch Heatmap", value="heatmap-tab"),
                dcc.Tab(label="⚡ Progressive Actions", value="progressive-tab"),
                dcc.Tab(label="📈 Performance Metrics", value="metrics-tab"),
            ], id="player-tabs", value="shots-tab"),
            html.Div(id='player-viz-content', className="mt-3")
        ], className="card p-3 mb-4"),
        
        # Player comparison
        html.Div([
            html.H4("⚖️ Player Comparison", className="mb-3"),
            html.Div([
                html.Div([
                    html.Label("Compare with Player:", className="fw-bold"),
                    dcc.Dropdown(
                        id='comparison-player-dropdown',
                        placeholder="Select a player to compare...",
                        className="mb-2"
                    )
                ], className="col-md-6"),
                html.Div([
                    html.Label("Comparison Metric:", className="fw-bold"),
                    dcc.Dropdown(
                        id='comparison-metric-dropdown',
                        options=[
                            {'label': 'Goals', 'value': 'goals'},
                            {'label': 'Shots', 'value': 'shots'},
                            {'label': 'Passes', 'value': 'passes'},
                            {'label': 'Dribbles', 'value': 'dribbles'}
                        ],
                        value='goals',
                        className="mb-2"
                    )
                ], className="col-md-6"),
            ], className="row"),
            html.Div(id='player-comparison-content', className="mt-3")
        ], className="card p-3"),
        
    ], className="container-fluid p-4")

@callback(
    Output('player-team-dropdown', 'options'),
    Input('player-team-dropdown', 'id')
)
def update_team_options(_):
    teams = get_all_teams()
    return [{'label': team, 'value': team} for team in teams]

@callback(
    Output('player-dropdown', 'options'),
    Output('player-dropdown', 'value'),
    Input('player-team-dropdown', 'value')
)
def update_player_options(selected_team):
    if not selected_team:
        return [], None
    
    try:
        # Load tournament data and filter by team
        events_df = load_tournament_data()
        team_events = events_df[
            events_df['team'].apply(
                lambda x: x.get('name', '') == selected_team if isinstance(x, dict) else str(x) == selected_team
            )
        ]
        
        # Get unique players
        players = team_events['player'].apply(
            lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
        ).unique()
        players = [p for p in players if p != 'Unknown' and pd.notna(p)]
        players.sort()
        
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
        # Load all players from tournament
        events_df = load_tournament_data()
        players = events_df['player'].apply(
            lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
        ).unique()
        players = [p for p in players if p != 'Unknown' and pd.notna(p)]
        players.sort()
        
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
            html.H4(f"📋 {selected_player} - {team_name}", className="text-center text-primary"),
            html.Div([
                html.Div([
                    html.H3(f"{goals}", className="text-success text-center"),
                    html.P("Goals", className="text-center text-muted")
                ], className="col-md-2"),
                html.Div([
                    html.H3(f"{shots}", className="text-info text-center"),
                    html.P("Shots", className="text-center text-muted")
                ], className="col-md-2"),
                html.Div([
                    html.H3(f"{passes}", className="text-warning text-center"),
                    html.P("Passes", className="text-center text-muted")
                ], className="col-md-2"),
                html.Div([
                    html.H3(f"{pass_accuracy:.1f}%", className="text-primary text-center"),
                    html.P("Pass Accuracy", className="text-center text-muted")
                ], className="col-md-2"),
                html.Div([
                    html.H3(f"{total_events}", className="text-secondary text-center"),
                    html.P("Total Actions", className="text-center text-muted")
                ], className="col-md-2"),
                html.Div([
                    html.H3(f"{(goals/shots*100) if shots > 0 else 0:.1f}%", className="text-danger text-center"),
                    html.P("Shot Accuracy", className="text-center text-muted")
                ], className="col-md-2"),
            ], className="row")
        ], className="card p-3")
        
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
            return html.Img(style={'width': '80%', 'max-width': '800px'},src=shot_map)
        
        elif active_tab == "heatmap-tab":
            heatmap = create_heatmap(events_df, selected_player)
            return html.Img(style={'width': '80%', 'max-width': '800px'},src=heatmap)
        
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
                return html.Img(style={'width': '80%', 'max-width': '800px'},src=prog_viz)
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
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=list(normalized_metrics.values()),
                theta=list(normalized_metrics.keys()),
                fill='toself',
                name=selected_player,
                line=dict(color='blue')
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                title=f"Performance Radar - {selected_player}",
                height=500
            )
            

            return html.Img(style={'width': '80%', 'max-width': '800px'},src=fig)

            
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
            
        elif metric == 'shots':
            p1_value = len(player1_events[player1_events['type'] == 'Shot'])
            p2_value = len(player2_events[player2_events['type'] == 'Shot'])
            title = "Shots Comparison"
            
        elif metric == 'passes':
            p1_value = len(player1_events[player1_events['type'] == 'Pass'])
            p2_value = len(player2_events[player2_events['type'] == 'Pass'])
            title = "Passes Comparison"
            
        elif metric == 'dribbles':
            p1_value = len(player1_events[player1_events['type'] == 'Dribble'])
            p2_value = len(player2_events[player2_events['type'] == 'Dribble'])
            title = "Dribbles Comparison"
        
        # Create comparison chart
        fig = go.Figure(go.Bar(
            x=[player1, player2],
            y=[p1_value, p2_value],
            marker=dict(color=['lightblue', 'lightcoral'])
        ))
        
        fig.update_layout(
            title=title,
            yaxis_title=metric.capitalize(),
            height=400
        )
        
        
        return html.Img(style={'width': '80%', 'max-width': '800px'},src=fig)

        
    except Exception as e:
        return html.P(f"Error creating comparison: {str(e)}")
