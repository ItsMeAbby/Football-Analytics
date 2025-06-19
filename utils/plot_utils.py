import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer import Pitch, VerticalPitch, Sbopen, FontManager, inset_image
import tempfile
import os

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
            
            # Different marker symbols based on outcome
            if outcome == 'Goal':
                marker_symbol = 'circle'  # Will add football emoji in text later
                marker_sizes = [max(10, (xg*1700)//100 + 10) for xg in xg_filtered]
                marker_color = colors.get(outcome, 'gold')
                opacity = 1.0
            else:
                # Use symbols with lines for non-goals
                marker_symbol = 'x'  # Alternative: 'x-open', 'cross-open'
                marker_sizes = [max(10, (xg*1700)//100) for xg in xg_filtered]
                marker_color = colors.get(outcome, 'gray')
                opacity = 0.8
            
            # Create hover text with football emoji for goals
            if outcome == 'Goal':
                hover_text = [f'⚽ GOAL! xG: {xg:.2f}' for xg in xg_filtered]
            else:
                hover_text = [f'xG: {xg:.2f}, Outcome: {outcome}' for xg in xg_filtered]
            
            fig.add_trace(go.Scatter(
                x=x_filtered, y=y_filtered,
                mode='markers',
                marker=dict(
                    size=marker_sizes,
                    color=marker_color,
                    opacity=opacity,
                    symbol=marker_symbol,
                    line=dict(width=2, color='black')
                ),
                name=outcome if outcome != 'Goal' else '⚽ Goal',
                text=hover_text,
                hovertemplate='%{text}<extra></extra>'
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
    # Get substitution data
    substitutions = events_df[events_df['type'] == 'Substitution'].copy()
    
    # Create a mapping from substituted player to replacement
    sub_mapping = {}
    for _, sub in substitutions.iterrows():
        player_name = sub['player'].get('name', 'Unknown') if isinstance(sub['player'], dict) else str(sub['player'])
        replacement_name = sub['substitution_replacement'].get('name', 'Unknown') if isinstance(sub['substitution_replacement'], dict) else str(sub['substitution_replacement'])
        sub_mapping[replacement_name] = player_name
    
    # Filter passes for the team
    passes_df = events_df[
        # PASS OR Ball Receipt
        (events_df['type'].isin(['Pass'])) &
        (events_df['team'].apply(
            lambda x: x.get('name', '') == team_name if isinstance(x, dict) else str(x) == team_name
        )) &
        (events_df['pass_outcome'].isna())  # Only successful passes
    ].copy()
    passes_df.to_csv(team_name + '_passes.csv', index=False)  # Save passes for debugging
    
    if passes_df.empty:
        return go.Figure().add_annotation(text="No pass data available", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Calculate pass connections (player to pass_recipient)
    pass_connections_list = []
    for index, row in passes_df.iterrows():
        passer_name = row['player'].get('name', 'Unknown') if isinstance(row['player'], dict) else str(row['player'])
        recipient_name = row['pass_recipient'].get('name', 'Unknown') if isinstance(row['pass_recipient'], dict) else str(row['pass_recipient'])
        
        # Map substituted players to original players
        if passer_name in sub_mapping:
            original_passer = sub_mapping[passer_name]
            pass_connections_list.append({'passer': original_passer, 'recipient': recipient_name, 'substituted_passer': True})
        else:
            pass_connections_list.append({'passer': passer_name, 'recipient': recipient_name, 'substituted_passer': False})
            
        # Do the same for recipients
        if recipient_name in sub_mapping:
            original_recipient = sub_mapping[recipient_name]
            # Update the last added connection
            pass_connections_list[-1]['recipient'] = original_recipient
            pass_connections_list[-1]['substituted_recipient'] = True
        else:
            pass_connections_list[-1]['substituted_recipient'] = False
    
    # Create a list of unique players for position calculation
    unique_players = set()
    for connection in pass_connections_list:
        unique_players.add(connection['passer'])
        unique_players.add(connection['recipient'])
    
    # Calculate average positions and include position information
    avg_positions_list = []
    for player_name in unique_players:
        # Find all passes by this player (either original or after substitution mapping)
        player_passes = passes_df[passes_df['player'].apply(
            lambda x: x.get('name', '') == player_name if isinstance(x, dict) else str(x) == player_name
        )]
        
        # Find all passes by the substituted player if this is an original player
        sub_player = None
        for replacement, original in sub_mapping.items():
            if original == player_name:
                sub_player = replacement
                break
                
        if sub_player:
            sub_passes = passes_df[passes_df['player'].apply(
                lambda x: x.get('name', '') == sub_player if isinstance(x, dict) else str(x) == sub_player
            )]
            # Combine passes from original and substituted player
            player_passes = pd.concat([player_passes, sub_passes])
        
        if not player_passes.empty:
            # Get position for this player from events dataframe
            player_events = events_df[events_df['player'].apply(
                lambda x: x.get('name', '') == player_name if isinstance(x, dict) else str(x) == player_name
            )]
            
            # Extract position name from the position field
            position = 'Unknown'
            if not player_events.empty and 'position' in player_events.columns:
                # Get the first available position for this player
                pos_entry = player_events['position'].dropna().iloc[0] if not player_events['position'].dropna().empty else None
                if pos_entry is not None:
                    position = pos_entry.get('name', 'Unknown') if isinstance(pos_entry, dict) else str(pos_entry)
            
            # Check if this player was substituted or is a substitute
            was_substituted = player_name in sub_mapping.values()
            is_substitute = player_name in sub_mapping.keys()
            
            avg_positions_list.append({
                'player_name': player_name,
                'position': position,
                'x': player_passes['x'].mean(),
                'y': player_passes['y'].mean(),
                'was_substituted': was_substituted,
                'is_substitute': is_substitute,
                'sub_player': sub_player
            })
    
    avg_positions = pd.DataFrame(avg_positions_list)

    if avg_positions.empty:
        return go.Figure().add_annotation(text="Could not calculate average player positions", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    pass_connections_df = pd.DataFrame(pass_connections_list)
    pass_connections = pass_connections_df.groupby(['passer', 'recipient']).size().reset_index(name='passes')
    
    # Calculate pass threshold dynamically as a percentage of the maximum pass count
    min_pass_threshold = max(2, int(pass_connections['passes'].max() * 0.15)) if not pass_connections.empty else 3
    print(f"Minimum pass threshold set to: {min_pass_threshold} for {team_name}")
    # Filter to include only connections with sufficient passes
    pass_connections = pass_connections[pass_connections['passes'] >= min_pass_threshold]
    
    # Calculate normalized line widths based on pass frequency
    if not pass_connections.empty:
        max_line_width = 18  # Thicker lines for better visibility (increased from example)
        min_line_width = 2.5  # Increased minimum for better visibility
        pass_connections['width'] = min_line_width + ((pass_connections['passes'] - pass_connections['passes'].min()) / 
                               (pass_connections['passes'].max() - pass_connections['passes'].min() + 0.001)) * (max_line_width - min_line_width)
        
        # Calculate transparency based on pass count
        min_transparency = 0.3  # Lower minimum transparency for better visibility (from example)
        pass_connections['transparency'] = min_transparency + ((pass_connections['passes'] - pass_connections['passes'].min()) / 
                                      (pass_connections['passes'].max() - pass_connections['passes'].min() + 0.001)) * (1 - min_transparency)

    fig = go.Figure()
    
    # First calculate all data and prepare everything before rendering
    # Add detailed pitch background
    _draw_pitch_plotly(fig)
    
    # Calculate total involvement (passes made + received) for better node sizing
    if not avg_positions.empty:
        # Count passes made
        made_passes = pass_connections_df.groupby('passer').size().reset_index(name='pass_count')
        made_passes = made_passes.rename(columns={'passer': 'player_name'})
        
        # Count passes received
        received_passes = pass_connections_df.groupby('recipient').size().reset_index(name='received_count')
        received_passes = received_passes.rename(columns={'recipient': 'player_name'})
        
        # Merge pass counts with avg_positions
        avg_positions = avg_positions.merge(made_passes, on='player_name', how='left')
        avg_positions = avg_positions.merge(received_passes, on='player_name', how='left')
        avg_positions['pass_count'] = avg_positions['pass_count'].fillna(0)
        avg_positions['received_count'] = avg_positions['received_count'].fillna(0)
        
        # Calculate total involvement
        avg_positions['total_involvement'] = avg_positions['pass_count'] + avg_positions['received_count']
        
        # Calculate node size based on total involvement - with larger sizes for better visibility
        min_marker_size = 30
        max_marker_size = 45
        if len(avg_positions) > 1:  # Only normalize if we have multiple players
            min_involvement = avg_positions['total_involvement'].min()
            max_involvement = avg_positions['total_involvement'].max()
            range_involvement = max_involvement - min_involvement
            
            if range_involvement > 0:  # Avoid division by zero
                avg_positions['marker_size'] = min_marker_size + ((avg_positions['total_involvement'] - min_involvement) / 
                                            range_involvement) * (max_marker_size - min_marker_size)
            else:
                avg_positions['marker_size'] = min_marker_size
        else:
            avg_positions['marker_size'] = max_marker_size
    
    # First add pass connections with variable width and transparency
    # (adding connections before player nodes ensures they appear underneath)
    for _, connection in pass_connections.iterrows():
        passer_pos = avg_positions[avg_positions['player_name'] == connection['passer']]
        receiver_pos = avg_positions[avg_positions['player_name'] == connection['recipient']]
        
        if not passer_pos.empty and not receiver_pos.empty:
            fig.add_trace(go.Scatter(
                x=[passer_pos.iloc[0]['x'], receiver_pos.iloc[0]['x']],
                y=[passer_pos.iloc[0]['y'], receiver_pos.iloc[0]['y']],
                mode='lines',
                line=dict(width=connection['width'], 
                         color=f'rgba(255,255,255,{connection["transparency"]})',  # White for maximum visibility
                         shape='linear'),  # Linear lines for more clarity
                showlegend=False,
                hoverinfo='text',
                text=f"{connection['passer']} to {connection['recipient']}: {connection['passes']} passes",
                name=f"Passes: {connection['passes']}"
            ))
    
    # Then add player position nodes with dynamic sizing and better styling
    positions_dict_acronym={
        "Goalkeeper": "GK",
        "Center Back": "CB",
        "Left Back": "LB",
        "Right Back": "RB",
        "Left Center Back": "LCB",
        "Right Center Back": "RCB",
        "Left Wing Back": "LWB",
        "Right Wing Back": "RWB",
        "Center Midfield": "CM",
        "Center Defensive Midfield": "CDM",
        "Center Attacking Midfield": "CAM",
        "Left Midfield": "LM",
        "Right Midfield": "RM",
        "Left Center Midfield": "LCM",
        "Right Center Midfield": "RCM",
        "Left Defensive Midfield": "LDM",
        "Right Defensive Midfield": "RDM",
        "Left Attacking Midfield": "LAM",
        "Right Attacking Midfield": "RAM",
        "Center Forward": "CF",
        "Left Wing": "LW",
        "Right Wing": "RW",
        "Left Center Forward": "LCF",
        "Right Center Forward": "RCF",
        "Substitute": "SUB"
        
    }
    if not avg_positions.empty:
        # Create player text (only position acronym)
        player_texts = []
        for _, player in avg_positions.iterrows():
            # Get position information
            pos = player['position']
            pos_abbr = positions_dict_acronym.get(pos, 'Unknown')  # Use acronym or 'Unknown' if not found
                
            player_texts.append(pos_abbr)
            
        # Create colored circles based on positions - brighter colors for better visibility on the pitch
        position_colors = {
            # Goalkeepers
            'Goalkeeper': '#FFC312',  # Yellow/Gold
            
            # Defenders
            'Center Back': '#00d2d3',  # Bright Teal
            'Left Back': '#54a0ff',    # Bright Blue
            'Right Back': '#54a0ff',   # Bright Blue
            'Left Center Back': '#00d2d3',  # Bright Teal
            'Right Center Back': '#00d2d3', # Bright Teal
            'Left Wing Back': '#54a0ff',    # Bright Blue
            'Right Wing Back': '#54a0ff',   # Bright Blue
            
            # Midfielders
            'Center Midfield': '#0be881',       # Bright Green
            'Center Defensive Midfield': '#20b2aa',  # Light Sea Green
            'Center Attacking Midfield': '#ff9f43',  # Bright Orange
            'Left Midfield': '#0be881',         # Bright Green
            'Right Midfield': '#0be881',        # Bright Green
            'Left Center Midfield': '#0be881',  # Bright Green
            'Right Center Midfield': '#0be881', # Bright Green
            'Left Defensive Midfield': '#20b2aa',  # Light Sea Green
            'Right Defensive Midfield': '#20b2aa', # Light Sea Green
            'Left Attacking Midfield': '#ff9f43',  # Bright Orange
            'Right Attacking Midfield': '#ff9f43', # Bright Orange
            
            # Forwards
            'Center Forward': '#ff6b6b',      # Bright Red
            'Left Wing': '#ff6b6b',          # Bright Red
            'Right Wing': '#ff6b6b',         # Bright Red
            'Left Center Forward': '#ff6b6b', # Bright Red
            'Right Center Forward': '#ff6b6b' # Bright Red
        }
        
        # Get color for each player based on position
        node_colors = [position_colors.get(pos, '#7f8c8d') for pos in avg_positions['position']]
        
        # Create different symbols for substituted players
        node_symbols = []
        for _, player in avg_positions.iterrows():
            if player['was_substituted']:
                node_symbols.append('octagon')  # Use diamond for substituted players
            else:
                node_symbols.append('circle')  # Use circle for regular players
        
        # Add player nodes with improved visibility
        fig.add_trace(go.Scatter(
            x=avg_positions['x'],
            y=avg_positions['y'],
            mode='markers+text',
            marker=dict(
                size=avg_positions['marker_size'],
                color=node_colors,
                line=dict(
                    width=2, 
                    color='black'  # Black border for better contrast
                ),
                opacity=1.0,  # Full opacity for maximum visibility
                symbol=node_symbols
            ),
            text=player_texts,
            textfont=dict(color='white', size=14, family='Arial, sans-serif', weight='bold'),  # Larger text for better visibility
            textposition='middle center',
            name='Players',
            hoverinfo='text',
            hovertext=[f"<b>{p['player_name']}</b><br>Position: {p['position']}<br>Passes: {int(p['pass_count'])}<br>Received: {int(p['received_count'])}<br>Total Involvement: {int(p['total_involvement'])}{('<br><b>Substituted by: </b>' + p['sub_player']) if p['was_substituted'] else ''}" for _, p in avg_positions.iterrows()]
        ))
            
    # Enhance the layout for a more professional look
    fig.update_layout(
        title={
            'text': f"<b>{team_name} Pass Network</b>",  # Changed format to match example
            'y': 0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#ffffff'}
        },
        height=600,
        showlegend=False,
        paper_bgcolor='#22312b',  # Dark green background like a pitch
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent since we draw our own pitch
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Arial, sans-serif', color='white'),
        # Add explanatory annotation
        annotations=[
            dict(
                text="Node size = player involvement | Line width = pass frequency",
                xref="paper", yref="paper",
                x=0.5, y=0.02,
                showarrow=False,
                font=dict(size=12, color='rgba(255,255,255,0.7)'),
                align="center"
            )
        ]
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
    """Create xG timeline for a match, including goal markers and own goals."""
    # Get both shots and own goals
    shots_df = events_df[events_df['type'] == 'Shot'].copy()
    
    # Get own goals (separately by type)
    own_goals_for = events_df[events_df['type'] == 'Own Goal For'].copy() if 'Own Goal For' in events_df['type'].values else pd.DataFrame()
    own_goals_against = events_df[events_df['type'] == 'Own Goal Against'].copy() if 'Own Goal Against' in events_df['type'].values else pd.DataFrame()
    
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
    
    # Collect all goals from all teams first for better handling of minute overlaps
    all_goals = []
    
    # Also track own goals separately so we can add them to the timeline
    own_goals_data = []

    for i, team in enumerate(teams):
        team_shots = shots_df[shots_df['team'].apply(
            lambda x: x.get('name', '') == team if isinstance(x, dict) else str(x) == team
        )]
        
        cumulative_xg = team_shots['shot_statsbomb_xg'].cumsum()
        
        # Always start from minute 0 with xG 0 for better visualization
        # and to ensure the graph shows the entire match timeline
        plot_minutes = list(team_shots['minute'])
        plot_xg = list(cumulative_xg)
        
        # Add starting point at minute 0 if not already present
        if not (plot_minutes and plot_minutes[0] == 0):
            plot_minutes = [0] + plot_minutes
            plot_xg = [0] + plot_xg
        
        # Add ending point at minute 90 if the last minute is less than 90
        if plot_minutes and plot_minutes[-1] < 90:
            plot_minutes.append(90)
            plot_xg.append(plot_xg[-1] if plot_xg else 0)  # Use last xG value
        
        fig.add_trace(go.Scatter(
            x=plot_minutes,
            y=plot_xg,
            mode='lines+markers',
            name=f"{team} xG",
            line=dict(width=3, color=team_colors[i % len(team_colors)]), # Assign distinct color
            marker=dict(size=8, symbol='circle'),
            hovertemplate='<b>%{fullData.name}</b><br>Minute: %{x}<br>Cumulative xG: %{y:.2f}<extra></extra>'
        ))

        # Find goals for this team
        goals = team_shots[
            (team_shots['shot_outcome'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x))) == 'Goal'
        ]
        
        # Collect goals for later processing
        for _, goal in goals.iterrows():
            # Safely get player name
            if isinstance(goal.get('player'), dict):
                player_name = goal['player'].get('name', 'Unknown')
            else:
                player_name = str(goal.get('player', 'Unknown'))
                
            # Get only last name for brevity
            if ' ' in player_name:
                player_name = player_name.split(' ')[-1]
                
            # Make sure we include all goals, even at minute 0
            all_goals.append({
                'minute': float(goal['minute']),  # Convert to float to handle any potential string values
                'player': player_name,
                'team': team,
                'team_index': i,  # Store team index for color reference
                'color': team_colors[i % len(team_colors)],
                'type': 'Goal'
            })
    
    # Process own goals and add them to the all_goals list
    # Only process Own Goal For events - to avoid double counting
    processed_event_ids = set()  # Track which events we've already processed
    
    for _, og in own_goals_for.iterrows():
        # Skip if we've already processed this event or its related event
        if og['id'] in processed_event_ids:
            continue
            
        # Add this event to processed list
        processed_event_ids.add(og['id'])
        
        # Find the team that benefited
        beneficiary_team = og['team'] if isinstance(og['team'], str) else og['team'].get('name', 'Unknown') if isinstance(og['team'], dict) else 'Unknown'
        
        # Try to find the other team involved
        related_events = og.get('related_events', [])
        scorer_team = None
        scorer_name = 'Unknown'
        
        # Look for related Own Goal Against event to get the scorer
        if related_events and not own_goals_against.empty:
            for _, related_og in own_goals_against.iterrows():
                if related_og['id'] in related_events:
                    # Add the related event to processed list to avoid double counting
                    processed_event_ids.add(related_og['id'])
                    
                    scorer_team = related_og['team'] if isinstance(related_og['team'], str) else related_og['team'].get('name', 'Unknown') if isinstance(related_og['team'], dict) else 'Unknown'
                    scorer_name = related_og['player'] if isinstance(related_og['player'], str) else related_og['player'].get('name', 'Unknown') if isinstance(related_og['player'], dict) else 'Unknown'
                    
                    # Get last name only
                    if ' ' in scorer_name:
                        scorer_name = scorer_name.split(' ')[-1]
                    break
        
        # Find the team index and color for the beneficiary team
        team_index = -1
        for i, team in enumerate(teams):
            if team == beneficiary_team:
                team_index = i
                break
        
        # Use a neutral gray if team not found
        team_color = team_colors[team_index % len(team_colors)] if team_index >= 0 else 'gray'
        
        # Add the own goal to the list
        all_goals.append({
            'minute': float(og['minute']),
            'player': scorer_name,
            'team': scorer_team if scorer_team else 'Unknown',
            'beneficiary': beneficiary_team,
            'team_index': team_index,
            'color': team_color,
            'type': 'Own Goal'
        })
    
    # Process all goal markers from all teams together
    all_goals_sorted = sorted(all_goals, key=lambda x: (x['minute'], x['team_index']))
    
    # Skip if no goals found
    if not all_goals_sorted:
        pass  # Continue without adding goal markers
    else:
        # Group goals by exact same minute to handle identical timing
        minute_groups = {}
        for goal in all_goals_sorted:
            minute = goal['minute']
            if minute not in minute_groups:
                minute_groups[minute] = []
            minute_groups[minute].append(goal)
        
        # Process each minute, handling cases where multiple goals occur at the same time
        for minute, goals_at_minute in sorted(minute_groups.items()):
            # For minute 0 goals, slightly offset to make them visible
            x_position = max(0.5, minute) if minute == 0 else minute
            
            # Sort goals within the minute by team for consistent ordering
            goals_at_minute.sort(key=lambda x: x['team_index'])
            
            # Create one vertical line for this minute
            # Use a neutral color for the line when multiple teams score in the same minute
            line_color = goals_at_minute[0]['color'] if len(goals_at_minute) == 1 else 'gray'
            
            # Add the vertical line
            fig.add_vline(
                x=x_position,
                line_width=1.5,
                line_dash="dash",
                line_color=line_color
            )
            
            # For goals that are close together in time, we need to spread out the labels horizontally
            # to prevent overlapping
            
            # Calculate horizontal offset for goals in similar time periods
            minutes_with_goals = list(sorted(minute_groups.keys()))
            minute_idx = minutes_with_goals.index(minute)
            
            # Check if this minute is close to previous minutes with goals
            horizontal_shift = 0
            if minute_idx > 0 and minute - minutes_with_goals[minute_idx-1] < 8:
                # If close to previous minute with goals, shift right
                horizontal_shift = 15
            
            # Add annotations for each goal at this minute
            for i, goal in enumerate(goals_at_minute):
                team_initial = goal['team'][0].upper() if goal['team'] else '?'
                player_name = goal['player']
                
                # Format goal text based on goal type
                if goal.get('type') == 'Own Goal':
                    beneficiary_initial = goal.get('beneficiary', 'Unknown')[0].upper() if goal.get('beneficiary') else '?'
                    goal_text = f"OG: {player_name} ({team_initial}) → ({beneficiary_initial})"
                else:
                    goal_text = f"{player_name} ({team_initial})"
                
                # Calculate vertical position - stagger goals at same minute
                if len(goals_at_minute) == 1:
                    y_pos = 1.05  # Single goal at top
                else:
                    # Distribute multiple goals vertically
                    # For odd number of goals, center the middle one
                    if len(goals_at_minute) % 2 == 1 and i == len(goals_at_minute) // 2:
                        y_pos = 0.5  # Middle position
                    else:
                        # Alternate between top and bottom
                        if i % 2 == 0:
                            y_pos = 1.05 - (0.15 * (i // 2))  # Top positions
                        else:
                            y_pos = 0.05 + (0.15 * (i // 2))  # Bottom positions
                
                # For horizontal position, use slight offsets for alternating goals
                # This spreads them out horizontally
                ax_offset = horizontal_shift
                if len(goals_at_minute) > 1:
                    ax_offset += (i % 2) * 20  # Alternate between 0 and 20 pixels offset
                
                # Add the annotation
                fig.add_annotation(
                    x=x_position,
                    y=y_pos,
                    text=goal_text,
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=1.5,
                    arrowcolor=goal['color'],
                    font=dict(color=goal['color'], size=10),
                    align="center",
                    xref="x",
                    yref="paper",  # Use paper coordinates
                    ax=ax_offset,  # Horizontal offset from the point
                    ay=0  # No vertical offset in the arrow
                )
    
    # Update layout with more space for annotations
    fig.update_layout(
        title="<b>Expected Goals (xG) Timeline</b>",
        xaxis_title="Minute",
        yaxis_title="Cumulative Expected Goals (xG)",
        height=600,  # Further increased height for better annotation spacing
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)', bordercolor='white', borderwidth=1),
        plot_bgcolor='white',
        paper_bgcolor='#E0E0E0',
        margin=dict(t=120, b=80, l=50, r=80)  # Significantly increased margins for annotations
    )
    
    # Add extra padding for the goal annotations
    fig.update_yaxes(rangemode='tozero', automargin=True)
    fig.update_xaxes(automargin=True)
    
    return fig

def create_formation_viz(events_df, team_name, match_id=None):
    """Create formation visualization with player position heatmaps using mplsoccer"""
    # Filter the events to get only the team's data
    team_events = events_df[events_df['team'].apply(
        lambda x: x.get('name', '') == team_name if isinstance(x, dict) else str(x) == team_name
    )].copy()
    
    # Get formation information
    formation_data = team_events[team_events['tactics_formation'].notna()]
    
    if formation_data.empty:
        return go.Figure().add_annotation(text="No formation data available", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Get the latest formation info
    formation = formation_data['tactics_formation'].iloc[0]
    
    # Get starting XI event and lineup
    starting_xi_events = team_events[(team_events['type'] == 'Starting XI') | 
                                    (team_events['type_name'] == 'Starting XI')]
    
    if starting_xi_events.empty:
        return go.Figure().add_annotation(text="No starting XI data available", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Extract lineup data
    players_info = []
    
    # Process tactics lineup
    try:
        # Try to extract from tactics_lineup field
        for _, row in starting_xi_events.iterrows():
            if 'tactics_lineup' in row and isinstance(row['tactics_lineup'], list):
                for player in row['tactics_lineup']:
                    player_id = player.get('player', {}).get('id')
                    player_name = player.get('player', {}).get('name')
                    position_id = player.get('position', {}).get('id')
                    position_name = player.get('position', {}).get('name')
                    
                    if player_id and player_name:
                        # Extract player data
                        player_events = team_events[
                            (team_events['player'].apply(
                                lambda x: x.get('id', None) == player_id if isinstance(x, dict) else False
                            )) & 
                            (team_events['type'].isin(['Pass', 'Ball Receipt', 'Carry']))
                        ]
                        
                        if not player_events.empty:
                            # Calculate average position
                            avg_x = player_events['x'].mean()
                            avg_y = player_events['y'].mean()
                            
                            # Get x, y coordinates for heatmap
                            x_coords = player_events['x'].dropna().tolist()
                            y_coords = player_events['y'].dropna().tolist()
                            
                            # Use last name if full name is too long
                            display_name = player_name
                            if len(player_name) > 12 and ' ' in player_name:
                                display_name = player_name.split(' ')[-1]
                            
                            # Get position acronym
                            pos_abbr = positions_dict_acronym.get(position_name, position_name[:2] if position_name else 'UN')
                            
                            players_info.append({
                                'player_id': player_id,
                                'player_name': player_name,
                                'display_name': display_name,
                                'position_id': position_id,
                                'position_name': position_name,
                                'position_abbr': pos_abbr,
                                'avg_x': avg_x,
                                'avg_y': avg_y,
                                'x_coords': x_coords,
                                'y_coords': y_coords
                            })
    except Exception as e:
        print(f"Error processing tactics lineup: {e}")
    
    # If no players found through tactics_lineup, try to extract from the events directly
    if not players_info:
        print("No players found in tactics_lineup, extracting from events")
        player_ids = team_events['player'].apply(
            lambda x: x.get('id') if isinstance(x, dict) and 'id' in x else None
        ).dropna().unique()
        
        for player_id in player_ids:
            player_events = team_events[
                (team_events['player'].apply(
                    lambda x: x.get('id') == player_id if isinstance(x, dict) and 'id' in x else False
                )) & 
                (team_events['type'].isin(['Pass', 'Ball Receipt', 'Carry']))
            ]
            
            if not player_events.empty:
                player_row = player_events.iloc[0]
                player_name = player_row['player'].get('name', 'Unknown') if isinstance(player_row['player'], dict) else 'Unknown'
                
                # Try to get position from the player data
                position_name = 'Unknown'
                position_id = None
                if 'position' in player_row and isinstance(player_row['position'], dict):
                    position_name = player_row['position'].get('name', 'Unknown')
                    position_id = player_row['position'].get('id')
                
                # Calculate average position
                avg_x = player_events['x'].mean()
                avg_y = player_events['y'].mean()
                
                # Get x, y coordinates for heatmap
                x_coords = player_events['x'].dropna().tolist()
                y_coords = player_events['y'].dropna().tolist()
                
                # Use last name if full name is too long
                display_name = player_name
                if len(player_name) > 12 and ' ' in player_name:
                    display_name = player_name.split(' ')[-1]
                
                # Get position acronym
                pos_abbr = positions_dict_acronym.get(position_name, position_name[:2] if position_name else 'UN')
                
                players_info.append({
                    'player_id': player_id,
                    'player_name': player_name,
                    'display_name': display_name,
                    'position_id': position_id,
                    'position_name': position_name,
                    'position_abbr': pos_abbr,
                    'avg_x': avg_x,
                    'avg_y': avg_y,
                    'x_coords': x_coords,
                    'y_coords': y_coords
                })
    
    # Check if we have enough data to create the visualization
    if not players_info:
        return go.Figure().add_annotation(text="Insufficient player data for formation visualization", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Create a matplotlib figure with formation visualization
    # Create vertical pitch
    pitch = VerticalPitch(goal_type='box', pitch_color='#22312b', line_color='#c7d5cc')
    
    # Create the figure with grid layout
    fig, axs = pitch.grid(endnote_height=0, title_height=0.08, figheight=14, grid_width=0.9,
                        grid_height=0.9, axis=False)
    
    # Use Rubik Mono One font for title
    try:
        fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                            'rubikmonoone/RubikMonoOne-Regular.ttf')
    except:
        # Fallback to default font if Rubik can't be loaded
        fm_rubik = None
    
    # Set title
    title_props = fm_rubik.prop if fm_rubik else None
    title = axs['title'].text(0.5, 0.5, f'Formation: {formation}\n{team_name}', fontsize=18,
                            va='center', ha='center', color='#c7d5cc', fontproperties=title_props)
    
    # Create a positional grid for each player
    pitch_positions = {}
    position_grids = {}
    
    for player in players_info:
        if player['position_id'] and player['x_coords'] and player['y_coords']:
            # Use position_id as the grid key
            position_id = player['position_id']
            
            # If this position hasn't been handled yet, create a grid for it
            if position_id not in position_grids:
                # Calculate grid positions with proper offsets to avoid overlap
                # This is a simplified approach - ideally we would calculate proper offsets based on formation
                position_grids[position_id] = pitch.grid(ncols=1, nrows=1, grid_height=0.9, axis=False)['pitch']
                
                # Create KDE plot for this player
                pitch_positions[position_id] = pitch.kdeplot(
                    player['x_coords'], player['y_coords'],
                    ax=position_grids[position_id],
                    fill=True, levels=100, 
                    cut=4, cmap='Blues', thresh=0)
                
                # Add player name and position
                position_grids[position_id].text(
                    120/2, 10, player['display_name'], 
                    va='top', ha='center', fontsize=12, 
                    color='white', fontweight='bold')
                
                position_grids[position_id].text(
                    120/2, 20, player['position_abbr'], 
                    va='top', ha='center', fontsize=14, 
                    color='white', fontweight='bold', 
                    bbox=dict(facecolor='#1E88E5', alpha=0.7, boxstyle='round,pad=0.5'))
    
    # Save figure to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name, dpi=200, bbox_inches='tight', facecolor='#22312b')
    plt.close()
    
    # Read the saved image and convert to base64
    with open(temp_file.name, 'rb') as img_file:
        img_data = base64.b64encode(img_file.read()).decode('utf-8')
    
    # Clean up the temporary file
    os.unlink(temp_file.name)
    
    # Create a Plotly figure to display the image
    fig = go.Figure()
    
    # Add the image to the figure
    fig.add_layout_image(
        dict(
            source=f'data:image/png;base64,{img_data}',
            xref="paper", yref="paper",
            x=0, y=1,
            sizex=1, sizey=1,
            sizing="stretch",
            layer="below"
        )
    )
    
    # Update the layout to be transparent
    fig.update_layout(
        title=f"{team_name} Formation: {formation}",
        title_x=0.5,
        title_font=dict(size=16, color='white'),
        height=700,
        width=500,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    return fig

# Dictionary for position acronyms
positions_dict_acronym = {
    "Goalkeeper": "GK",
    "Center Back": "CB",
    "Left Back": "LB",
    "Right Back": "RB",
    "Left Center Back": "LCB",
    "Right Center Back": "RCB",
    "Left Wing Back": "LWB",
    "Right Wing Back": "RWB",
    "Center Midfield": "CM",
    "Center Defensive Midfield": "CDM",
    "Center Attacking Midfield": "CAM",
    "Left Midfield": "LM",
    "Right Midfield": "RM",
    "Left Center Midfield": "LCM",
    "Right Center Midfield": "RCM",
    "Left Defensive Midfield": "LDM",
    "Right Defensive Midfield": "RDM",
    "Left Attacking Midfield": "LAM",
    "Right Attacking Midfield": "RAM",
    "Center Forward": "CF",
    "Left Wing": "LW",
    "Right Wing": "RW",
    "Left Center Forward": "LCF",
    "Right Center Forward": "RCF",
    "Substitute": "SUB"
}

def save_plot_as_base64(fig):
    """Convert Plotly figure to base64 string"""
    buf = io.BytesIO()
    fig.write_image(buf, format='png', engine='kaleido', scale=2) # Use kaleido for better quality
    buf.seek(0)
    encoded = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{encoded}"