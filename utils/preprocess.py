"""
Data preprocessing module for creating summaries and caches
Handles data aggregation, caching, and statistical computations
"""

import matplotlib
matplotlib.use('Agg')
import os
import pickle
import hashlib
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class DataCache:
    """Simple caching mechanism for processed data"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, pd.DataFrame):
            # Use DataFrame hash for cache key
            return hashlib.md5(str(data.values.tobytes()).encode()).hexdigest()
        else:
            return hashlib.md5(str(data).encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached data"""
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def set(self, key: str, data: Any) -> None:
        """Store data in cache"""
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)


def create_match_summary(events_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create high-level match summary statistics
    
    Args:
        events_df: DataFrame of match events
        
    Returns:
        Dictionary containing match summary
    """
    if events_df.empty:
        return {}
    
    summary = {
        'total_events': len(events_df),
        'event_types': events_df.get('event_category', pd.Series()).value_counts().to_dict(),
        'duration': None,
        'teams': [],
        'players': []
    }
    
    # Extract team information
    if 'team' in events_df.columns:
        teams = events_df['team'].apply(
            lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
        ).unique().tolist()
        summary['teams'] = teams
    
    # Extract player information
    if 'player' in events_df.columns:
        players = events_df['player'].apply(
            lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
        ).unique().tolist()
        summary['players'] = [p for p in players if p != 'Unknown']
    
    # Calculate match duration
    if 'timestamp' in events_df.columns:
        try:
            start_time = events_df['timestamp'].min()
            end_time = events_df['timestamp'].max()
            summary['duration'] = str(end_time - start_time)
        except:
            pass
    
    return summary


def create_player_summary(events_df: pd.DataFrame, player_name: str) -> Dict[str, Any]:
    """
    Create player-specific summary statistics
    
    Args:
        events_df: DataFrame of match events
        player_name: Name of the player to analyze
        
    Returns:
        Dictionary containing player summary
    """
    if events_df.empty:
        return {}
    
    # Filter events for specific player
    player_events = events_df[
        events_df['player'].apply(
            lambda x: x.get('name', '') == player_name if isinstance(x, dict) else str(x) == player_name
        )
    ]
    
    if player_events.empty:
        return {'player': player_name, 'events': 0}
    
    summary = {
        'player': player_name,
        'total_events': len(player_events),
        'event_breakdown': player_events.get('event_category', pd.Series()).value_counts().to_dict(),
        'positions': [],
        'team': None
    }
    
    # Extract team
    if 'team' in player_events.columns:
        team_data = player_events['team'].iloc[0]
        summary['team'] = team_data.get('name', 'Unknown') if isinstance(team_data, dict) else str(team_data)
    
    # Extract position information
    if 'position' in player_events.columns:
        positions = player_events['position'].apply(
            lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
        ).unique().tolist()
        summary['positions'] = [p for p in positions if p != 'Unknown']
    
    return summary


def create_team_summary(events_df: pd.DataFrame, team_name: str) -> Dict[str, Any]:
    """
    Create team-specific summary statistics
    
    Args:
        events_df: DataFrame of match events
        team_name: Name of the team to analyze
        
    Returns:
        Dictionary containing team summary
    """
    if events_df.empty:
        return {}
    
    # Filter events for specific team
    team_events = events_df[
        events_df['team'].apply(
            lambda x: x.get('name', '') == team_name if isinstance(x, dict) else str(x) == team_name
        )
    ]
    
    if team_events.empty:
        return {'team': team_name, 'events': 0}
    
    summary = {
        'team': team_name,
        'total_events': len(team_events),
        'event_breakdown': team_events.get('event_category', pd.Series()).value_counts().to_dict(),
        'players': [],
        'formations': []
    }
    
    # Extract player list
    if 'player' in team_events.columns:
        players = team_events['player'].apply(
            lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
        ).unique().tolist()
        summary['players'] = [p for p in players if p != 'Unknown']
    
    return summary


# Initialize global cache instance
cache = DataCache()
