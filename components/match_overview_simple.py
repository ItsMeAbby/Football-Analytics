import matplotlib
matplotlib.use('Agg')
import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_euro_2024_matches, load_match_data, get_all_teams, get_tournament_stats
from utils.plot_utils_mpl import create_shot_map, create_pass_network, create_xg_timeline

def layout():
    # Get tournament stats
    try:
        stats = get_tournament_stats()
        teams = get_all_teams()
    except Exception as e:
        return html.Div([
            html.H2("Euro 2024 Dashboard", className="text-center"),
            html.Div([
                html.P(f"Error loading data: {str(e)}", className="text-danger text-center"),
                html.P("Please check your internet connection and try again.", className="text-center")
            ], className="alert alert-warning")
        ])
    
    return html.Div([
        # Header with tournament stats
        html.Div([
            html.H2("⚽ UEFA Euro 2024 Dashboard", 
                   style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#2c3e50'}),
            html.Div([
                html.Div([
                    html.H4(f"{stats['total_matches']}", 
                           style={'textAlign': 'center', 'color': '#3498db', 'marginBottom': '5px'}),
                    html.P("Total Matches", style={'textAlign': 'center', 'color': '#7f8c8d'})
                ], style={'width': '25%', 'display': 'inline-block', 'textAlign': 'center'}),
                html.Div([
                    html.H4(f"{stats['total_teams']}", 
                           style={'textAlign': 'center', 'color': '#3498db', 'marginBottom': '5px'}),
                    html.P("Teams", style={'textAlign': 'center', 'color': '#7f8c8d'})
                ], style={'width': '25%', 'display': 'inline-block', 'textAlign': 'center'}),
                html.Div([
                    html.H4(f"{stats['total_goals']}", 
                           style={'textAlign': 'center', 'color': '#3498db', 'marginBottom': '5px'}),
                    html.P("Total Goals", style={'textAlign': 'center', 'color': '#7f8c8d'})
                ], style={'width': '25%', 'display': 'inline-block', 'textAlign': 'center'}),
                html.Div([
                    html.H4(f"{stats['avg_goals_per_match']:.1f}", 
                           style={'textAlign': 'center', 'color': '#3498db', 'marginBottom': '5px'}),
                    html.P("Goals per Match", style={'textAlign': 'center', 'color': '#7f8c8d'})
                ], style={'width': '25%', 'display': 'inline-block', 'textAlign': 'center'}),
            ])
        ], style={
            'backgroundColor': 'white', 
            'padding': '20px', 
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        }),
        
        # Match selector
        html.Div([
            html.H4("🔍 Match Analysis", style={'marginBottom': '20px', 'color': '#2c3e50'}),
            html.Div([
                html.Div([
                    html.Label("Select Team:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='team-dropdown',
                        options=[{'label': team, 'value': team} for team in teams],
                        value=teams[0] if teams else None,
                        placeholder="Select a team...",
                        style={'marginBottom': '10px'}
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'paddingRight': '10px'}),
                html.Div([
                    html.Label("Select Match:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='match-dropdown',
                        placeholder="Select a match...",
                        style={'marginBottom': '10px'}
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'paddingLeft': '10px'}),
            ])
        ], style={
            'backgroundColor': 'white', 
            'padding': '20px', 
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        }),
        
        # Match analysis content
        html.Div(id='match-analysis-content'),
        
        # Tournament overview charts
        html.Div([
            html.H4("📊 Tournament Overview", style={'marginBottom': '20px', 'color': '#2c3e50'}),
            dcc.Tabs([
                dcc.Tab(label="⚽ Goals Overview", value="goals-tab"),
                dcc.Tab(label="🏆 Team Performance", value="team-tab"),
                dcc.Tab(label="📈 Tournament Stats", value="stats-tab"),
            ], id="overview-tabs", value="goals-tab"),
            html.Div(id='overview-content', style={'marginTop': '20px'})
        ], style={
            'backgroundColor': 'white', 
            'padding': '20px', 
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        }),
        
    ], style={
        'padding': '20px',
        'backgroundColor': '#f8f9fa',
        'minHeight': '100vh'
    })

@callback(
    Output('match-dropdown', 'options'),
    Output('match-dropdown', 'value'),
    Input('team-dropdown', 'value')
)
def update_match_options(selected_team):
    if not selected_team:
        return [], None
    
    try:
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
    except Exception as e:
        return [], None

@callback(
    Output('match-analysis-content', 'children'),
    Input('match-dropdown', 'value')
)
def update_match_analysis(match_id):
    if not match_id:
        return html.P("Please select a match to view analysis.", 
                     style={'textAlign': 'center', 'color': '#7f8c8d'})
    
    try:
        # Load match data
        events_df = load_match_data(match_id)
        matches = load_euro_2024_matches()
        match_info = matches[matches['match_id'] == match_id].iloc[0]
        
        home_team = match_info['home_team']
        away_team = match_info['away_team']
        
        return html.Div([
            html.H4(f"🏟️ {home_team} vs {away_team}", 
                   style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50'}),
            html.H5(f"Final Score: {match_info['home_score']} - {match_info['away_score']}", 
                   style={'textAlign': 'center', 'color': '#3498db', 'marginBottom': '20px'}),
            
            # Match visualizations
            dcc.Tabs([
                dcc.Tab(label="📍 Shot Maps", value="shots"),
                dcc.Tab(label="🔗 Pass Networks", value="passes"),
                dcc.Tab(label="📈 xG Timeline", value="xg"),
                dcc.Tab(label="📊 Match Stats", value="stats"),
            ], id="match-tabs", value="shots"),
            
            html.Div(id='match-viz-content', style={'marginTop': '20px'})
        ], style={
            'backgroundColor': 'white', 
            'padding': '20px', 
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        })
        
    except Exception as e:
        return html.Div([
            html.P(f"Error loading match data: {str(e)}", 
                  style={'color': '#e74c3c', 'textAlign': 'center'})
        ], style={
            'backgroundColor': '#fff5f5', 
            'padding': '20px', 
            'borderRadius': '10px',
            'border': '1px solid #e74c3c'
        })

@callback(
    Output('match-viz-content', 'children'),
    Input('match-tabs', 'value'),
    Input('match-dropdown', 'value')
)
def update_match_visualizations(active_tab, match_id):
    if not match_id:
        return html.P("Please select a match.", style={'textAlign': 'center'})
    
    try:
        events_df = load_match_data(match_id)
        matches = load_euro_2024_matches()
        match_info = matches[matches['match_id'] == match_id].iloc[0]
        
        home_team = match_info['home_team']
        away_team = match_info['away_team']
        
        if active_tab == "shots":
            home_shot_map = create_shot_map(events_df, home_team)
            away_shot_map = create_shot_map(events_df, away_team)
            
            return html.Div([
                html.Div([
                    html.H5(f"{home_team} Shots", style={'textAlign': 'center', 'marginBottom': '15px', 'color': '#2c3e50'}),
                    html.Img(style={'width': '100%', 'maxWidth': '600px', 'height': 'auto', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}, src=home_shot_map)
                ], style={'width': '50%', 'display': 'inline-block', 'paddingRight': '10px', 'textAlign': 'center'}),
                html.Div([
                    html.H5(f"{away_team} Shots", style={'textAlign': 'center', 'marginBottom': '15px', 'color': '#2c3e50'}),
                    html.Img(style={'width': '100%', 'maxWidth': '600px', 'height': 'auto', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}, src=away_shot_map)
                ], style={'width': '50%', 'display': 'inline-block', 'paddingLeft': '10px', 'textAlign': 'center'}),
            ])
        
        elif active_tab == "passes":
            home_pass_network = create_pass_network(events_df, home_team)
            away_pass_network = create_pass_network(events_df, away_team)
            
            return html.Div([
                html.Div([
                    html.H5(f"{home_team} Pass Network", style={'textAlign': 'center', 'marginBottom': '15px', 'color': '#2c3e50'}),
                    html.Img(style={'width': '100%', 'maxWidth': '600px', 'height': 'auto', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}, src=home_pass_network)
                ], style={'width': '50%', 'display': 'inline-block', 'paddingRight': '10px', 'textAlign': 'center'}),
                html.Div([
                    html.H5(f"{away_team} Pass Network", style={'textAlign': 'center', 'marginBottom': '15px', 'color': '#2c3e50'}),
                    html.Img(style={'width': '100%', 'maxWidth': '600px', 'height': 'auto', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}, src=away_pass_network)
                ], style={'width': '50%', 'display': 'inline-block', 'paddingLeft': '10px', 'textAlign': 'center'}),
            ])
        
        elif active_tab == "xg":
            xg_timeline = create_xg_timeline(events_df, match_info)
            
            return html.Div([
                html.H5("Expected Goals Timeline", style={'textAlign': 'center', 'marginBottom': '15px', 'color': '#2c3e50'}),
                html.Img(style={'width': '100%', 'maxWidth': '1000px', 'height': 'auto', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}, src=xg_timeline)
            ], style={'textAlign': 'center'})
        
        elif active_tab == "stats":
            # Calculate match statistics
            home_stats = {}
            away_stats = {}
            
            # Total shots
            home_shots = len(events_df[(events_df['type'] == 'Shot') & (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == home_team)])
            away_shots = len(events_df[(events_df['type'] == 'Shot') & (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == away_team)])
            
            # Shots on target
            home_shots_on_target = len(events_df[
                (events_df['type'] == 'Shot') & 
                (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == home_team) &
                (events_df['shot_outcome'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)).isin(['Goal', 'Saved']))
            ])
            away_shots_on_target = len(events_df[
                (events_df['type'] == 'Shot') & 
                (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == away_team) &
                (events_df['shot_outcome'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)).isin(['Goal', 'Saved']))
            ])
            
            # Possession (based on pass count)
            home_passes = len(events_df[(events_df['type'] == 'Pass') & (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == home_team)])
            away_passes = len(events_df[(events_df['type'] == 'Pass') & (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == away_team)])
            total_passes = home_passes + away_passes
            home_possession = (home_passes / total_passes * 100) if total_passes > 0 else 0
            away_possession = (away_passes / total_passes * 100) if total_passes > 0 else 0
            
            # xG values
            home_xg = events_df[
                (events_df['type'] == 'Shot') & 
                (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == home_team)
            ]['shot_statsbomb_xg'].sum()
            away_xg = events_df[
                (events_df['type'] == 'Shot') & 
                (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == away_team)
            ]['shot_statsbomb_xg'].sum()
            
            return html.Div([
                html.H5("Match Statistics", style={'textAlign': 'center', 'marginBottom': '25px', 'color': '#2c3e50'}),
                
                # Stats comparison
                html.Div([
                    # Home team column
                    html.Div([
                        html.H6(home_team, style={'textAlign': 'center', 'color': '#3498db', 'marginBottom': '20px'})
                    ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center'}),
                    
                    # Stats labels column
                    html.Div([
                        html.P("Shots", style={'margin': '10px 0', 'fontWeight': 'bold'}),
                        html.P("Shots on Target", style={'margin': '10px 0', 'fontWeight': 'bold'}),
                        html.P("Possession %", style={'margin': '10px 0', 'fontWeight': 'bold'}),
                        html.P("Expected Goals", style={'margin': '10px 0', 'fontWeight': 'bold'}),
                        html.P("Goals", style={'margin': '10px 0', 'fontWeight': 'bold'}),
                    ], style={'width': '40%', 'display': 'inline-block', 'textAlign': 'center'}),
                    
                    # Away team column
                    html.Div([
                        html.H6(away_team, style={'textAlign': 'center', 'color': '#e74c3c', 'marginBottom': '20px'})
                    ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center'}),
                ]),
                
                # Stats values
                html.Div([
                    # Home team values
                    html.Div([
                        html.P(f"{home_shots}", style={'margin': '10px 0', 'color': '#3498db', 'fontWeight': 'bold'}),
                        html.P(f"{home_shots_on_target}", style={'margin': '10px 0', 'color': '#3498db', 'fontWeight': 'bold'}),
                        html.P(f"{home_possession:.1f}%", style={'margin': '10px 0', 'color': '#3498db', 'fontWeight': 'bold'}),
                        html.P(f"{home_xg:.2f}", style={'margin': '10px 0', 'color': '#3498db', 'fontWeight': 'bold'}),
                        html.P(f"{match_info['home_score']}", style={'margin': '10px 0', 'color': '#3498db', 'fontWeight': 'bold', 'fontSize': '18px'}),
                    ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center'}),
                    
                    # Stat bars
                    html.Div([
                        # Shots bar
                        html.Div([
                            html.Div(style={
                                'width': f"{(home_shots / (home_shots + away_shots) * 100) if (home_shots + away_shots) > 0 else 50}%",
                                'height': '20px',
                                'backgroundColor': '#3498db',
                                'display': 'inline-block'
                            }),
                            html.Div(style={
                                'width': f"{(away_shots / (home_shots + away_shots) * 100) if (home_shots + away_shots) > 0 else 50}%",
                                'height': '20px',
                                'backgroundColor': '#e74c3c',
                                'display': 'inline-block'
                            })
                        ], style={'margin': '10px 0', 'border': '1px solid #ddd', 'borderRadius': '10px', 'overflow': 'hidden'}),
                        
                        # Shots on target bar
                        html.Div([
                            html.Div(style={
                                'width': f"{(home_shots_on_target / (home_shots_on_target + away_shots_on_target) * 100) if (home_shots_on_target + away_shots_on_target) > 0 else 50}%",
                                'height': '20px',
                                'backgroundColor': '#3498db',
                                'display': 'inline-block'
                            }),
                            html.Div(style={
                                'width': f"{(away_shots_on_target / (home_shots_on_target + away_shots_on_target) * 100) if (home_shots_on_target + away_shots_on_target) > 0 else 50}%",
                                'height': '20px',
                                'backgroundColor': '#e74c3c',
                                'display': 'inline-block'
                            })
                        ], style={'margin': '10px 0', 'border': '1px solid #ddd', 'borderRadius': '10px', 'overflow': 'hidden'}),
                        
                        # Possession bar
                        html.Div([
                            html.Div(style={
                                'width': f"{home_possession}%",
                                'height': '20px',
                                'backgroundColor': '#3498db',
                                'display': 'inline-block'
                            }),
                            html.Div(style={
                                'width': f"{away_possession}%",
                                'height': '20px',
                                'backgroundColor': '#e74c3c',
                                'display': 'inline-block'
                            })
                        ], style={'margin': '10px 0', 'border': '1px solid #ddd', 'borderRadius': '10px', 'overflow': 'hidden'}),
                        
                        # xG bar
                        html.Div([
                            html.Div(style={
                                'width': f"{(home_xg / (home_xg + away_xg) * 100) if (home_xg + away_xg) > 0 else 50}%",
                                'height': '20px',
                                'backgroundColor': '#3498db',
                                'display': 'inline-block'
                            }),
                            html.Div(style={
                                'width': f"{(away_xg / (home_xg + away_xg) * 100) if (home_xg + away_xg) > 0 else 50}%",
                                'height': '20px',
                                'backgroundColor': '#e74c3c',
                                'display': 'inline-block'
                            })
                        ], style={'margin': '10px 0', 'border': '1px solid #ddd', 'borderRadius': '10px', 'overflow': 'hidden'}),
                        
                        # Goals bar
                        html.Div([
                            html.Div(style={
                                'width': f"{(match_info['home_score'] / (match_info['home_score'] + match_info['away_score']) * 100) if (match_info['home_score'] + match_info['away_score']) > 0 else 50}%",
                                'height': '25px',
                                'backgroundColor': '#3498db',
                                'display': 'inline-block'
                            }),
                            html.Div(style={
                                'width': f"{(match_info['away_score'] / (match_info['home_score'] + match_info['away_score']) * 100) if (match_info['home_score'] + match_info['away_score']) > 0 else 50}%",
                                'height': '25px',
                                'backgroundColor': '#e74c3c',
                                'display': 'inline-block'
                            })
                        ], style={'margin': '10px 0', 'border': '1px solid #ddd', 'borderRadius': '10px', 'overflow': 'hidden'}),
                    ], style={'width': '40%', 'display': 'inline-block'}),
                    
                    # Away team values
                    html.Div([
                        html.P(f"{away_shots}", style={'margin': '10px 0', 'color': '#e74c3c', 'fontWeight': 'bold'}),
                        html.P(f"{away_shots_on_target}", style={'margin': '10px 0', 'color': '#e74c3c', 'fontWeight': 'bold'}),
                        html.P(f"{away_possession:.1f}%", style={'margin': '10px 0', 'color': '#e74c3c', 'fontWeight': 'bold'}),
                        html.P(f"{away_xg:.2f}", style={'margin': '10px 0', 'color': '#e74c3c', 'fontWeight': 'bold'}),
                        html.P(f"{match_info['away_score']}", style={'margin': '10px 0', 'color': '#e74c3c', 'fontWeight': 'bold', 'fontSize': '18px'}),
                    ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center'}),
                ])
            ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'})
            
    except Exception as e:
        return html.P(f"Error creating visualization: {str(e)}", 
                     style={'color': '#e74c3c', 'textAlign': 'center'})

@callback(
    Output('overview-content', 'children'),
    Input('overview-tabs', 'value')
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
                title={
                    'text': "⚽ Total Goals by Team",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#2c3e50'}
                },
                xaxis_title="Goals Scored",
                yaxis_title="Team",
                height=600,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50'},
                margin=dict(l=100, r=50, t=80, b=50)
            )
            
            return dcc.Graph(figure=fig, style={'height': '600px'})

        
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
                    'Points': wins * 3 + draws
                })
            
            df_stats = pd.DataFrame(team_stats).sort_values('Points', ascending=False)
            
            fig = go.Figure(go.Bar(
                x=df_stats['Team'],
                y=df_stats['Points'],
                marker=dict(color='gold', line=dict(color='orange', width=1))
            ))
            
            fig.update_layout(
                title={
                    'text': "🏆 Team Points (3 for win, 1 for draw)",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50'}
                },
                xaxis_title="Team",
                yaxis_title="Points",
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50'},
                margin=dict(l=60, r=50, t=80, b=100),
                xaxis={'tickangle': 45}
            )
            
            return dcc.Graph(figure=fig, style={'height': '500px'})

        
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
                title={
                    'text': "📈 Goals per Match Distribution",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50'}
                },
                xaxis_title="Total Goals per Match",
                yaxis_title="Number of Matches",
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50'},
                margin=dict(l=60, r=50, t=80, b=50)
            )

            return dcc.Graph(figure=fig, style={'height': '400px'})

            
    except Exception as e:
        return html.P(f"Error creating overview: {str(e)}", 
                     style={'color': '#e74c3c', 'textAlign': 'center'})
