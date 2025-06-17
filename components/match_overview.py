import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go

import pandas as pd
from utils.data_loader import load_euro_2024_matches, load_match_data, get_all_teams, get_tournament_stats
from utils.plot_utils_mpl import create_shot_map, create_pass_network, create_xg_timeline

def layout():
    # Get tournament stats
    stats = get_tournament_stats()
    teams = get_all_teams()
    matches = load_euro_2024_matches()
    
    return html.Div([
        # Header with tournament stats
        html.Div([
            html.H2("⚽ UEFA Euro 2024 Dashboard", className="text-center mb-4"),
            html.Div([
                html.Div([
                    html.H4(f"{stats['total_matches']}", className="text-primary text-center"),
                    html.P("Total Matches", className="text-center text-muted")
                ], className="col-md-3"),
                html.Div([
                    html.H4(f"{stats['total_teams']}", className="text-primary text-center"),
                    html.P("Teams", className="text-center text-muted")
                ], className="col-md-3"),
                html.Div([
                    html.H4(f"{stats['total_goals']}", className="text-primary text-center"),
                    html.P("Total Goals", className="text-center text-muted")
                ], className="col-md-3"),
                html.Div([
                    html.H4(f"{stats['avg_goals_per_match']:.1f}", className="text-primary text-center"),
                    html.P("Goals per Match", className="text-center text-muted")
                ], className="col-md-3"),
            ], className="row")
        ], className="card p-4 mb-4"),
        
        # Match selector
        html.Div([
            html.H4("🔍 Match Analysis", className="mb-3"),
            html.Div([
                html.Div([
                    html.Label("Select Teams:", className="fw-bold"),
                    dcc.Dropdown(
                        id='team-dropdown',
                        options=[{'label': team, 'value': team} for team in teams],
                        value=teams[0] if teams else None,
                        placeholder="Select a team..."
                    )
                ], className="col-md-6"),
                html.Div([
                    html.Label("Select Match:", className="fw-bold"),
                    dcc.Dropdown(
                        id='match-dropdown',
                        placeholder="Select a match..."
                    )
                ], className="col-md-6"),
            ], className="row")
        ], className="card p-4 mb-4"),
        
        # Match details and analysis
        html.Div(id='match-analysis-content'),
        
        # Tournament overview charts
        dbc.Card([
            dbc.CardBody([
                html.H4("📊 Tournament Overview", className="mb-3"),
                dbc.Tabs([
                    dbc.Tab(label="Goals Overview", tab_id="goals-tab"),
                    dbc.Tab(label="Team Performance", tab_id="team-tab"),
                    dbc.Tab(label="Match Statistics", tab_id="stats-tab"),
                ], id="overview-tabs", active_tab="goals-tab"),
                html.Div(id='overview-content', className="mt-3")
            ])
        ], className="mb-4"),
        
    ], className="container-fluid p-4")

@callback(
    Output('match-dropdown', 'options'),
    Output('match-dropdown', 'value'),
    Input('team-dropdown', 'value')
)
def update_match_options(selected_team):
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
    Output('match-analysis-content', 'children'),
    Input('match-dropdown', 'value')
)
def update_match_analysis(match_id):
    if not match_id:
        return html.P("Please select a match to view analysis.")
    
    try:
        # Load match data
        events_df = load_match_data(match_id)
        matches = load_euro_2024_matches()
        match_info = matches[matches['match_id'] == match_id].iloc[0]
        
        home_team = match_info['home_team']
        away_team = match_info['away_team']
        
        return dbc.Card([
            dbc.CardBody([
                html.H4(f"🏟️ {home_team} vs {away_team}", className="text-center mb-4"),
                dbc.Row([
                    dbc.Col([
                        html.H5(f"Final Score: {match_info['home_score']} - {match_info['away_score']}", 
                               className="text-center text-primary")
                    ], width=12)
                ]),
                
                # Match visualizations
                dbc.Tabs([
                    dbc.Tab(label="Shot Maps", tab_id="shots"),
                    dbc.Tab(label="Pass Networks", tab_id="passes"),
                    dbc.Tab(label="xG Timeline", tab_id="xg"),
                ], id="match-tabs", active_tab="shots"),
                
                html.Div(id='match-viz-content', className="mt-3")
            ])
        ])
        
    except Exception as e:
        return dbc.Alert(f"Error loading match data: {str(e)}", color="danger")

@callback(
    Output('match-viz-content', 'children'),
    Input('match-tabs', 'active_tab'),
    Input('match-dropdown', 'value')
)
def update_match_visualizations(active_tab, match_id):
    if not match_id:
        return html.P("Please select a match.")
    
    try:
        events_df = load_match_data(match_id)
        matches = load_euro_2024_matches()
        match_info = matches[matches['match_id'] == match_id].iloc[0]
        
        home_team = match_info['home_team']
        away_team = match_info['away_team']
        
        if active_tab == "shots":
            home_shot_map = create_shot_map(events_df, home_team)
            away_shot_map = create_shot_map(events_df, away_team)
            
            return dbc.Row([
                dbc.Col([
                    html.H5(f"{home_team} Shots", className="text-center"),
                    html.Img(style={'width': '80%', 'max-width': '800px'},src=home_shot_map)
                ], width=6),
                dbc.Col([
                    html.H5(f"{away_team} Shots", className="text-center"),
                    html.Img(style={'width': '80%', 'max-width': '800px'},src=away_shot_map)
                ], width=6),
            ])
        
        elif active_tab == "passes":
            home_pass_network = create_pass_network(events_df, home_team)
            away_pass_network = create_pass_network(events_df, away_team)
            
            return dbc.Row([
                dbc.Col([
                    html.H5(f"{home_team} Pass Network", className="text-center"),
                    html.Img(style={'width': '80%', 'max-width': '800px'},src=home_pass_network)
                ], width=6),
                dbc.Col([
                    html.H5(f"{away_team} Pass Network", className="text-center"),
                    html.Img(style={'width': '80%', 'max-width': '800px'},src=away_pass_network)
                ], width=6),
            ])
        
        elif active_tab == "xg":
            xg_timeline = create_xg_timeline(events_df, match_info)
            
            return dbc.Row([
                dbc.Col([
                    html.Img(style={'width': '80%', 'max-width': '800px'},src=xg_timeline)
                ], width=12)
            ])
            
    except Exception as e:
        return dbc.Alert(f"Error creating visualization: {str(e)}", color="danger")

@callback(
    Output('overview-content', 'children'),
    Input('overview-tabs', 'active_tab')
)
def update_overview_content(active_tab):
    try:
        matches = load_euro_2024_matches()
        
        if active_tab == "goals-tab":
            # Goals scored by team
            home_goals = matches.groupby('home_team')['home_score'].sum()
            away_goals = matches.groupby('away_team')['away_score'].sum()
            total_goals = home_goals.add(away_goals, fill_value=0).sort_values(ascending=False)
            
            fig = go.Figure(go.Bar(
                x=total_goals.values,
                y=total_goals.index,
                orientation='h',
                marker=dict(color='lightblue', line=dict(color='darkblue', width=1))
            ))
            
            fig.update_layout(
                title="Total Goals by Team",
                xaxis_title="Goals Scored",
                yaxis_title="Team",
                height=600
            )
            
            return html.Div([
    return html.Img(style={'width': '80%', 'max-width': '800px'},src=fig)
])
        
        elif active_tab == "team-tab":
            # Team performance metrics
            team_stats = []
            teams = get_all_teams()
            
            for team in teams:
                team_matches = matches[
                    (matches['home_team'] == team) | (matches['away_team'] == team)
                ]
                
                wins = 0
                draws = 0
                losses = 0
                goals_for = 0
                goals_against = 0
                
                for _, match in team_matches.iterrows():
                    if match['home_team'] == team:
                        goals_for += match['home_score']
                        goals_against += match['away_score']
                        if match['home_score'] > match['away_score']:
                            wins += 1
                        elif match['home_score'] == match['away_score']:
                            draws += 1
                        else:
                            losses += 1
                    else:
                        goals_for += match['away_score']
                        goals_against += match['home_score']
                        if match['away_score'] > match['home_score']:
                            wins += 1
                        elif match['away_score'] == match['home_score']:
                            draws += 1
                        else:
                            losses += 1
                
                team_stats.append({
                    'Team': team,
                    'Matches': len(team_matches),
                    'Wins': wins,
                    'Draws': draws,
                    'Losses': losses,
                    'Goals For': goals_for,
                    'Goals Against': goals_against,
                    'Goal Difference': goals_for - goals_against,
                    'Points': wins * 3 + draws
                })
            
            df_stats = pd.DataFrame(team_stats).sort_values('Points', ascending=False)
            
            fig = go.Figure(go.Bar(
                x=df_stats['Team'],
                y=df_stats['Points'],
                marker=dict(color='gold', line=dict(color='orange', width=1))
            ))
            
            fig.update_layout(
                title="Team Points (3 for win, 1 for draw)",
                xaxis_title="Team",
                yaxis_title="Points",
                height=500
            )
            
            return html.Div([
    return html.Img(style={'width': '80%', 'max-width': '800px'},src=fig)
])
        
        elif active_tab == "stats-tab":
            # Match statistics
            matches['total_goals'] = matches['home_score'] + matches['away_score']
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=matches['total_goals'],
                nbinsx=10,
                marker=dict(color='lightgreen', line=dict(color='darkgreen', width=1))
            ))
            
            fig.update_layout(
                title="Distribution of Total Goals per Match",
                xaxis_title="Total Goals",
                yaxis_title="Number of Matches",
                height=400
            )
            
            return html.Div([
    return html.Img(style={'width': '80%', 'max-width': '800px'},src=fig)
])
            
    except Exception as e:
        return dbc.Alert(f"Error creating overview: {str(e)}", color="danger")