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
        return save_plot_as_base64(fig)
        
    shots_df = events_df[events_df['type'] == 'Shot'].copy()

    if team_name:
        shots_df = shots_df[shots_df['team'].apply(get_entity_name) == team_name]
    
    if player_name:
        shots_df = shots_df[shots_df['player'].apply(get_entity_name) == player_name]

    # Check for necessary columns x, y, shot_statsbomb_xg, shot_outcome
    required_cols = ['x', 'y', 'shot_statsbomb_xg', 'shot_outcome']
    if not all(col in shots_df.columns for col in required_cols):
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "Missing required columns (x, y, shot_statsbomb_xg, or shot_outcome).", 
                  ha='center', va='center', fontsize=10)
        ax.set_title(f"Shot Map - {team_name}" + (f" - {player_name}" if player_name else ""), fontsize=16)
        return save_plot_as_base64(fig)
        
    if shots_df.empty:
        fig, ax = plt.subplots(figsize=(12, 8)) # Create a figure to return
        pitch = VerticalPitch(pitch_type='statsbomb', half=True, pad_bottom=-10, line_zorder=2, line_color='grey')
        pitch.draw(ax=ax)
        ax.text(60, 40, "No shot data available", ha='center', va='center', fontsize=12, color='red',
                transform=ax.transData) # Use transData for pitch coordinates if pitch is drawn
        ax.set_title(f"Shot Map - {team_name}" + (f" - {player_name}" if player_name else ""), fontsize=16)
        return save_plot_as_base64(fig)

    pitch = VerticalPitch(pitch_type='statsbomb', half=True, pad_bottom=-10, line_zorder=2, line_color='grey')
    fig, ax = pitch.draw(figsize=(12, 8))
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    # Define colors for outcomes (similar to example)
    # Ensure shot_outcome is parsed correctly if it's a dict
    shots_df['outcome_name'] = shots_df['shot_outcome'].apply(lambda x: get_entity_name(x) if isinstance(x, dict) else str(x))

    goals = shots_df[shots_df['outcome_name'] == 'Goal']
    other_shots = shots_df[shots_df['outcome_name'] != 'Goal']

    # Plot non-goals
    pitch.scatter(other_shots.x, other_shots.y,
                  s=other_shots.shot_statsbomb_xg * 700 + 100,  # Scale size by xG, add base size
                  c='red',
                  edgecolors='black',
                  marker='o',
                  alpha=0.6,
                  ax=ax,
                  label='Shot')

    # Plot goals
    pitch.scatter(goals.x, goals.y,
                  s=goals.shot_statsbomb_xg * 700 + 100,  # Scale size by xG
                  c='blue', # Or use 'football' marker from example
                  edgecolors='black',
                  marker='*', # Using star for goals
                  linewidth=1.5,
                  alpha=0.8,
                  ax=ax,
                  label='Goal',
                  zorder=3) # Ensure goals are on top

    ax.legend(facecolor='#EFE9E6', handlelength=3, edgecolor='None', fontsize=12, loc='lower left', framealpha=0.7)
    title_text = f"Shot Map - {team_name}" + (f" - {player_name}" if player_name else "")
    ax.set_title(title_text, fontsize=18, color='black', pad=15)
    
    return save_plot_as_base64(fig)

def create_pass_network(events_df, team_name, match_id=None):
    """Create a pass network visualization using Matplotlib and mplsoccer"""
    if 'type' not in events_df.columns:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "Column 'type' not found in DataFrame.", ha='center', va='center', fontsize=12)
        return save_plot_as_base64(fig)

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
        return save_plot_as_base64(fig)

    if passes_df.empty:
        fig, ax = plt.subplots(figsize=(11, 7))
        pitch = Pitch(pitch_type='statsbomb', line_zorder=2, line_color='grey')
        pitch.draw(ax=ax)
        ax.text(60, 40, "No pass data available", ha='center', va='center', fontsize=12, color='red', transform=ax.transData)
        ax.set_title(f"Pass Network - {team_name}", fontsize=16)
        return save_plot_as_base64(fig)

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
    return save_plot_as_base64(fig)

def create_heatmap(events_df, player_name, event_types=None):
    """Create a player heatmap using Matplotlib and mplsoccer"""
    if event_types is None:
        event_types = ['Pass', 'Ball Receipt*', 'Carry', 'Clearance', 'Foul Won', 'Block',
                       'Ball Recovery', 'Duel', 'Dribble', 'Interception', 'Miscontrol', 'Shot']
    
    if 'type' not in events_df.columns:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "Column 'type' not found in DataFrame.", ha='center', va='center', fontsize=12)
        return save_plot_as_base64(fig)

    player_events = events_df[
        (events_df['player'].apply(get_entity_name) == player_name) &
        (events_df['type'].isin(event_types))
    ].copy()

    required_event_cols = ['x', 'y']
    if not all(col in player_events.columns for col in required_event_cols):
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "Missing required columns (x, y) for heatmap.", 
                  ha='center', va='center', fontsize=10)
        ax.set_title(f"Touch Heatmap - {player_name}", fontsize=16)
        return save_plot_as_base64(fig)

    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, line_color='black', pitch_color='white')
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('white')

    if player_events.empty or player_events[['x', 'y']].isnull().all().all():
        ax.text(40, 60, "No event data for heatmap", ha='center', va='center', fontsize=12, color='red', transform=ax.transData)
        ax.set_title(f"Touch Heatmap - {player_name}", fontsize=16, color='black', pad=10)
        return save_plot_as_base64(fig)
    
    # Create heatmap
    # Using kdeplot for smooth heatmap, or bin_statistic for binned heatmap
    # For binned heatmap as in example:
    bin_statistic = pitch.bin_statistic(player_events.x.dropna(), player_events.y.dropna(), statistic='count', bins=(6, 5), normalize=True)
    
    # Custom colormap like example
    # colour1="white", colour2="#c3c3c3", colour3="#e21017" # From example
    # cmaplist = [colour1, colour2, colour3]
    # cmap = LinearSegmentedColormap.from_list("", cmaplist)
    cmap = LinearSegmentedColormap.from_list("", ["white", "lightcoral", "red"]) # Simpler red cmap

    pitch.heatmap(bin_statistic, ax=ax, cmap=cmap, edgecolor='grey')
    labels = pitch.label_heatmap(bin_statistic, color='black', fontsize=10,
                                 ax=ax, str_format='{:.0%}', ha='center', va='center',
                                 path_effects=[path_effects.Stroke(linewidth=1, foreground='white')])

    ax.set_title(f"Touch Heatmap - {player_name}", fontsize=18, color='black', pad=15)
    return save_plot_as_base64(fig)

def create_progressive_passes_viz(events_df, team_name):
    """Create visualization for progressive passes using Matplotlib"""
    # Filter progressive passes
    if 'type' not in events_df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Column 'type' not found in DataFrame.", ha='center', va='center', fontsize=12)
        return save_plot_as_base64(fig)
        
    prog_passes = events_df[
        (events_df['type'] == 'Pass') &
        (events_df['team'].apply(get_entity_name) == team_name) &
        (events_df['pass_outcome'].isna()) &
        # Statsbomb X progression definition can be complex. Simple definition based on distance:
        ( (events_df['pass_end_x'] - events_df['x'] > 10) & (events_df['x'] < 60) ) | # Start in own half, move 10m
        ( (events_df['pass_end_x'] - events_df['x'] > 10) & (events_df['x'] >= 60) & (events_df['pass_end_x'] > events_df['x']) ) # Start in opp half, move 10m forward
        # A more common definition: If starts in own half, must end in opp half OR travel 30m. If starts in opp half, must travel 10m.
        # For simplicity, using the 10m forward rule if not into final third.
        # Or, like example, passes into final third: (events_df.x<80)&(events_df.pass_end_x>80)
    ].copy()

    required_prog_cols = ['player', 'x', 'pass_end_x'] # Add more if your definition requires
    if not all(col in prog_passes.columns for col in required_prog_cols):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Missing required columns for progressive passes.", 
                  ha='center', va='center', fontsize=10)
        ax.set_title(f"Progressive Passes - {team_name}", fontsize=16)
        return save_plot_as_base64(fig)

    if prog_passes.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No progressive pass data available", ha='center', va='center', fontsize=12, color='red')
        ax.set_title(f"Progressive Passes - {team_name}", fontsize=16)
        return save_plot_as_base64(fig)
    
    prog_passes['player_name'] = prog_passes['player'].apply(get_entity_name)
    player_counts = prog_passes.groupby('player_name').size().reset_index(name='progressive_passes')
    player_counts = player_counts.sort_values('progressive_passes', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, max(6, len(player_counts) * 0.5))) # Adjust height
    ax.barh(player_counts['player_name'], player_counts['progressive_passes'], 
            color='skyblue', edgecolor='black')
    
    ax.set_xlabel("Number of Progressive Passes", fontsize=12)
    ax.set_ylabel("Player", fontsize=12)
    ax.set_title(f"Progressive Passes - {team_name}", fontsize=16, pad=15)
    plt.tight_layout() # Adjust layout to prevent labels cutting off
    
    return save_plot_as_base64(fig)

def create_xg_timeline(events_df, match_info=None):
    """Create xG timeline for a match using Matplotlib"""
    if 'type' not in events_df.columns:
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.text(0.5, 0.5, "Column 'type' not found in DataFrame.", ha='center', va='center', fontsize=12)
        return save_plot_as_base64(fig)

    shots_df = events_df[events_df['type'] == 'Shot'].copy()

    required_xg_cols = ['minute', 'team', 'shot_statsbomb_xg']
    if not all(col in shots_df.columns for col in required_xg_cols):
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.text(0.5, 0.5, "Missing required columns for xG timeline.", 
                  ha='center', va='center', fontsize=10)
        ax.set_title("Expected Goals (xG) Timeline", fontsize=16)
        return save_plot_as_base64(fig)
        
    if shots_df.empty or shots_df['shot_statsbomb_xg'].isnull().all():
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.text(0.5, 0.5, "No shot data with xG available", ha='center', va='center', fontsize=12, color='red')
        ax.set_title("Expected Goals (xG) Timeline", fontsize=16)
        return save_plot_as_base64(fig)

    shots_df['team_name'] = shots_df['team'].apply(get_entity_name)
    shots_df = shots_df.sort_values('minute')
    
    teams = shots_df['team_name'].unique()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    colors = plt.cm.get_cmap('viridis', len(teams)) # Get distinct colors

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

        ax.plot(timeline_data['minute'], timeline_data['cumulative_xg'], 
                label=f"{team} xG ({timeline_data['cumulative_xg'].iloc[-1]:.2f})", 
                linewidth=2.5, marker='o', markersize=5, markevery=team_shots['minute'].tolist(), 
                color=colors(i))

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

    return save_plot_as_base64(fig)

def save_plot_as_base64(fig):
    """Convert matplotlib figure to base64 string"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor=fig.get_facecolor()) # Preserve facecolor
    buf.seek(0)
    encoded = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig) # Close the figure to free memory
    return f"data:image/png;base64,{encoded}"