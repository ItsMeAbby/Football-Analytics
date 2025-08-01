import matplotlib
matplotlib.use('Agg') # <--- !! IMPORTANT: MUST be before pyplot import !!
# -*- coding: utf-8 -*-
# Import necessary packages
from mplsoccer import Pitch, VerticalPitch
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from matplotlib.colors import LinearSegmentedColormap
# import plotly.graph_objects as go # No longer needed for these functions
# import plotly.express as px # No longer needed
# from plotly.subplots import make_subplots # No longer needed
import numpy as np
# import seaborn as sns # Used for style/palette, can be replaced by matplotlib specifics
import io
import base64
# from highlight_text import ax_text # Using standard matplotlib text for now

# Set a matplotlib style similar to seaborn or a common football analytics style
plt.style.use('ggplot') # ggplot is a common alternative, or use a custom one

# Helper function to get entity names (player, team)
def get_entity_name(entity):
    if isinstance(entity, dict):
        return entity.get('name', 'Unknown')
    if pd.isna(entity):
        return 'Unknown'
    return str(entity)

def create_shot_map(events_df, team_name, player_name=None):
    """Create a shot map using Matplotlib and mplsoccer"""
    # Filter shots
    # First, ensure 'type' column exists and handle potential errors
    if 'type' not in events_df.columns:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "Column 'type' not found in DataFrame.", ha='center', va='center', fontsize=12)
        return matplotlib_plot_as_base64(fig)
        
    shots_df = events_df[events_df['type'] == 'Shot'].copy()

    if team_name:
        shots_df = shots_df[shots_df['team'].apply(get_entity_name) == team_name]
    
    if player_name:
        shots_df = shots_df[shots_df['player'].apply(get_entity_name) == player_name]

    # Check for necessary columns: x, y
    if 'x' not in shots_df.columns or 'y' not in shots_df.columns:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "Missing required columns (x, y) for shot map.", 
                  ha='center', va='center', fontsize=10)
        ax.set_title(f"Shot Map - {team_name or 'None'}" + (f" - {player_name}" if player_name else ""), fontsize=16)
        return matplotlib_plot_as_base64(fig)
        
    if shots_df.empty:
        fig, ax = plt.subplots(figsize=(12, 8)) # Create a figure to return
        pitch = VerticalPitch(pitch_type='statsbomb', half=True, pad_bottom=-10, line_zorder=2, line_color='grey')
        pitch.draw(ax=ax)
        ax.text(60, 40, "No shot data available", ha='center', va='center', fontsize=12, color='red',
                transform=ax.transData) # Use transData for pitch coordinates if pitch is drawn
        ax.set_title(f"Shot Map - {team_name or 'None'}" + (f" - {player_name}" if player_name else ""), fontsize=16)
        return matplotlib_plot_as_base64(fig)

    # Create a default xG value if not available
    if 'shot_statsbomb_xg' not in shots_df.columns:
        # Use a default value (0.05) if xG not available
        shots_df['shot_statsbomb_xg'] = 0.05
        print("Warning: shot_statsbomb_xg not found, using default value")
    
    # Create outcome field if not available
    if 'shot_outcome' not in shots_df.columns:
        shots_df['outcome_name'] = 'Off Target'
        print("Warning: shot_outcome not found, using default value")
    else:
        # Ensure shot_outcome is parsed correctly if it's a dict
        shots_df['outcome_name'] = shots_df['shot_outcome'].apply(lambda x: get_entity_name(x) if isinstance(x, dict) else str(x))

    # Setup the pitch
    pitch = VerticalPitch(pitch_type='statsbomb', half=True, pad_bottom=-10, line_zorder=2, line_color='grey')
    fig, ax = pitch.draw(figsize=(12, 8))
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    # Find goals based on outcome
    goals = shots_df[shots_df['outcome_name'] == 'Goal']
    other_shots = shots_df[shots_df['outcome_name'] != 'Goal']

    # Plot non-goal shots with hatch pattern
    if not other_shots.empty:
        pitch.scatter(other_shots.x, other_shots.y,
                      s=(other_shots.shot_statsbomb_xg * 1900) + 100,  # Scale size by xG
                      edgecolors='#b94b75',  # Border color
                      c='None',  # No fill color
                      hatch='///',  # Diagonal hatch pattern
                      marker='o',
                      linewidths=0.6,
                      alpha=0.8,
                      ax=ax,
                      label='Shot')

    # Plot goals with football marker
    if not goals.empty:
        pitch.scatter(goals.x, goals.y,
                      s=(goals.shot_statsbomb_xg * 1900) + 100,  # Scale size by xG
                      edgecolors='#b94b75',  # Border color  
                      linewidths=0.6,
                      c='white',  # White fill
                      marker='football',  # Football marker
                      ax=ax,
                      label='Goal')

    ax.legend(facecolor='#EFE9E6', handlelength=3, edgecolor='None', fontsize=12, loc='lower left', framealpha=0.7)
    title_text = f"Shot Map - {team_name or 'None'}" + (f" - {player_name}" if player_name else "")
    ax.set_title(title_text, fontsize=18, color='black', pad=15)
    
    return matplotlib_plot_as_base64(fig)

def create_pass_network(events_df, team_name, match_id=None):
    """Create a pass network visualization using Matplotlib and mplsoccer"""
    if 'type' not in events_df.columns:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "Column 'type' not found in DataFrame.", ha='center', va='center', fontsize=12)
        return matplotlib_plot_as_base64(fig)

    passes_df = events_df[
        (events_df['type'] == 'Pass') &
        (events_df['team'].apply(get_entity_name) == team_name) &
        (events_df['pass_outcome'].isna())  # Only successful passes
    ].copy()

    required_pass_cols = ['x', 'y', 'pass_end_x', 'pass_end_y', 'player', 'pass_recipient']
    if not all(col in passes_df.columns for col in required_pass_cols):
        fig, ax = plt.subplots(figsize=(11, 7))
        ax.text(0.5, 0.5, "Missing required columns for pass network.", 
                  ha='center', va='center', fontsize=10)
        ax.set_title(f"Pass Network - {team_name}", fontsize=16)
        return matplotlib_plot_as_base64(fig)

    if passes_df.empty:
        fig, ax = plt.subplots(figsize=(11, 7))
        pitch = Pitch(pitch_type='statsbomb', line_zorder=2, line_color='grey')
        pitch.draw(ax=ax)
        ax.text(60, 40, "No pass data available", ha='center', va='center', fontsize=12, color='red', transform=ax.transData)
        ax.set_title(f"Pass Network - {team_name}", fontsize=16)
        return matplotlib_plot_as_base64(fig)

    # Get player names correctly
    passes_df['player_name'] = passes_df['player'].apply(get_entity_name)
    passes_df['recipient_name'] = passes_df['pass_recipient'].apply(get_entity_name)
    
    # Calculate average positions
    avg_positions = passes_df.groupby('player_name').agg({
        'x': 'mean',
        'y': 'mean',
        'id': 'count' # Count passes made by player
    }).reset_index().rename(columns={'id': 'pass_count'})
    
    # Calculate pass connections (use names now)
    pass_connections = passes_df.groupby(['player_name', 'recipient_name']).size().reset_index(name='passes_between')
    # Filter for minimum passes (e.g., >=3 from original code, or adjust)
    min_passes_threshold = max(1, int(pass_connections['passes_between'].quantile(0.6))) # Dynamic threshold
    pass_connections = pass_connections[pass_connections['passes_between'] >= min_passes_threshold]

    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, line_color='grey', pitch_color='#22312b')
    fig, ax = pitch.draw(figsize=(13.5, 9))
    fig.set_facecolor('#22312b')

    # Plot pass connections
    for _, row in pass_connections.iterrows():
        passer = avg_positions[avg_positions['player_name'] == row['player_name']]
        receiver = avg_positions[avg_positions['player_name'] == row['recipient_name']]
        
        if not passer.empty and not receiver.empty:
            pitch.lines(passer.x.iloc[0], passer.y.iloc[0], 
                        receiver.x.iloc[0], receiver.y.iloc[0],
                        lw=row['passes_between'] / 2, color='white', alpha=0.6, ax=ax, zorder=1)

    # Plot player positions
    # Scale node size by pass_count (number of passes made)
    max_passes = avg_positions['pass_count'].max()
    min_node_size, max_node_size = 200, 1200
    
    node_sizes = min_node_size + (avg_positions['pass_count'] / max_passes) * (max_node_size - min_node_size)
    # Handle cases where max_passes could be 0 or avg_positions is small
    if max_passes == 0 or len(avg_positions) == 1:
        node_sizes = [min_node_size] * len(avg_positions)

    pitch.scatter(avg_positions.x, avg_positions.y, s=node_sizes, 
                  color='red', edgecolors='black', linewidth=1, alpha=0.9, ax=ax, zorder=2)
    for _, row in avg_positions.iterrows():
        pitch.text(row.x, row.y, row.player_name.split(' ')[-1][:5], # Last name, up to 5 chars
                   fontsize=9, color='white', va='center', ha='center', ax=ax, zorder=3,
                   path_effects=[path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()])

    ax.set_title(f"Pass Network - {team_name}", fontsize=18, color='white', pad=15)
    return matplotlib_plot_as_base64(fig)

def create_heatmap(events_df, player_name, event_types=None):
    """Create a player heatmap using Matplotlib and mplsoccer"""
    if event_types is None:
        event_types = ['Pass', 'Ball Receipt*', 'Carry', 'Clearance', 'Foul Won', 'Block',
                       'Ball Recovery', 'Duel', 'Dribble', 'Interception', 'Miscontrol', 'Shot']
    
    if 'type' not in events_df.columns:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "Column 'type' not found in DataFrame.", ha='center', va='center', fontsize=12)
        return matplotlib_plot_as_base64(fig)

    # Filter for player events
    player_events = events_df[events_df['player'].apply(get_entity_name) == player_name].copy()
    
    # Further filter by event types if they exist in the data
    available_types = set(events_df['type'].unique())
    valid_types = [t for t in event_types if t in available_types]
    
    if valid_types:
        player_events = player_events[player_events['type'].isin(valid_types)]

    # Check for the required x, y columns
    if 'x' not in player_events.columns or 'y' not in player_events.columns:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "Missing required columns (x, y) for heatmap.", 
                  ha='center', va='center', fontsize=10)
        ax.set_title(f"Touch Heatmap - {player_name}", fontsize=16)
        return matplotlib_plot_as_base64(fig)

    # Setup the pitch
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, line_color='black', pitch_color='white')
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('white')

    # Check if we have valid event data
    if player_events.empty or player_events['x'].dropna().empty or player_events['y'].dropna().empty:
        ax.text(40, 60, "No event data for heatmap", ha='center', va='center', fontsize=12, color='red', transform=ax.transData)
        ax.set_title(f"Touch Heatmap - {player_name}", fontsize=16, color='black', pad=10)
        return matplotlib_plot_as_base64(fig)
    
    # Create heatmap using bin_statistic
    try:
        # Use smaller bins (more detailed) and only valid x,y data
        bin_statistic = pitch.bin_statistic(
            player_events.x.dropna(), 
            player_events.y.dropna(), 
            statistic='count', 
            bins=(6, 5), 
            normalize=True
        )
        
        # Simple red colormap
        cmap = LinearSegmentedColormap.from_list("", ["white", "lightcoral", "red"])

        # Draw the heatmap
        pitch.heatmap(bin_statistic, ax=ax, cmap=cmap, edgecolor='grey')
        
        # Add percentage labels
        labels = pitch.label_heatmap(
            bin_statistic, 
            color='black', 
            fontsize=10,
            ax=ax, 
            str_format='{:.0%}', 
            ha='center', 
            va='center',
            path_effects=[path_effects.Stroke(linewidth=1, foreground='white')]
        )
    except Exception as e:
        # If something goes wrong with the heatmap, provide fallback visualization
        print(f"Error creating heatmap: {e}")
        ax.text(40, 60, f"Error creating heatmap: {str(e)}", 
                ha='center', va='center', fontsize=10, color='red',
                transform=ax.transData)

    # Set title
    ax.set_title(f"Touch Heatmap - {player_name}", fontsize=18, color='black', pad=15)
    return matplotlib_plot_as_base64(fig)

def create_progressive_passes_viz(events_df, team_name):
    """Create visualization for progressive passes using Matplotlib"""
    # Check for required type column
    if 'type' not in events_df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Column 'type' not found in DataFrame.", ha='center', va='center', fontsize=12)
        return matplotlib_plot_as_base64(fig)
        
    # Check if we have pass data
    if len(events_df[events_df['type'] == 'Pass']) == 0:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No pass data available.", ha='center', va='center', fontsize=12)
        return matplotlib_plot_as_base64(fig)
    
    # Check for required coordinates
    if 'x' not in events_df.columns or 'pass_end_x' not in events_df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Missing required columns (x, pass_end_x) for progressive passes.", 
                ha='center', va='center', fontsize=10)
        ax.set_title(f"Progressive Passes - {team_name}", fontsize=16)
        return matplotlib_plot_as_base64(fig)
    
    # Get passes for the team
    team_passes = events_df[
        (events_df['type'] == 'Pass') &
        (events_df['team'].apply(get_entity_name) == team_name)
    ].copy()
    
    # If we have outcome info, filter for successful passes
    if 'pass_outcome' in team_passes.columns:
        team_passes = team_passes[team_passes['pass_outcome'].isna()]
    
    # Filter for only rows with valid x and pass_end_x (not NaN)
    team_passes = team_passes.dropna(subset=['x', 'pass_end_x'])
    
    if team_passes.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"No pass data available for team: {team_name}", 
                ha='center', va='center', fontsize=12, color='red')
        ax.set_title(f"Progressive Passes - {team_name}", fontsize=16)
        return matplotlib_plot_as_base64(fig)
        
    # Define progressive passes (simplified for robustness)
    # Consider a pass progressive if it moves forward at least 10 meters
    team_passes['progressive'] = (team_passes['pass_end_x'] - team_passes['x']) > 10
    
    prog_passes = team_passes[team_passes['progressive'] == True].copy()
    
    if prog_passes.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No progressive pass data available", 
                ha='center', va='center', fontsize=12, color='red')
        ax.set_title(f"Progressive Passes - {team_name}", fontsize=16)
        return matplotlib_plot_as_base64(fig)
    
    # Get player names and count progressive passes
    prog_passes['player_name'] = prog_passes['player'].apply(get_entity_name)
    player_counts = prog_passes.groupby('player_name').size().reset_index(name='progressive_passes')
    player_counts = player_counts.sort_values('progressive_passes', ascending=True)
    
    # Create the horizontal bar chart
    fig, ax = plt.subplots(figsize=(10, max(6, len(player_counts) * 0.5))) # Adjust height based on # of players
    
    bars = ax.barh(
        player_counts['player_name'], 
        player_counts['progressive_passes'], 
        color='skyblue', 
        edgecolor='black'
    )
    
    # Add labels to the bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f"{width:.0f}", 
                ha='left', va='center', fontweight='bold')
    
    # Customize the chart
    ax.set_xlabel("Number of Progressive Passes", fontsize=12)
    ax.set_ylabel("Player", fontsize=12)
    ax.set_title(f"Progressive Passes - {team_name}", fontsize=16, pad=15)
    
    # Set x-axis to start at 0
    ax.set_xlim(0, max(player_counts['progressive_passes']) * 1.1)
    
    # Add grid lines for better readability
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout() # Adjust layout to prevent labels cutting off
    
    return matplotlib_plot_as_base64(fig)

def create_xg_timeline(events_df, match_info=None, team_colors=None):
    """Create xG timeline for a match using Matplotlib"""
    if 'type' not in events_df.columns:
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.text(0.5, 0.5, "Column 'type' not found in DataFrame.", ha='center', va='center', fontsize=12)
        return matplotlib_plot_as_base64(fig)

    shots_df = events_df[events_df['type'] == 'Shot'].copy()

    required_xg_cols = ['minute', 'team', 'shot_statsbomb_xg']
    if not all(col in shots_df.columns for col in required_xg_cols):
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.text(0.5, 0.5, "Missing required columns for xG timeline.", 
                  ha='center', va='center', fontsize=10)
        ax.set_title("Expected Goals (xG) Timeline", fontsize=16)
        return matplotlib_plot_as_base64(fig)
        
    if shots_df.empty or shots_df['shot_statsbomb_xg'].isnull().all():
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.text(0.5, 0.5, "No shot data with xG available", ha='center', va='center', fontsize=12, color='red')
        ax.set_title("Expected Goals (xG) Timeline", fontsize=16)
        return matplotlib_plot_as_base64(fig)

    shots_df['team_name'] = shots_df['team'].apply(get_entity_name)
    shots_df = shots_df.sort_values('minute')
    
    teams = shots_df['team_name'].unique()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Use provided team colors or defaults
    if team_colors and len(team_colors) >= len(teams):
        colors = team_colors[:len(teams)]
    else:
        default_colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
        colors = default_colors[:len(teams)] if len(teams) <= len(default_colors) else plt.cm.get_cmap('Set1', len(teams))

    for i, team in enumerate(teams):
        team_shots = shots_df[shots_df['team_name'] == team].copy()
        if team_shots.empty:
            continue
        team_shots['cumulative_xg'] = team_shots['shot_statsbomb_xg'].cumsum()
        
        # Add a point at minute 0 with xG 0 for both teams to start lines from origin
        # Also ensure line extends to full time (e.g., 95 mins) for better viz
        plot_minutes = pd.concat([pd.Series([0]), team_shots['minute'], pd.Series([team_shots['minute'].max() if not team_shots['minute'].empty else 95])])
        plot_xg = pd.concat([pd.Series([0]), team_shots['cumulative_xg'], pd.Series([team_shots['cumulative_xg'].iloc[-1] if not team_shots['cumulative_xg'].empty else 0]) ])
        
        # Ensure plot_xg and plot_minutes are correctly aligned after sorting by minute and forward filling
        timeline_data = pd.DataFrame({'minute': plot_minutes, 'cumulative_xg': plot_xg}).sort_values('minute').drop_duplicates('minute',keep='last')
        timeline_data['cumulative_xg'] = timeline_data['cumulative_xg'].ffill()

        color = colors[i] if isinstance(colors, list) else colors(i)
        ax.plot(timeline_data['minute'], timeline_data['cumulative_xg'], 
                label=f"{team} xG ({timeline_data['cumulative_xg'].iloc[-1]:.2f})", 
                linewidth=3, marker='o', markersize=6, 
                color=color, alpha=0.8)
        
        # Add markers at shot events
        for shot_minute in team_shots['minute']:
            shot_idx = timeline_data[timeline_data['minute'] <= shot_minute].index[-1] if len(timeline_data[timeline_data['minute'] <= shot_minute]) > 0 else 0
            if shot_idx < len(timeline_data):
                ax.scatter(timeline_data.iloc[shot_idx]['minute'], timeline_data.iloc[shot_idx]['cumulative_xg'], 
                          s=80, color=color, edgecolor='white', linewidth=2, zorder=3, alpha=0.9)

    ax.set_xlabel("Minute", fontsize=12)
    ax.set_ylabel("Cumulative xG", fontsize=12)
    ax.set_title("Expected Goals (xG) Timeline", fontsize=16, pad=15)
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.7)
    # Set x-axis limits, e.g., 0 to 95 or max minute + buffer
    max_minute = shots_df['minute'].max()
    ax.set_xlim(0, max_minute + 5 if not pd.isna(max_minute) else 95)
    ax.set_ylim(bottom=0)
    plt.tight_layout()

    return matplotlib_plot_as_base64(fig)

def matplotlib_plot_as_base64(fig):
    """Convert matplotlib figure to base64 string"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor=fig.get_facecolor()) # Preserve facecolor
    buf.seek(0)
    encoded = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig) # Close the figure to free memory
    return f"data:image/png;base64,{encoded}"