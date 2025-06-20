import matplotlib
matplotlib.use('Agg')
from statsbombpy import sb
from mplsoccer import  Sbopen
import pandas as pd
import numpy as np
from functools import lru_cache
# Avoid creating parser as a global object to prevent semaphore leaks
@lru_cache(maxsize=1)
def load_euro_2024_matches():
    """Load all Euro 2024 matches"""
    return sb.matches(competition_id=55, season_id=282)

@lru_cache(maxsize=20)
def load_match_data(match_id):
    """Load event data for a specific match"""
    events = sb.events(match_id=match_id)
    # Process coordinates
    events[['x', 'y']] = events['location'].apply(pd.Series)
    events[['pass_end_x', 'pass_end_y']] = events['pass_end_location'].apply(pd.Series)
    events[['carry_end_x', 'carry_end_y']] = events['carry_end_location'].apply(pd.Series)
    return events
@lru_cache(maxsize=10)
def load_sbopen_match_data(match_id):
    """Load event data for a specific match using sbopen"""
    
    # Create a new parser instance for each call to avoid semaphore leaks
    # This ensures proper cleanup of multiprocessing resources
    parser = Sbopen()
    event, related, freeze, tactics = parser.event(match_id)
    return event, related, freeze, tactics
@lru_cache(maxsize=1)
def load_tournament_data():
    """Load all event data for Euro 2024"""
    events = sb.competition_events(
        country='Europe',
        division='UEFA Euro',
        season='2024',
        gender="male"
    )
    
    # Process coordinates
    events[['x', 'y']] = events['location'].apply(pd.Series)
    events[['pass_end_x', 'pass_end_y']] = events['pass_end_location'].apply(pd.Series)
    events[['carry_end_x', 'carry_end_y']] = events['carry_end_location'].apply(pd.Series)
    
    return events

def get_team_matches(team_name):
    """Get matches for a specific team"""
    matches = load_euro_2024_matches()
    return matches[(matches['home_team'] == team_name) | (matches['away_team'] == team_name)]

def get_latest_match_id(team_name):
    """Get the latest match ID for a team"""
    team_matches = get_team_matches(team_name)
    team_matches = team_matches.sort_values(by='match_date', ascending=False)
    return team_matches.match_id.iloc[0] if not team_matches.empty else None

def get_all_teams():
    """Get list of all teams in Euro 2024"""
    matches = load_euro_2024_matches()
    home_teams = set(matches['home_team'].unique())
    away_teams = set(matches['away_team'].unique())
    return sorted(list(home_teams.union(away_teams)))

def get_tournament_stats():
    """Get basic tournament statistics"""
    matches = load_euro_2024_matches()
    return {
        'total_matches': len(matches),
        'total_teams': len(get_all_teams()),
        'total_goals': matches['home_score'].sum() + matches['away_score'].sum(),
        'avg_goals_per_match': (matches['home_score'].sum() + matches['away_score'].sum()) / len(matches)
    }

@lru_cache(maxsize=24)
def get_team_players(team_name):
    """Get all players for a specific team with caching"""
    events_df = load_tournament_data()
    team_events = events_df[
        events_df['team'].apply(
            lambda x: x.get('name', '') == team_name if isinstance(x, dict) else str(x) == team_name
        )
    ]
    
    # Get unique players
    players = team_events['player'].apply(
        lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
    ).unique()
    players = [p for p in players if p != 'Unknown' and pd.notna(p)]
    players.sort()
    
    return players

@lru_cache(maxsize=1)
def get_all_players():
    """Get all players in the tournament with caching"""
    events_df = load_tournament_data()
    players = events_df['player'].apply(
        lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
    ).unique()
    players = [p for p in players if p != 'Unknown' and pd.notna(p)]
    players.sort()
    
    return players

def warm_up_cache():
    """
    Pre-load data into cache to improve dashboard performance.
    Call this before starting the server to avoid slow initial loads.
    """
    print("🔥 Warming up cache...")
    
    try:
        # 1. Load tournament matches (cached with maxsize=1)
        print("📊 Loading Euro 2024 matches...")
        matches = load_euro_2024_matches()
        print(f"✅ Loaded {len(matches)} matches")
        
        # 2. Load tournament data (cached with maxsize=1)  
        print("🏆 Loading tournament data...")
        tournament_data = load_tournament_data()
        print(f"✅ Loaded {len(tournament_data)} events")
        
        # 3. Load all players (cached with maxsize=1)
        print("👥 Loading all players...")
        all_players = get_all_players()
        print(f"✅ Loaded {len(all_players)} players")
        
        # 4. Pre-load team players for all teams (cached with maxsize=24)
        print("🏟️  Loading team rosters...")
        teams = get_all_teams()
        for i, team in enumerate(teams, 1):
            try:
                players = get_team_players(team)
                print(f"   {i:2d}/{len(teams)} - {team}: {len(players)} players")
            except Exception as e:
                print(f"   ❌ Failed to load {team}: {e}")
        
        # 5. Pre-load recent match data for faster access (cached with maxsize=10)
        print("⚽ Pre-loading recent match data...")
        recent_matches = matches.head(10)  # Load last 10 matches
        for i, (_, match) in enumerate(recent_matches.iterrows(), 1):
            try:
                match_id = match['match_id']
                home_team = match['home_team']
                away_team = match['away_team']
                
                # Load both regular and sbopen data
                events = load_match_data(match_id)
                sbopen_data = load_sbopen_match_data(match_id)
                
                print(f"   {i:2d}/10 - {home_team} vs {away_team}: {len(events)} events")
            except Exception as e:
                print(f"   ❌ Failed to load match {match_id}: {e}")
        
        print("🚀 Cache warming completed successfully!")
        
        # Print cache stats
        print("\n📈 Cache Statistics:")
        print(f"   Tournament matches: {load_euro_2024_matches.cache_info()}")
        print(f"   Tournament data: {load_tournament_data.cache_info()}")
        print(f"   Match data: {load_match_data.cache_info()}")
        print(f"   SBOpen data: {load_sbopen_match_data.cache_info()}")
        print(f"   Team players: {get_team_players.cache_info()}")
        print(f"   All players: {get_all_players.cache_info()}")
        
    except Exception as e:
        print(f"❌ Error during cache warming: {e}")
        print("⚠️  Dashboard will still work, but initial loads may be slower")