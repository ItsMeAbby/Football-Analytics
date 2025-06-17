import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.data_loader import load_euro_2024_matches, load_match_data, get_all_teams
from utils.plot_utils_mpl import create_pass_network

def layout():
    return html.Div([
        # Header
        html.Div([
            html.H2("⚡ Tactical Analysis Dashboard", className="text-center mb-4"),
            html.P("Advanced tactical insights including formations, passing patterns, and team shape analysis", 
                   className="text-center text-muted")
        ], className="mb-4"),
        
        # Team and match selection
        html.Div([
            html.H4("🎯 Analysis Selection", className="mb-3"),
            html.Div([
                html.Div([
                    html.Label("Select Team:", className="fw-bold"),
                    dcc.Dropdown(
                        id='tactical-team-dropdown',
                        options=[],
                        placeholder="Select a team...",
                        className="mb-2"
                    )
                ], className="col-md-4"),
                html.Div([
                    html.Label("Select Match:", className="fw-bold"),
                    dcc.Dropdown(
                        id='tactical-match-dropdown',
                        placeholder="Select a match...",
                        className="mb-2"
                    )
                ], className="col-md-4"),
                html.Div([
                    html.Label("Analysis Type:", className="fw-bold"),
                    dcc.Dropdown(
                        id='analysis-type-dropdown',
                        options=[
                            {'label': 'Formation Analysis', 'value': 'formation'},
                            {'label': 'Pass Network', 'value': 'pass_network'},
                            {'label': 'Defensive Actions', 'value': 'defensive'},
                            {'label': 'Attacking Patterns', 'value': 'attacking'},
                            {'label': 'Set Pieces', 'value': 'set_pieces'}
                        ],
                        value='formation',
                        className="mb-2"
                    )
                ], className="col-md-4"),
            ], className="row")
        ], className="card p-3 mb-4"),
        
        # Tactical insights summary
        html.Div(id='tactical-summary', className="mb-4"),
        
        # Main tactical visualization
        html.Div([
            html.H4("📊 Tactical Visualization", className="mb-3"),
            dcc.Graph(id='tactical-viz', style={'height': '600px'})
        ], className="card p-3 mb-4"),
        
        # Secondary analysis
        html.Div([
            html.H4("🔍 Detailed Analysis", className="mb-3"),
            html.Div([
                html.Div([
                    dcc.Graph(id='secondary-viz-1')
                ], className="col-md-6"),
                html.Div([
                    dcc.Graph(id='secondary-viz-2')
                ], className="col-md-6"),
            ], className="row")
        ], className="card p-3 mb-4"),
        
        # Team comparison
        html.Div([
            html.H4("⚖️ Team Comparison", className="mb-3"),
            dcc.Graph(id='team-comparison-viz')
        ], className="card p-3"),
        
    ], className="container-fluid p-4")

@callback(
    Output('tactical-team-dropdown', 'options'),
    Input('tactical-team-dropdown', 'id')
)
def update_tactical_team_options(_):
    teams = get_all_teams()
    return [{'label': team, 'value': team} for team in teams]

@callback(
    Output('tactical-match-dropdown', 'options'),
    Output('tactical-match-dropdown', 'value'),
    Input('tactical-team-dropdown', 'value')
)
def update_tactical_match_options(selected_team):
    if not selected_team:
        return [], None
    
    matches = load_euro_2024_matches()
    team_matches = matches[
        (matches['home_team'] == selected_team) | 
        (matches['away_team'] == selected_team)
    ].sort_values('match_date')
    
    options = []
    for _, match in team_matches.iterrows():
        label = f"{match['home_team']} vs {match['away_team']} ({match['match_date']})"
        options.append({'label': label, 'value': match['match_id']})
    
    return options, options[0]['value'] if options else None

@callback(
    Output('tactical-summary', 'children'),
    Input('tactical-team-dropdown', 'value'),
    Input('tactical-match-dropdown', 'value')
)
def update_tactical_summary(team, match_id):
    if not team or not match_id:
        return html.P("Please select a team and match for tactical analysis.")
    
    try:
        events_df = load_match_data(match_id)
        matches = load_euro_2024_matches()
        match_info = matches[matches['match_id'] == match_id].iloc[0]
        
        # Filter events for the selected team
        team_events = events_df[
            events_df['team'].apply(
                lambda x: x.get('name', '') == team if isinstance(x, dict) else str(x) == team
            )
        ]
        
        # Calculate tactical metrics
        total_passes = len(team_events[team_events['type'] == 'Pass'])
        successful_passes = len(team_events[
            (team_events['type'] == 'Pass') & 
            (team_events['pass_outcome'].isna())
        ])
        pass_accuracy = (successful_passes / total_passes * 100) if total_passes > 0 else 0
        
        # Possession zones
        attacking_third_events = len(team_events[team_events['x'] > 80])
        middle_third_events = len(team_events[(team_events['x'] >= 40) & (team_events['x'] <= 80)])
        defensive_third_events = len(team_events[team_events['x'] < 40])
        
        total_events = attacking_third_events + middle_third_events + defensive_third_events
        
        # Defensive actions
        defensive_actions = len(team_events[
            team_events['type'].isin(['Tackle', 'Interception', 'Block', 'Clearance'])
        ])
        
        return html.Div([
            html.H4(f"📈 Tactical Summary - {team}", className="text-center text-primary"),
            html.Div([
                html.Div([
                    html.H3(f"{pass_accuracy:.1f}%", className="text-success text-center"),
                    html.P("Pass Accuracy", className="text-center text-muted")
                ], className="col-md-2"),
                html.Div([
                    html.H3(f"{total_passes}", className="text-info text-center"),
                    html.P("Total Passes", className="text-center text-muted")
                ], className="col-md-2"),
                html.Div([
                    html.H3(f"{attacking_third_events}", className="text-warning text-center"),
                    html.P("Attacking Third", className="text-center text-muted")
                ], className="col-md-2"),
                html.Div([
                    html.H3(f"{middle_third_events}", className="text-primary text-center"),
                    html.P("Middle Third", className="text-center text-muted")
                ], className="col-md-2"),
                html.Div([
                    html.H3(f"{defensive_third_events}", className="text-secondary text-center"),
                    html.P("Defensive Third", className="text-center text-muted")
                ], className="col-md-2"),
                html.Div([
                    html.H3(f"{defensive_actions}", className="text-danger text-center"),
                    html.P("Defensive Actions", className="text-center text-muted")
                ], className="col-md-2"),
            ], className="row")
        ], className="card p-3")
        
    except Exception as e:
        return html.Div([
            html.P(f"Error loading tactical summary: {str(e)}", className="text-danger")
        ])

@callback(
    Output('tactical-viz', 'figure'),
    Input('tactical-team-dropdown', 'value'),
    Input('tactical-match-dropdown', 'value'),
    Input('analysis-type-dropdown', 'value')
)
def update_tactical_visualization(team, match_id, analysis_type):
    if not team or not match_id:
        return go.Figure().add_annotation(text="Select team and match for analysis", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    try:
        events_df = load_match_data(match_id)
        
        if analysis_type == 'formation':
            return create_formation_analysis(events_df, team)
        elif analysis_type == 'pass_network':
            return create_pass_network(events_df, team)
        elif analysis_type == 'defensive':
            return create_defensive_analysis(events_df, team)
        elif analysis_type == 'attacking':
            return create_attacking_analysis(events_df, team)
        elif analysis_type == 'set_pieces':
            return create_set_piece_analysis(events_df, team)
        
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error: {str(e)}", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)

def create_formation_analysis(events_df, team):
    """Create formation and average position visualization"""
    # Filter events for the team
    team_events = events_df[
        events_df['team'].apply(
            lambda x: x.get('name', '') == team if isinstance(x, dict) else str(x) == team
        )
    ]
    
    # Calculate average positions for starting XI
    starting_events = team_events[team_events['minute'] <= 15]  # First 15 minutes
    
    avg_positions = starting_events.groupby('player').agg({
        'x': 'mean',
        'y': 'mean'
    }).reset_index()
    
    # Get positions
    player_positions = starting_events.groupby('player')['position'].first().reset_index()
    avg_positions = avg_positions.merge(player_positions, on='player')
    
    fig = go.Figure()
    
    # Add pitch background
    fig.add_shape(type="rect", x0=0, y0=0, x1=120, y1=80, 
                  line=dict(color="white", width=2), fillcolor="green")
    
    # Add center line
    fig.add_shape(type="line", x0=60, y0=0, x1=60, y1=80, 
                  line=dict(color="white", width=2))
    
    # Add player positions with different colors by position
    position_colors = {
        'Goalkeeper': 'yellow',
        'Centre-Back': 'blue',
        'Left-Back': 'lightblue',
        'Right-Back': 'lightblue',
        'Defensive Midfield': 'green',
        'Central Midfield': 'orange',
        'Attacking Midfield': 'red',
        'Left Winger': 'purple',
        'Right Winger': 'purple',
        'Centre-Forward': 'darkred'
    }
    
    for _, player in avg_positions.iterrows():
        position = player['position'].get('name', 'Unknown') if isinstance(player['position'], dict) else str(player['position'])
        color = position_colors.get(position, 'gray')
        
        player_name = player['player'].get('name', 'Unknown') if isinstance(player['player'], dict) else str(player['player'])
        
        fig.add_trace(go.Scatter(
            x=[player['x']],
            y=[player['y']],
            mode='markers+text',
            marker=dict(size=20, color=color, line=dict(width=2, color='black')),
            text=player_name[:3],
            textposition='middle center',
            name=position,
            showlegend=False,
            hovertemplate=f'{player_name}<br>Position: {position}<br>Avg Position: ({player["x"]:.1f}, {player["y"]:.1f})<extra></extra>'
        ))
    
    fig.update_layout(
        title=f"Average Formation - {team}",
        xaxis=dict(range=[0, 120], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 80], showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='green',
        height=600
    )
    
    return fig

def create_defensive_analysis(events_df, team):
    """Create defensive actions heatmap"""
    defensive_events = events_df[
        (events_df['team'].apply(
            lambda x: x.get('name', '') == team if isinstance(x, dict) else str(x) == team
        )) &
        (events_df['type'].isin(['Tackle', 'Interception', 'Block', 'Clearance', 'Foul Committed']))
    ]
    
    if defensive_events.empty:
        return go.Figure().add_annotation(text="No defensive data available", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Create heatmap
    x_bins = np.linspace(0, 120, 13)
    y_bins = np.linspace(0, 80, 9)
    
    hist, x_edges, y_edges = np.histogram2d(
        defensive_events['x'].dropna(), 
        defensive_events['y'].dropna(), 
        bins=[x_bins, y_bins]
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=hist.T,
        x=x_edges[:-1],
        y=y_edges[:-1],
        colorscale='Blues',
        opacity=0.8
    ))
    
    # Add pitch outline
    fig.add_shape(type="rect", x0=0, y0=0, x1=120, y1=80, 
                  line=dict(color="white", width=2), fill=None)
    
    fig.update_layout(
        title=f"Defensive Actions Heatmap - {team}",
        xaxis=dict(range=[0, 120], title="", showticklabels=False),
        yaxis=dict(range=[0, 80], title="", showticklabels=False),
        height=600
    )
    
    return fig

def create_attacking_analysis(events_df, team):
    """Create attacking patterns visualization"""
    attacking_events = events_df[
        (events_df['team'].apply(
            lambda x: x.get('name', '') == team if isinstance(x, dict) else str(x) == team
        )) &
        (events_df['type'].isin(['Shot', 'Dribble', 'Pass'])) &
        (events_df['x'] > 80)  # Final third
    ]
    
    if attacking_events.empty:
        return go.Figure().add_annotation(text="No attacking data available", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    fig = go.Figure()
    
    # Add pitch background (final third only)
    fig.add_shape(type="rect", x0=80, y0=0, x1=120, y1=80, 
                  line=dict(color="white", width=2), fillcolor="green")
    
    # Add different markers for different event types
    event_colors = {'Shot': 'red', 'Dribble': 'orange', 'Pass': 'blue'}
    
    for event_type in ['Shot', 'Dribble', 'Pass']:
        type_events = attacking_events[attacking_events['type'] == event_type]
        if not type_events.empty:
            fig.add_trace(go.Scatter(
                x=type_events['x'],
                y=type_events['y'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=event_colors[event_type],
                    opacity=0.7
                ),
                name=event_type,
                hovertemplate=f'{event_type}<br>Position: (%{{x:.1f}}, %{{y:.1f}})<extra></extra>'
            ))
    
    fig.update_layout(
        title=f"Final Third Attacking Actions - {team}",
        xaxis=dict(range=[80, 120], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 80], showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='green',
        height=600
    )
    
    return fig

def create_set_piece_analysis(events_df, team):
    """Analyze set piece situations"""
    set_pieces = events_df[
        (events_df['team'].apply(
            lambda x: x.get('name', '') == team if isinstance(x, dict) else str(x) == team
        )) &
        (events_df['type'] == 'Pass') &
        (events_df['pass_type'].apply(
            lambda x: x.get('name', '') in ['Corner', 'Free Kick', 'Throw-in'] if isinstance(x, dict) else False
        ))
    ]
    
    if set_pieces.empty:
        return go.Figure().add_annotation(text="No set piece data available", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Count set pieces by type
    set_piece_counts = set_pieces['pass_type'].apply(
        lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else 'Unknown'
    ).value_counts()
    
    fig = go.Figure(go.Bar(
        x=set_piece_counts.index,
        y=set_piece_counts.values,
        marker=dict(color=['gold', 'silver', 'bronze'][:len(set_piece_counts)])
    ))
    
    fig.update_layout(
        title=f"Set Piece Distribution - {team}",
        xaxis_title="Set Piece Type",
        yaxis_title="Number of Set Pieces",
        height=400
    )
    
    return fig

@callback(
    Output('secondary-viz-1', 'figure'),
    Output('secondary-viz-2', 'figure'),
    Input('tactical-team-dropdown', 'value'),
    Input('tactical-match-dropdown', 'value')
)
def update_secondary_visualizations(team, match_id):
    if not team or not match_id:
        empty_fig = go.Figure().add_annotation(text="Select team and match", 
                                             xref="paper", yref="paper", x=0.5, y=0.5)
        return empty_fig, empty_fig
    
    try:
        events_df = load_match_data(match_id)
        
        # Viz 1: Pass length distribution
        team_passes = events_df[
            (events_df['team'].apply(
                lambda x: x.get('name', '') == team if isinstance(x, dict) else str(x) == team
            )) &
            (events_df['type'] == 'Pass') &
            (events_df['pass_outcome'].isna())
        ]
        
        if not team_passes.empty:
            # Calculate pass lengths
            pass_lengths = []
            for _, pass_event in team_passes.iterrows():
                if pd.notna(pass_event['x']) and pd.notna(pass_event['pass_end_x']):
                    length = np.sqrt(
                        (pass_event['pass_end_x'] - pass_event['x'])**2 + 
                        (pass_event['pass_end_y'] - pass_event['y'])**2
                    )
                    pass_lengths.append(length)
            
            fig1 = go.Figure(go.Histogram(
                x=pass_lengths,
                nbinsx=20,
                marker=dict(color='lightblue', line=dict(color='darkblue', width=1))
            ))
            fig1.update_layout(
                title="Pass Length Distribution",
                xaxis_title="Pass Length (meters)",
                yaxis_title="Frequency"
            )
        else:
            fig1 = go.Figure().add_annotation(text="No pass data", 
                                            xref="paper", yref="paper", x=0.5, y=0.5)
        
        # Viz 2: Event timeline
        team_events = events_df[
            events_df['team'].apply(
                lambda x: x.get('name', '') == team if isinstance(x, dict) else str(x) == team
            )
        ]
        
        if not team_events.empty:
            events_by_minute = team_events.groupby('minute').size().reset_index(name='count')
            
            fig2 = go.Figure(go.Scatter(
                x=events_by_minute['minute'],
                y=events_by_minute['count'],
                mode='lines+markers',
                line=dict(color='green', width=2),
                marker=dict(size=6)
            ))
            fig2.update_layout(
                title="Event Activity Timeline",
                xaxis_title="Match Minute",
                yaxis_title="Events per Minute"
            )
        else:
            fig2 = go.Figure().add_annotation(text="No event data", 
                                            xref="paper", yref="paper", x=0.5, y=0.5)
        
        return fig1, fig2
        
    except Exception as e:
        error_fig = go.Figure().add_annotation(text=f"Error: {str(e)}", 
                                             xref="paper", yref="paper", x=0.5, y=0.5)
        return error_fig, error_fig

@callback(
    Output('team-comparison-viz', 'figure'),
    Input('tactical-match-dropdown', 'value')
)
def update_team_comparison(match_id):
    if not match_id:
        return go.Figure().add_annotation(text="Select a match for team comparison", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    try:
        events_df = load_match_data(match_id)
        matches = load_euro_2024_matches()
        match_info = matches[matches['match_id'] == match_id].iloc[0]
        
        home_team = match_info['home_team']
        away_team = match_info['away_team']
        
        # Compare key metrics
        metrics = {}
        for team in [home_team, away_team]:
            team_events = events_df[
                events_df['team'].apply(
                    lambda x: x.get('name', '') == team if isinstance(x, dict) else str(x) == team
                )
            ]
            
            metrics[team] = {
                'Passes': len(team_events[team_events['type'] == 'Pass']),
                'Shots': len(team_events[team_events['type'] == 'Shot']),
                'Tackles': len(team_events[team_events['type'] == 'Tackle']),
                'Dribbles': len(team_events[team_events['type'] == 'Dribble']),
                'Fouls': len(team_events[team_events['type'] == 'Foul Committed'])
            }
        
        # Create comparison chart
        metric_names = list(metrics[home_team].keys())
        home_values = list(metrics[home_team].values())
        away_values = list(metrics[away_team].values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=home_team,
            x=metric_names,
            y=home_values,
            marker=dict(color='lightblue')
        ))
        
        fig.add_trace(go.Bar(
            name=away_team,
            x=metric_names,
            y=away_values,
            marker=dict(color='lightcoral')
        ))
        
        fig.update_layout(
            title=f"Team Comparison: {home_team} vs {away_team}",
            barmode='group',
            height=400
        )
        
        return fig
        
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error: {str(e)}", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
