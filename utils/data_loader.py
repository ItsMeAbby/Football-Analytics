import matplotlib
matplotlib.use('Agg')
from statsbombpy import sb
from mplsoccer import  Sbopen
import pandas as pd
import numpy as np
from functools import lru_cache
parser = Sbopen()
@lru_cache(maxsize=1)
def load_euro_2024_matches():
    """Load all Euro 2024 matches"""
    return sb.matches(competition_id=55, season_id=282)

@lru_cache(maxsize=10)
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
    
    event, related, freeze, tactics = parser.event(match_id)
    return event, related, freeze, tactics
@lru_cache(maxsize=1)
def load_tournament_data():
    """Load all event data for Euro 2024"""
    return sb.competition_events(
        country='Europe',
        division='UEFA Euro',
        season='2024',
        gender="male"
    )

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