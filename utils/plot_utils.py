import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io
import base64

def _draw_pitch_plotly(fig):
    """Draws a detailed soccer pitch background on a Plotly figure."""
    pitch_length_x = 120
    pitch_width_y = 80

    pitch_color = '#388E3C'  # A darker, more realistic green
    line_color = 'white'
    line_width = 2

    # Outer box (pitch boundary)
    fig.add_shape(type="rect", x0=0, y0=0, x1=pitch_length_x, y1=pitch_width_y,
                  line=dict(color=line_color, width=line_width), fillcolor=pitch_color, layer="below")

    # Halfway line
    fig.add_shape(type="line", x0=pitch_length_x/2, y0=0, x1=pitch_length_x/2, y1=pitch_width_y,
                  line=dict(color=line_color, width=line_width))

    # Center circle
    fig.add_shape(type="circle", xref="x", yref="y",
                  x0=pitch_length_x/2 - 10, y0=pitch_width_y/2 - 10,
                  x1=pitch_length_x/2 + 10, y1=pitch_width_y/2 + 10,
                  line=dict(color=line_color, width=line_width))

    # Center dot
    fig.add_trace(go.Scatter(x=[pitch_length_x/2], y=[pitch_width_y/2],
                             mode='markers', marker=dict(size=4, color=line_color),
                             showlegend=False, hoverinfo='skip', name='Center Point'))

    # Penalty areas & D-areas
    # Left Penalty Area
    fig.add_shape(type="rect", x0=0, y0=24, x1=18, y1=56,
                  line=dict(color=line_color, width=line_width))
    # Left 6-yard box
    fig.add_shape(type="rect", x0=0, y0=30, x1=6, y1=50,
                  line=dict(color=line_color, width=line_width))
    # Left Penalty Spot
    fig.add_trace(go.Scatter(x=[12], y=[40], mode='markers', marker=dict(size=4, color=line_color),
                             showlegend=False, hoverinfo='skip', name='Left Penalty Spot'))
    # Left D
    fig.add_shape(type="path",
                  path=f'M {18} {40 - 10} A {10} {10} 0 0 1 {18} {40 + 10}',
                  line=dict(color=line_color, width=line_width))

    # Right Penalty Area
    fig.add_shape(type="rect", x0=pitch_length_x - 18, y0=24, x1=pitch_length_x, y1=56,
                  line=dict(color=line_color, width=line_width))
    # Right 6-yard box
    fig.add_shape(type="rect", x0=pitch_length_x - 6, y0=30, x1=pitch_length_x, y1=50,
                  line=dict(color=line_color, width=line_width))
    # Right Penalty Spot
    fig.add_trace(go.Scatter(x=[pitch_length_x - 12], y=[40], mode='markers', marker=dict(size=4, color=line_color),
                             showlegend=False, hoverinfo='skip', name='Right Penalty Spot'))
    # Right D
    fig.add_shape(type="path",
                  path=f'M {pitch_length_x - 18} {40 - 10} A {10} {10} 0 0 0 {pitch_length_x - 18} {40 + 10}',
                  line=dict(color=line_color, width=line_width))

    # Goals (Adjusted for visual representation, actual goal depth is usually small)
    fig.add_trace(go.Scatter(x=[120, 120], y=[36, 44], mode='lines', line=dict(color="white", width=4), showlegend=False, hoverinfo='skip', name='Right Goal'))
    fig.add_trace(go.Scatter(x=[0, 0], y=[36, 44], mode='lines', line=dict(color="white", width=4), showlegend=False, hoverinfo='skip', name='Left Goal'))

    fig.update_layout(
        xaxis=dict(range=[0, pitch_length_x], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, pitch_width_y], showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background as pitch is drawn with shape
        paper_bgcolor='#E0E0E0'  # Light gray background for the entire plot area
    )

def create_shot_map(events_df, team_name, player_name=None):
    """Create an interactive shot map using Plotly"""
    # Filter shots for the team
    if isinstance(events_df, dict) and 'shots' in events_df:
        shots_df = events_df['shots']
    else:
        shots_df = events_df[events_df['type'] == 'Shot'].copy()
    
    if team_name:
        team_shots = shots_df[shots_df['team'].apply(
            lambda x: x.get('name', '') == team_name if isinstance(x, dict) else str(x) == team_name
        )]
    else:
        team_shots = shots_df
    
    if player_name:
        team_shots = team_shots[team_shots['player'].apply(
            lambda x: x.get('name', '') == player_name if isinstance(x, dict) else str(x) == player_name
        )]
    
    if team_shots.empty:
        return go.Figure().add_annotation(text="No shot data available", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Extract coordinates and xG values
    x_coords = []
    y_coords = []
    xg_values = []
    outcomes = []
    
    for _, shot in team_shots.iterrows():
        if isinstance(shot['location'], list) and len(shot['location']) >= 2:
            x_coords.append(shot['location'][0])
            y_coords.append(shot['location'][1])
            xg_values.append(shot.get('shot_statsbomb_xg', 0))
            outcomes.append(shot.get('shot_outcome', {}).get('name', 'Unknown') if isinstance(shot.get('shot_outcome'), dict) else str(shot.get('shot_outcome', 'Unknown')))
    
    # Create figure
    fig = go.Figure()
    
    # Add detailed pitch background
    _draw_pitch_plotly(fig)
    
    # Color code by outcome
    colors = {
        'Goal': '#FFD700',       # Gold
        'Saved': '#87CEEB',      # SkyBlue
        'Off T': '#FF6347',      # Tomato (reddish)
        'Blocked': '#FFA07A',    # LightSalmon (orange-ish)
        'Wayward': '#D3D3D3',    # LightGray
        'Post': '#A0522D',       # Sienna (brownish)
        'Saved Goal': '#20B2AA', # LightSeaGreen (lighter green)
        'Other': '#6A5ACD'       # SlateBlue
    }
    
    for outcome in sorted(list(set(outcomes))): # Sort for consistent legend order
        mask = [o == outcome for o in outcomes]
        if any(mask):
            x_filtered = [x for i, x in enumerate(x_coords) if mask[i]]
            y_filtered = [y for i, y in enumerate(y_coords) if mask[i]]
            xg_filtered = [xg for i, xg in enumerate(xg_values) if mask[i]]
            
            fig.add_trace(go.Scatter(
                x=x_filtered, y=y_filtered,
                mode='markers',
                marker=dict(
                    size=[max(6, xg*25) for xg in xg_filtered], # Adjusted size multiplier slightly
                    color=colors.get(outcome, 'gray'),
                    opacity=0.8,
                    line=dict(width=1, color='black')
                ),
                name=outcome,
                text=[f'xG: {xg:.2f}' + (f', Outcome: {outcome}' if outcome != 'Goal' else ', GOAL!') for xg in xg_filtered],
                hovertemplate='%{text}<extra></extra>' # Simpler hovertemplate
            ))
    
    fig.update_layout(
        title=f"<b>Shot Map - {team_name}</b>" + (f"<br><i>{player_name}</i>" if player_name else ""),
        height=550, # Slightly increased height for better view
        showlegend=True,
        legend_title_text='Shot Outcome'
    )
    
    return fig

def create_pass_network(events_df, team_name, match_id=None):
    """Create a pass network visualization"""
    # Filter passes for the team
    passes_df = events_df[
        (events_df['type'] == 'Pass') & 
        (events_df['team'].apply(
            lambda x: x.get('name', '') == team_name if isinstance(x, dict) else str(x) == team_name
        )) &
        (events_df['pass_outcome'].isna())  # Only successful passes
    ].copy()
    
    if passes_df.empty:
        return go.Figure().add_annotation(text="No pass data available", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Calculate average positions
    avg_positions_list = []
    for player_val in passes_df['player'].unique():
        player_name = player_val.get('name', 'Unknown') if isinstance(player_val, dict) else str(player_val)
        player_passes = passes_df[passes_df['player'].apply(
            lambda x: x.get('name', '') == player_name if isinstance(x, dict) else str(x) == player_name
        )]
        if not player_passes.empty:
            avg_positions_list.append({
                'player_name': player_name,
                'x': player_passes['x'].mean(),
                'y': player_passes['y'].mean()
            })
    avg_positions = pd.DataFrame(avg_positions_list)

    if avg_positions.empty:
        return go.Figure().add_annotation(text="Could not calculate average player positions", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Calculate pass connections (player to pass_recipient)
    pass_connections_list = []
    for index, row in passes_df.iterrows():
        passer_name = row['player'].get('name', 'Unknown') if isinstance(row['player'], dict) else str(row['player'])
        recipient_name = row['pass_recipient'].get('name', 'Unknown') if isinstance(row['pass_recipient'], dict) else str(row['pass_recipient'])
        pass_connections_list.append({'passer': passer_name, 'recipient': recipient_name})
    
    pass_connections_df = pd.DataFrame(pass_connections_list)
    pass_connections = pass_connections_df.groupby(['passer', 'recipient']).size().reset_index(name='passes')
    pass_connections = pass_connections[pass_connections['passes'] >= 3]  # Minimum 3 passes

    fig = go.Figure()
    
    # Add detailed pitch background
    _draw_pitch_plotly(fig)
    
    # Add pass connections
    for _, connection in pass_connections.iterrows():
        passer_pos = avg_positions[avg_positions['player_name'] == connection['passer']]
        receiver_pos = avg_positions[avg_positions['player_name'] == connection['recipient']]
        
        if not passer_pos.empty and not receiver_pos.empty:
            fig.add_trace(go.Scatter(
                x=[passer_pos.iloc[0]['x'], receiver_pos.iloc[0]['x']],
                y=[passer_pos.iloc[0]['y'], receiver_pos.iloc[0]['y']],
                mode='lines',
                line=dict(width=connection['passes']/1.5, color='rgba(255,255,255,0.7)'), # Thicker lines, higher opacity
                showlegend=False,
                hoverinfo='text',
                text=f"{connection['passer']} to {connection['recipient']}: {connection['passes']} passes",
                name=f"Passes: {connection['passes']}" # Tooltip name
            ))
    
    # Add player positions
    fig.add_trace(go.Scatter(
        x=avg_positions['x'],
        y=avg_positions['y'],
        mode='markers+text',
        marker=dict(size=20, color='gold', line=dict(width=2, color='darkblue')), # Yellow/Gold markers
        text=[p_name.split()[-1] if ' ' in p_name else p_name for p_name in avg_positions['player_name']], # Use last name or full name
        textfont=dict(color='black', size=10), # Black text for better contrast
        textposition='middle center',
        name='Players',
        hovertemplate='<b>%{text}</b><br>Avg X: %{x:.1f}<br>Avg Y: %{y:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"<b>Pass Network - {team_name}</b>",
        height=550,
        showlegend=False
    )
    
    return fig

def create_heatmap(events_df, player_name, event_types=None):
    """Create a player heatmap"""
    if event_types is None:
        event_types = ['Pass', 'Ball Receipt*', 'Carry', 'Clearance', 'Foul Won', 'Block',
                      'Ball Recovery', 'Duel', 'Dribble', 'Interception', 'Miscontrol', 'Shot']
    
    player_events = events_df[
        (events_df['player'].apply(
            lambda x: x.get('name', '') == player_name if isinstance(x, dict) else str(x) == player_name
        )) &
        (events_df['type'].isin(event_types))
    ].copy()
    
    if player_events.empty:
        return go.Figure().add_annotation(text="No event data available for this player and event types.", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Create bins for heatmap
    x_bins = np.linspace(0, 120, 16) # More bins for higher resolution
    y_bins = np.linspace(0, 80, 11)
    
    # Count events in each bin
    hist, x_edges, y_edges = np.histogram2d(
        player_events['x'].dropna(), 
        player_events['y'].dropna(), 
        bins=[x_bins, y_bins]
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=hist.T,
        x=x_edges[:-1],
        y=y_edges[:-1],
        colorscale='Hot', # Changed to 'Hot' for a fiery look, or 'YlOrRd'
        opacity=0.7, # Slightly more transparent
        hoverongaps=False,
        hovertemplate='Intensity: %{z}<extra></extra>'
    ))
    
    # Add detailed pitch background
    _draw_pitch_plotly(fig)
    
    fig.update_layout(
         title=f"<b>Touch Heatmap - {player_name}</b>",
        height=500,
        xaxis=dict(range=[0, 120], title="", showticklabels=False),
        yaxis=dict(range=[0, 80], title="", showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='#E0E0E0'
    )
    
    return fig

def create_progressive_passes_viz(events_df, team_name):
    """Create visualization for progressive passes"""
    # Filter progressive passes (passes that move ball significantly forward)
    prog_passes = events_df[
        (events_df['type'] == 'Pass') &
        (events_df['team'].apply(
            lambda x: x.get('name', '') == team_name if isinstance(x, dict) else str(x) == team_name
        )) &
        (events_df['pass_outcome'].isna()) & # Successful passes
        (
            ((events_df['pass_end_x'] > events_df['x']) & (events_df['x'] < 75) & (events_df['pass_end_x'] - events_df['x'] >= 10)) | # In attacking 3/4, move 10m forward
            ((events_df['x'] >= 75) & (events_df['pass_end_x'] > events_df['x'])& (events_df['pass_end_x'] - events_df['x'] >= 10)) | # In final 1/4, just cross the line. 
            ((events_df['pass_end_x'] >= 102) & (events_df['x'] < 102))# Pass ends in final 18-yard box, having not started there
        ) 
    ].copy()
    
    if prog_passes.empty:
        return go.Figure().add_annotation(text="No progressive pass data available", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Count by player
    player_counts_list = []
    for player_val in prog_passes['player'].unique():
        player_name = player_val.get('name', 'Unknown') if isinstance(player_val, dict) else str(player_val)
        count = len(prog_passes[prog_passes['player'].apply(
            lambda x: x.get('name', '') == player_name if isinstance(x, dict) else str(x) == player_name
        )])
        player_counts_list.append({'player_name': player_name, 'progressive_passes': count})
    player_counts = pd.DataFrame(player_counts_list)
    player_counts = player_counts.sort_values('progressive_passes', ascending=True) # Ascending for bar chart

    
    fig = go.Figure(go.Bar(
        x=player_counts['progressive_passes'],
        y=player_counts['player_name'],
        orientation='h',
        marker=dict(color=px.colors.sequential.Plotly3_r, # Using a Plotly sequential colorscale
                    line=dict(color='darkblue', width=1)),
        hovertemplate='<b>%{y}</b><br>Progressive Passes: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"<b>Progressive Passes - {team_name}</b>",
        xaxis_title="Number of Progressive Passes",
        yaxis_title="Player",
        height=max(400, len(player_counts) * 30), # Adjust height dynamically
        margin=dict(l=150, r=20, t=70, b=70) # Adjust margins for long player names
    )
    
    return fig

def create_xg_timeline(events_df, match_info=None):
    """Create xG timeline for a match, including goal markers."""
    shots_df = events_df[events_df['type'] == 'Shot'].copy()
    
    if shots_df.empty:
        return go.Figure().add_annotation(text="No shot data available", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Sort by minute
    shots_df = shots_df.sort_values('minute')
    
    # Calculate cumulative xG by team
    teams = shots_df['team'].apply(lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)).unique()
    
    fig = go.Figure()
    
    # Define colors for teams
    team_colors = px.colors.qualitative.Plotly # A qualitative colorscale from Plotly

    for i, team in enumerate(teams):
        team_shots = shots_df[shots_df['team'].apply(
            lambda x: x.get('name', '') == team if isinstance(x, dict) else str(x) == team
        )]
        
        cumulative_xg = team_shots['shot_statsbomb_xg'].cumsum()
        
        fig.add_trace(go.Scatter(
            x=team_shots['minute'],
            y=cumulative_xg,
            mode='lines+markers',
            name=f"{team} xG",
            line=dict(width=3, color=team_colors[i % len(team_colors)]), # Assign distinct color
            marker=dict(size=8, symbol='circle'),
            hovertemplate='<b>%{fullData.name}</b><br>Minute: %{x}<br>Cumulative xG: %{y:.2f}<extra></extra>'
        ))

        # Add vertical lines for goals
        goals = team_shots[
            (team_shots['shot_outcome'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x))) == 'Goal'
        ]
        
        for _, goal in goals.iterrows():
            fig.add_vline(x=goal['minute'], line_width=1, line_dash="dash", line_color=team_colors[i % len(team_colors)],
                          annotation_text=f"Goal ({goal['player'].get('name', 'Unknown')})",
                          annotation_position="top",
                          annotation_font_color=team_colors[i % len(team_colors)]
                         )
    
    fig.update_layout(
        title="<b>Expected Goals (xG) Timeline</b>",
        xaxis_title="Minute",
        yaxis_title="Cumulative Expected Goals (xG)",
        height=500,
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)', bordercolor='white', borderwidth=1),
        plot_bgcolor='white', # Clean white background for timeline
        paper_bgcolor='#E0E0E0'
    )
    
    return fig

def save_plot_as_base64(fig):
    """Convert Plotly figure to base64 string"""
    buf = io.BytesIO()
    fig.write_image(buf, format='png', engine='kaleido', scale=2) # Use kaleido for better quality
    buf.seek(0)
    encoded = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{encoded}"