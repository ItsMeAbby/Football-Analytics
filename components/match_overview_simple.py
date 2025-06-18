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
        # Header for match analysis
        html.Div([
            html.H2("🏟️ Match Analysis", 
                   style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50'}),
            html.P("Select a team and match to view detailed analysis including shot maps, pass networks, xG timeline, and comprehensive match statistics.", 
                   style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'lineHeight': '1.5'})
        ], style={
            'backgroundColor': 'white', 
            'padding': '25px', 
            'borderRadius': '15px',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
            'marginBottom': '25px'
        }),
        
        # Match selector
        html.Div([
            html.H4("🔍 Select Match", style={'marginBottom': '20px', 'color': '#2c3e50'}),
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
        
        
    ], style={
        'padding': '20px',
        'backgroundColor': '#f8f9fa',
        'minHeight': '100vh'
    })

def tournament_layout():
    """Separate layout for tournament overview"""
    try:
        stats = get_tournament_stats()
    except Exception as e:
        return html.Div([
            html.H2("📊 Tournament Overview", style={'textAlign': 'center', 'color': '#2c3e50'}),
            html.Div([
                html.P(f"Error loading data: {str(e)}", style={'color': '#e74c3c', 'textAlign': 'center'}),
                html.P("Please check your internet connection and try again.", style={'textAlign': 'center'})
            ], style={'backgroundColor': '#fff5f5', 'padding': '20px', 'borderRadius': '10px', 'border': '1px solid #e74c3c'})
        ])
    
    return html.Div([
        # Tournament header with key stats
        html.Div([
            html.H2("📊 UEFA Euro 2024 Tournament Overview", 
                   style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#2c3e50'}),
            html.Div([
                html.Div([
                    html.H3(f"{stats['total_matches']}", 
                           style={'textAlign': 'center', 'color': '#3498db', 'marginBottom': '5px', 'fontSize': '48px'}),
                    html.P("Total Matches", style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'fontWeight': 'bold'})
                ], style={'width': '25%', 'display': 'inline-block', 'textAlign': 'center'}),
                html.Div([
                    html.H3(f"{stats['total_teams']}", 
                           style={'textAlign': 'center', 'color': '#e74c3c', 'marginBottom': '5px', 'fontSize': '48px'}),
                    html.P("Teams", style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'fontWeight': 'bold'})
                ], style={'width': '25%', 'display': 'inline-block', 'textAlign': 'center'}),
                html.Div([
                    html.H3(f"{stats['total_goals']}", 
                           style={'textAlign': 'center', 'color': '#2ecc71', 'marginBottom': '5px', 'fontSize': '48px'}),
                    html.P("Total Goals", style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'fontWeight': 'bold'})
                ], style={'width': '25%', 'display': 'inline-block', 'textAlign': 'center'}),
                html.Div([
                    html.H3(f"{stats['avg_goals_per_match']:.1f}", 
                           style={'textAlign': 'center', 'color': '#f39c12', 'marginBottom': '5px', 'fontSize': '48px'}),
                    html.P("Goals per Match", style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'fontWeight': 'bold'})
                ], style={'width': '25%', 'display': 'inline-block', 'textAlign': 'center'}),
            ])
        ], style={
            'backgroundColor': 'white', 
            'padding': '30px', 
            'borderRadius': '15px',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
            'marginBottom': '30px'
        }),
        
        # Tournament overview charts
        html.Div([
            dcc.Tabs([
                dcc.Tab(label="⚽ Goals Overview", value="goals-tab", style={'padding': '12px', 'fontWeight': 'bold'}),
                dcc.Tab(label="🏆 Team Performance", value="team-tab", style={'padding': '12px', 'fontWeight': 'bold'}),
                dcc.Tab(label="📈 Tournament Stats", value="stats-tab", style={'padding': '12px', 'fontWeight': 'bold'}),
            ], id="overview-tabs", value="goals-tab"),
            html.Div(id='overview-content', style={'marginTop': '20px'})
        ], style={
            'backgroundColor': 'white', 
            'padding': '25px', 
            'borderRadius': '15px',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
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
            # Match header
            html.Div([
                html.H3(f"{home_team} vs {away_team}", 
                       style={'textAlign': 'center', 'marginBottom': '15px', 'color': '#2c3e50', 'fontSize': '28px'}),
                html.Div([
                    html.Span(f"{match_info['home_score']}", style={'fontSize': '36px', 'fontWeight': 'bold', 'color': "#000000"}),
                    html.Span(" - ", style={'fontSize': '24px', 'color': '#7f8c8d', 'margin': '0 15px'}),
                    html.Span(f"{match_info['away_score']}", style={'fontSize': '36px', 'fontWeight': 'bold', 'color': "#000000"})
                ], style={'textAlign': 'center', 'marginBottom': '25px'})
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '20px',
                'borderRadius': '15px',
                'marginBottom': '25px',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.05)'
            }),
            
            # Match visualizations
            dcc.Tabs([
                dcc.Tab(label="📍 Shot Maps", value="shots", style={'padding': '12px', 'fontWeight': 'bold'}),
                dcc.Tab(label="🔗 Pass Networks", value="passes", style={'padding': '12px', 'fontWeight': 'bold'}),
                dcc.Tab(label="📈 xG Timeline", value="xg", style={'padding': '12px', 'fontWeight': 'bold'}),
                dcc.Tab(label="📊 Match Stats", value="stats", style={'padding': '12px', 'fontWeight': 'bold'}),
                dcc.Tab(label="🎯 Key Events", value="events", style={'padding': '12px', 'fontWeight': 'bold'}),
            ], id="match-tabs", value="shots"),
            
            html.Div(id='match-viz-content', style={'marginTop': '25px'})
        ], style={
            'backgroundColor': 'white', 
            'padding': '25px', 
            'borderRadius': '15px',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
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
        
        # Determine team colors based on match result
        home_score = match_info['home_score']
        away_score = match_info['away_score']
        
        if home_score > away_score:
            # Home team wins
            home_color = '#2ecc71'  # Green for winner
            away_color = '#e74c3c'  # Red for loser
        elif away_score > home_score:
            # Away team wins
            home_color = '#e74c3c'  # Red for loser
            away_color = '#2ecc71'  # Green for winner
        else:
            # Draw - use different colors
            home_color = '#2ecc71'  # Green for first team
            away_color = '#3498db'  # Blue for second team
        
        if active_tab == "shots":
            home_shot_map = create_shot_map(events_df, home_team)
            away_shot_map = create_shot_map(events_df, away_team)
            
            return html.Div([
                # Statistics summary for shots
                html.Div([
                    html.H5("📊 Shot Statistics", style={'color': '#2c3e50', 'marginBottom': '15px', 'textAlign': 'center'}),
                    html.Div([
                        html.Div([
                            html.H6(f"{len(events_df[(events_df['type'] == 'Shot') & (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == home_team)])}", 
                                   style={'fontSize': '24px', 'color': home_color, 'margin': '0', 'fontWeight': 'bold'}),
                            html.P(f"{home_team} Shots", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{len(events_df[(events_df['type'] == 'Shot') & (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == away_team)])}", 
                                   style={'fontSize': '24px', 'color': away_color, 'margin': '0', 'fontWeight': 'bold'}),
                            html.P(f"{away_team} Shots", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{match_info['home_score'] + match_info['away_score']}", 
                                   style={'fontSize': '24px', 'color': '#2ecc71', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Total Goals", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{len(events_df[events_df['type'] == 'Foul Committed'])}", 
                                   style={'fontSize': '24px', 'color': '#e74c3c', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Total Fouls", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{len(events_df[(events_df['type'] == 'Shot') & (events_df['shot_outcome'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == 'Goal')])}", 
                                   style={'fontSize': '24px', 'color': '#f39c12', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Goals Scored", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                    ])
                ], style={
                    'backgroundColor': '#ecf0f1', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '20px'
                }),
                
                # Description section
                html.Div([
                    html.Div([
                        html.H5("📍 Shot Maps", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                        html.Span(" ℹ️", style={
                            'marginLeft': '10px', 
                            'cursor': 'pointer', 
                            'fontSize': '16px',
                            'color': '#3498db'
                        }, title="Shot maps show location and quality of shot attempts. Circle size = xG value")
                    ]),
                    html.Div([
                        html.P("Shot maps show the location and quality of all shot attempts during the match. Circle size represents Expected Goals (xG) value - larger circles indicate higher probability of scoring. Green circles with white centers show goals, red circles show other shots.", 
                               style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '10px'}),
                        html.Details([
                            html.Summary("📖 Why Shot Maps?", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                            html.Div([
                                html.P("• Reveals attacking patterns and shooting quality", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Shows efficiency: teams may have many shots but from poor positions", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Alternative visualizations: Heat maps, shot zones, or temporal shot charts", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• We chose scatter plots for precise location and xG representation", style={'margin': '5px 0', 'fontSize': '13px'})
                            ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                        ], style={'marginTop': '10px'})
                    ])
                ], style={
                    'backgroundColor': '#f8f9fa', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '20px'
                }),
                
                # Shot maps
                html.Div([
                    html.Div([
                        html.Div([
                            html.H5(f"{home_team} Shots", style={
                                'textAlign': 'center', 
                                'marginBottom': '15px', 
                                'color': home_color,
                                'fontSize': '18px',
                                'fontWeight': 'bold'
                            }),
                            html.Img(style={
                                'width': '100%', 
                                'maxWidth': '550px', 
                                'height': 'auto', 
                                'borderRadius': '12px', 
                                'boxShadow': '0 4px 15px rgba(0,0,0,0.15)'
                            }, src=home_shot_map)
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': '15px',
                            'borderRadius': '12px',
                            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '50%', 'display': 'inline-block', 'paddingRight': '10px'}),
                    
                    html.Div([
                        html.Div([
                            html.H5(f"{away_team} Shots", style={
                                'textAlign': 'center', 
                                'marginBottom': '15px', 
                                'color': away_color,
                                'fontSize': '18px',
                                'fontWeight': 'bold'
                            }),
                            html.Img(style={
                                'width': '100%', 
                                'maxWidth': '550px', 
                                'height': 'auto', 
                                'borderRadius': '12px', 
                                'boxShadow': '0 4px 15px rgba(0,0,0,0.15)'
                            }, src=away_shot_map)
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': '15px',
                            'borderRadius': '12px',
                            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '50%', 'display': 'inline-block', 'paddingLeft': '10px'}),
                ], style={'textAlign': 'center'})
            ])
        
        elif active_tab == "passes":
            home_pass_network = create_pass_network(events_df, home_team)
            away_pass_network = create_pass_network(events_df, away_team)
            
            return html.Div([
                # Statistics summary for passes
                html.Div([
                    html.H5("📊 Pass Statistics", style={'color': '#2c3e50', 'marginBottom': '15px', 'textAlign': 'center'}),
                    html.Div([
                        html.Div([
                            html.H6(f"{len(events_df[(events_df['type'] == 'Pass') & (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == home_team)])}", 
                                   style={'fontSize': '24px', 'color': home_color, 'margin': '0', 'fontWeight': 'bold'}),
                            html.P(f"{home_team} Passes", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{len(events_df[(events_df['type'] == 'Pass') & (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == away_team)])}", 
                                   style={'fontSize': '24px', 'color': away_color, 'margin': '0', 'fontWeight': 'bold'}),
                            html.P(f"{away_team} Passes", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{len(events_df[(events_df['type'] == 'Pass') & (events_df['pass_outcome'].isna())])}", 
                                   style={'fontSize': '24px', 'color': '#2ecc71', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Successful Passes", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{len(events_df[(events_df['type'] == 'Pass') & (events_df['pass_outcome'].notna())])}", 
                                   style={'fontSize': '24px', 'color': '#e74c3c', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Failed Passes", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{round((len(events_df[(events_df['type'] == 'Pass') & (events_df['pass_outcome'].isna())]) / len(events_df[events_df['type'] == 'Pass']) * 100) if len(events_df[events_df['type'] == 'Pass']) > 0 else 0, 1)}%", 
                                   style={'fontSize': '24px', 'color': '#f39c12', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Pass Accuracy", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                    ])
                ], style={
                    'backgroundColor': '#ecf0f1', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '20px'
                }),
                
                # Description section
                html.Div([
                    html.Div([
                        html.H5("🔗 Pass Networks", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                        html.Span(" ℹ️", style={
                            'marginLeft': '10px', 
                            'cursor': 'pointer', 
                            'fontSize': '16px',
                            'color': '#3498db'
                        }, title="Pass networks show team shape and passing relationships")
                    ]),
                    html.Div([
                        html.P("Pass networks show team shape and passing relationships. Node size represents passing activity, node position shows average field position, and line thickness shows pass frequency between players.", 
                               style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '10px'}),
                        html.Details([
                            html.Summary("📖 Why Pass Networks?", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                            html.Div([
                                html.P("• Reveals team formation and tactical structure", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Shows key playmakers and passing patterns", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Alternative visualizations: Heat maps, chord diagrams, or flow charts", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• We chose network graphs for clear relationship visualization", style={'margin': '5px 0', 'fontSize': '13px'})
                            ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                        ], style={'marginTop': '10px'})
                    ])
                ], style={
                    'backgroundColor': '#f8f9fa', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '20px'
                }),
                
                # Pass networks
                html.Div([
                    html.Div([
                        html.Div([
                            html.H5(f"{home_team} Pass Network", style={
                                'textAlign': 'center', 
                                'marginBottom': '15px', 
                                'color': home_color,
                                'fontSize': '18px',
                                'fontWeight': 'bold'
                            }),
                            html.Img(style={
                                'width': '100%', 
                                'maxWidth': '550px', 
                                'height': 'auto', 
                                'borderRadius': '12px', 
                                'boxShadow': '0 4px 15px rgba(0,0,0,0.15)'
                            }, src=home_pass_network)
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': '15px',
                            'borderRadius': '12px',
                            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '50%', 'display': 'inline-block', 'paddingRight': '10px'}),
                    
                    html.Div([
                        html.Div([
                            html.H5(f"{away_team} Pass Network", style={
                                'textAlign': 'center', 
                                'marginBottom': '15px', 
                                'color': away_color,
                                'fontSize': '18px',
                                'fontWeight': 'bold'
                            }),
                            html.Img(style={
                                'width': '100%', 
                                'maxWidth': '550px', 
                                'height': 'auto', 
                                'borderRadius': '12px', 
                                'boxShadow': '0 4px 15px rgba(0,0,0,0.15)'
                            }, src=away_pass_network)
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': '15px',
                            'borderRadius': '12px',
                            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '50%', 'display': 'inline-block', 'paddingLeft': '10px'}),
                ], style={'textAlign': 'center'})
            ])
        
        elif active_tab == "xg":
            # Create team colors list for xG timeline - match team order with data
            # The xG timeline function sorts teams alphabetically, so we need to map colors correctly
            teams_in_data = sorted([home_team, away_team])
            team_colors_dict = {home_team: home_color, away_team: away_color}
            team_colors_list = [team_colors_dict[team] for team in teams_in_data]
            xg_timeline = create_xg_timeline(events_df, match_info, team_colors_list)
            
            # Calculate xG values for statistics
            home_xg = events_df[
                (events_df['type'] == 'Shot') & 
                (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == home_team)
            ]['shot_statsbomb_xg'].sum()
            away_xg = events_df[
                (events_df['type'] == 'Shot') & 
                (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == away_team)
            ]['shot_statsbomb_xg'].sum()
            
            return html.Div([
                # Statistics summary for xG
                html.Div([
                    html.H5("📊 Expected Goals Statistics", style={'color': '#2c3e50', 'marginBottom': '15px', 'textAlign': 'center'}),
                    html.Div([
                        html.Div([
                            html.H6(f"{round(home_xg, 2)}", 
                                   style={'fontSize': '24px', 'color': home_color, 'margin': '0', 'fontWeight': 'bold'}),
                            html.P(f"{home_team} xG", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{round(away_xg, 2)}", 
                                   style={'fontSize': '24px', 'color': away_color, 'margin': '0', 'fontWeight': 'bold'}),
                            html.P(f"{away_team} xG", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{round(home_xg + away_xg, 2)}", 
                                   style={'fontSize': '24px', 'color': '#2ecc71', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Total xG", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{match_info['home_score'] + match_info['away_score']}", 
                                   style={'fontSize': '24px', 'color': '#f39c12', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Actual Goals", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{round(abs((home_xg + away_xg) - (match_info['home_score'] + match_info['away_score'])), 2)}", 
                                   style={'fontSize': '24px', 'color': '#e74c3c', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("xG Difference", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                    ])
                ], style={
                    'backgroundColor': '#ecf0f1', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '20px'
                }),
                
                # Description section
                html.Div([
                    html.Div([
                        html.H5("📈 Expected Goals Timeline", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                        html.Span(" ℹ️", style={
                            'marginLeft': '10px', 
                            'cursor': 'pointer', 
                            'fontSize': '16px',
                            'color': '#3498db'
                        }, title="xG timeline shows cumulative goal-scoring chances over time")
                    ]),
                    html.Div([
                        html.P("Expected Goals (xG) timeline shows the cumulative goal-scoring chances throughout the match. Each point represents a shot attempt, with the line showing how goal threat accumulated over time.", 
                               style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '10px'}),
                        html.Details([
                            html.Summary("📖 Why xG Timeline?", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                            html.Div([
                                html.P("• Shows match momentum and periods of dominance", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Reveals if the score reflects actual performance", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Alternative visualizations: xG difference, rolling xG, or shot value charts", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• We chose cumulative line charts for clear temporal progression", style={'margin': '5px 0', 'fontSize': '13px'})
                            ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                        ], style={'marginTop': '10px'})
                    ])
                ], style={
                    'backgroundColor': '#f8f9fa', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '20px'
                }),
                
                # xG Timeline
                html.Div([
                    html.Img(style={
                        'width': '100%', 
                        'maxWidth': '900px', 
                        'height': 'auto', 
                        'borderRadius': '12px', 
                        'boxShadow': '0 4px 15px rgba(0,0,0,0.15)'
                    }, src=xg_timeline)
                ], style={
                    'backgroundColor': '#f8f9fa',
                    'padding': '20px',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                    'textAlign': 'center'
                })
            ])
        
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
            
            # Pass success/failure statistics
            home_successful_passes = len(events_df[
                (events_df['type'] == 'Pass') & 
                (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == home_team) &
                (events_df['pass_outcome'].isna())
            ])
            away_successful_passes = len(events_df[
                (events_df['type'] == 'Pass') & 
                (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == away_team) &
                (events_df['pass_outcome'].isna())
            ])
            
            home_failed_passes = len(events_df[
                (events_df['type'] == 'Pass') & 
                (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == home_team) &
                (events_df['pass_outcome'].notna())
            ])
            away_failed_passes = len(events_df[
                (events_df['type'] == 'Pass') & 
                (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == away_team) &
                (events_df['pass_outcome'].notna())
            ])
            
            return html.Div([
                # Description section
                html.Div([
                    html.Div([
                        html.H5("📊 Match Statistics", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                        html.Span(" ℹ️", style={
                            'marginLeft': '10px', 
                            'cursor': 'pointer', 
                            'fontSize': '16px',
                            'color': '#3498db'
                        }, title="Click for more information")
                    ]),
                    html.Div([
                        html.P("Comprehensive match statistics comparing both teams across key performance metrics. Bar length shows relative performance, with numbers displayed inside each segment.", 
                               style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '10px'}),
                        html.Details([
                            html.Summary("📖 Why These Statistics?", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                            html.Div([
                                html.P("• Provides quick visual comparison between teams", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Shows both volume (shots) and quality (xG, shots on target)", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Alternative visualizations: Radar charts, tables, or percentage displays", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• We chose horizontal bars for easy comparison and clear value display", style={'margin': '5px 0', 'fontSize': '13px'})
                            ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                        ], style={'marginTop': '10px'})
                    ])
                ], style={
                    'backgroundColor': '#ecf0f1', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '25px'
                }),
                
                # Team headers
                html.Div([
                    html.Div([
                        html.H5(home_team, style={
                            'textAlign': 'center', 
                            'color': home_color, 
                            'marginBottom': '30px',
                            'fontSize': '20px',
                            'fontWeight': 'bold',
                            'padding': '10px',
                            'backgroundColor': '#ecf0f1',
                            'borderRadius': '8px'
                        })
                    ], style={'width': '35%', 'display': 'inline-block', 'paddingRight': '10px'}),
                    
                    html.Div([
                        html.H5("VS", style={
                            'textAlign': 'center', 
                            'color': '#34495e', 
                            'marginBottom': '30px',
                            'fontSize': '18px',
                            'fontWeight': 'bold'
                        })
                    ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center'}),
                    
                    html.Div([
                        html.H5(away_team, style={
                            'textAlign': 'center', 
                            'color': away_color, 
                            'marginBottom': '30px',
                            'fontSize': '20px',
                            'fontWeight': 'bold',
                            'padding': '10px',
                            'backgroundColor': '#ecf0f1',
                            'borderRadius': '8px'
                        })
                    ], style={'width': '35%', 'display': 'inline-block', 'paddingLeft': '10px'}),
                ]),
                
                # Stats comparison rows
                html.Div([
                    *[html.Div([
                        # Label on top
                        html.Div([
                            html.P(label, style={
                                'margin': '0 0 8px 0', 
                                'color': '#2c3e50', 
                                'fontWeight': 'bold',
                                'fontSize': '16px',
                                'textAlign': 'center'
                            })
                        ], style={'width': '100%', 'marginBottom': '5px'}),
                        
                        # Bar with numbers inside
                        html.Div([
                            html.Div([
                                html.Span(str(home_val), style={
                                    'color': 'white', 
                                    'fontWeight': 'bold',
                                    'fontSize': '16px',
                                    'position': 'absolute',
                                    'left': '50%',
                                    'top': '50%',
                                    'transform': 'translate(-50%, -50%)',
                                    'textShadow': '1px 1px 2px rgba(0,0,0,0.5)'
                                })
                            ], style={
                                'width': f"{max(5, (home_val / (home_val + away_val) * 100)) if (home_val + away_val) > 0 else 50}%",
                                'height': '40px',
                                'backgroundColor': home_color,
                                'display': 'inline-block',
                                'borderRadius': '20px 0 0 20px' if home_val >= away_val else '20px',
                                'position': 'relative',
                                'minWidth': '40px'
                            }),
                            html.Div([
                                html.Span(str(away_val), style={
                                    'color': 'white', 
                                    'fontWeight': 'bold',
                                    'fontSize': '16px',
                                    'position': 'absolute',
                                    'left': '50%',
                                    'top': '50%',
                                    'transform': 'translate(-50%, -50%)',
                                    'textShadow': '1px 1px 2px rgba(0,0,0,0.5)'
                                })
                            ], style={
                                'width': f"{max(5, (away_val / (home_val + away_val) * 100)) if (home_val + away_val) > 0 else 50}%",
                                'height': '40px',
                                'backgroundColor': away_color,
                                'display': 'inline-block',
                                'borderRadius': '0 20px 20px 0' if away_val < home_val else '20px',
                                'position': 'relative',
                                'minWidth': '40px'
                            })
                        ], style={'width': '100%', 'display': 'flex', 'borderRadius': '20px', 'overflow': 'hidden'})
                    ], style={
                        'marginBottom': '20px', 
                        'padding': '15px',
                        'backgroundColor': '#f8f9fa',
                        'borderRadius': '15px',
                        'boxShadow': '0 3px 10px rgba(0,0,0,0.1)'
                    }) for (home_val, away_val, label) in [
                        (home_shots, away_shots, "Shots"),
                        (home_shots_on_target, away_shots_on_target, "Shots on Target"),
                        (home_successful_passes, away_successful_passes, "Successful Passes"),
                        (home_failed_passes, away_failed_passes, "Failed Passes"),
                        (round(home_possession, 1), round(away_possession, 1), "Possession %"),
                        (round(home_xg, 2), round(away_xg, 2), "Expected Goals"),
                        (match_info['home_score'], match_info['away_score'], "Goals")
                    ]]
                ])
            ], style={
                'padding': '25px', 
                'backgroundColor': 'white', 
                'borderRadius': '15px',
                'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
                'margin': '0 auto',
                'width': '50%',
                'minWidth': '600px'
            })
        
        elif active_tab == "events":
            # Key Events Timeline
            key_events = []
            
            # Get goals
            goals = events_df[
                (events_df['type'] == 'Shot') & 
                (events_df['shot_outcome'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == 'Goal')
            ]
            
            for _, goal in goals.iterrows():
                team_name = goal['team'].get('name', '') if isinstance(goal['team'], dict) else str(goal['team'])
                player_name = goal['player'].get('name', '') if isinstance(goal['player'], dict) else str(goal['player'])
                key_events.append({
                    'minute': goal['minute'],
                    'type': 'Goal ⚽',
                    'team': team_name,
                    'player': player_name,
                    'description': f"Goal by {player_name}"
                })
            
            # Get cards and fouls with better detection
            try:
                # Check for different card-related columns that might exist
                card_columns = [col for col in events_df.columns if 'card' in col.lower()]
                foul_columns = [col for col in events_df.columns if 'foul' in col.lower()]
                
                # Try multiple approaches to find cards
                cards_found = pd.DataFrame()
                
                # Method 1: bad_behaviour_card column
                if 'bad_behaviour_card' in events_df.columns:
                    cards_method1 = events_df[events_df['bad_behaviour_card'].notna()]
                    cards_found = pd.concat([cards_found, cards_method1], ignore_index=True)
                
                # Method 2: Look for direct card events
                card_types = ['Yellow Card', 'Red Card', 'Second Yellow']
                card_events = events_df[events_df['type'].isin(card_types)]
                cards_found = pd.concat([cards_found, card_events], ignore_index=True)
                
                # Method 3: Look in foul events with card info
                if 'foul_committed_card' in events_df.columns:
                    foul_cards = events_df[
                        (events_df['type'] == 'Foul Committed') & 
                        (events_df['foul_committed_card'].notna())
                    ]
                    cards_found = pd.concat([cards_found, foul_cards], ignore_index=True)
                
                # Remove duplicates
                cards_found = cards_found.drop_duplicates()
                
                # Process found cards
                for _, card in cards_found.iterrows():
                    team_name = card['team'].get('name', '') if isinstance(card['team'], dict) else str(card['team'])
                    player_name = card['player'].get('name', '') if isinstance(card['player'], dict) else str(card['player'])
                    
                    # Determine card type
                    card_type = ""
                    card_icon = ""
                    
                    # Check multiple possible card fields
                    if 'bad_behaviour_card' in card and pd.notna(card['bad_behaviour_card']):
                        card_info = card['bad_behaviour_card']
                        card_type = card_info.get('name', '') if isinstance(card_info, dict) else str(card_info)
                    elif card['type'] in ['Yellow Card', 'Red Card', 'Second Yellow']:
                        card_type = card['type']
                    elif 'foul_committed_card' in card and pd.notna(card['foul_committed_card']):
                        card_info = card['foul_committed_card']
                        card_type = card_info.get('name', '') if isinstance(card_info, dict) else str(card_info)
                    
                    # Set appropriate icon
                    if 'Yellow' in card_type or 'yellow' in card_type.lower():
                        card_icon = '🟨'
                        display_type = 'Yellow Card'
                    elif 'Red' in card_type or 'red' in card_type.lower() or 'Second' in card_type:
                        card_icon = '🟥'
                        display_type = 'Red Card' if 'Second' not in card_type else 'Second Yellow (Red)'
                    else:
                        card_icon = '🟨'  # Default to yellow if unclear
                        display_type = card_type if card_type else 'Card'
                    
                    # Check for penalty
                    penalty_info = ""
                    if 'foul_committed_penalty' in card and pd.notna(card['foul_committed_penalty']):
                        penalty_info = " (Penalty awarded)"
                    
                    key_events.append({
                        'minute': card['minute'],
                        'type': f'{display_type} {card_icon}',
                        'team': team_name,
                        'player': player_name,
                        'description': f"{display_type} for {player_name}{penalty_info}"
                    })
                
                # Penalty fouls (without cards)
                if 'foul_committed_penalty' in events_df.columns:
                    penalty_fouls = events_df[
                        (events_df['type'] == 'Foul Committed') & 
                        (events_df['foul_committed_penalty'].notna()) &
                        (~events_df.index.isin(cards_found.index))  # Exclude those already processed as cards
                    ]
                    for _, foul in penalty_fouls.iterrows():
                        team_name = foul['team'].get('name', '') if isinstance(foul['team'], dict) else str(foul['team'])
                        player_name = foul['player'].get('name', '') if isinstance(foul['player'], dict) else str(foul['player'])
                        key_events.append({
                            'minute': foul['minute'],
                            'type': 'Penalty Foul ⚠️',
                            'team': team_name,
                            'player': player_name,
                            'description': f"Penalty foul by {player_name}"
                        })
                
            except Exception as e:
                # Debug: Add available columns info if no cards found
                if len(key_events) == 0:  # Only show if no other events
                    key_events.append({
                        'minute': 0,
                        'type': 'Debug Info 🔧',
                        'team': 'System',
                        'player': '',
                        'description': f"Available columns: {', '.join([col for col in events_df.columns if 'card' in col.lower() or 'foul' in col.lower()][:5])}"
                    })
            
            # Get major fouls without cards
            try:
                major_fouls = events_df[
                    (events_df['type'] == 'Foul Committed') & 
                    (events_df['bad_behaviour_card'].isna()) &
                    (events_df['foul_committed_offensive'].notna() if 'foul_committed_offensive' in events_df.columns else True)
                ].head(10)  # Limit to avoid too many events
                
                for _, foul in major_fouls.iterrows():
                    team_name = foul['team'].get('name', '') if isinstance(foul['team'], dict) else str(foul['team'])
                    player_name = foul['player'].get('name', '') if isinstance(foul['player'], dict) else str(foul['player'])
                    key_events.append({
                        'minute': foul['minute'],
                        'type': 'Foul ⚠️',
                        'team': team_name,
                        'player': player_name,
                        'description': f"Foul by {player_name}"
                    })
            except:
                pass
            
            # Get substitutions (if available)
            try:
                subs = events_df[events_df['type'] == 'Substitution']
                for _, sub in subs.iterrows():
                    team_name = sub['team'].get('name', '') if isinstance(sub['team'], dict) else str(sub['team'])
                    player_name = sub['player'].get('name', '') if isinstance(sub['player'], dict) else str(sub['player'])
                    replacement = sub['substitution_replacement'].get('name', '') if isinstance(sub.get('substitution_replacement'), dict) else str(sub.get('substitution_replacement', 'Unknown'))
                    key_events.append({
                        'minute': sub['minute'],
                        'type': 'Substitution 🔄',
                        'team': team_name,
                        'player': player_name,
                        'description': f"{replacement} on for {player_name}"
                    })
            except:
                pass
            
            # # Add half-time and full-time events
            # try:
            #     half_time_events = events_df[events_df['type'] == 'Half End']
            #     for _, ht in half_time_events.iterrows():
            #         period = ht.get('period', 1)
            #         key_events.append({
            #             'minute': ht['minute'],
            #             'type': f'Half Time ⏱️' if period == 1 else 'Full Time 🏁',
            #             'team': 'Match',
            #             'player': '',
            #             'description': f"End of {'first' if period == 1 else 'second'} half"
            #         })
            # except:
            #     pass
            
            # Sort by minute
            key_events.sort(key=lambda x: x['minute'])
            
            # Calculate event statistics
            total_goals = len([e for e in key_events if 'Goal' in e['type']])
            total_cards = len([e for e in key_events if 'Card' in e['type']])
            total_subs = len([e for e in key_events if 'Substitution' in e['type']])
            total_fouls = len([e for e in key_events if 'Foul' in e['type']])
            
            return html.Div([
                # Statistics summary for events
                html.Div([
                    html.H5("📊 Event Statistics", style={'color': '#2c3e50', 'marginBottom': '15px', 'textAlign': 'center'}),
                    html.Div([
                        html.Div([
                            html.H6(f"{total_goals}", 
                                   style={'fontSize': '24px', 'color': '#2ecc71', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Goals", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{total_cards}", 
                                   style={'fontSize': '24px', 'color': '#e74c3c', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Cards", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{total_subs}", 
                                   style={'fontSize': '24px', 'color': '#3498db', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Substitutions", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{total_fouls}", 
                                   style={'fontSize': '24px', 'color': '#f39c12', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Foul Events", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{len(key_events)}", 
                                   style={'fontSize': '24px', 'color': '#9b59b6', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Total Events", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'}),
                    ])
                ], style={
                    'backgroundColor': '#ecf0f1', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '20px'
                }),
                
                # Description section
                html.Div([
                    html.Div([
                        html.H5("🎯 Key Match Events", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                        html.Span(" ℹ️", style={
                            'marginLeft': '10px', 
                            'cursor': 'pointer', 
                            'fontSize': '16px',
                            'color': '#3498db'
                        }, title="Timeline of important match events with color-coded teams")
                    ]),
                    html.Div([
                        html.P("Chronological timeline of important match events including goals, cards, and substitutions. Events are color-coded by team for easy identification.", 
                               style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '10px'}),
                        html.Details([
                            html.Summary("📖 Why Event Timeline?", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                            html.Div([
                                html.P("• Shows match narrative and key turning points", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Helps understand tactical changes and momentum shifts", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Alternative visualizations: Match timeline, event maps, or flow diagrams", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• We chose chronological list for clear sequence understanding", style={'margin': '5px 0', 'fontSize': '13px'})
                            ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                        ], style={'marginTop': '10px'})
                    ])
                ], style={
                    'backgroundColor': '#f8f9fa', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '25px'
                }),
                
                # Events list
                html.Div([
                    html.Div(
                        [html.Div([
                            html.Div([
                                html.Span(f"{event['minute']}'", style={
                                    'fontSize': '18px',
                                    'fontWeight': 'bold',
                                    'color': '#2c3e50',
                                    'minWidth': '40px',
                                    'display': 'inline-block'
                                }),
                                html.Span(event['type'], style={
                                    'fontSize': '16px',
                                    'marginLeft': '15px',
                                    'fontWeight': 'bold'
                                }),
                                html.Span(f" - {event['description']}", style={
                                    'fontSize': '14px',
                                    'marginLeft': '10px',
                                    'color': 'rgba(255,255,255,0.9)'
                                })
                            ], style={
                                'padding': '12px 15px',
                                'backgroundColor': (
                                    '#34495e' if event['team'] == 'Match' 
                                    else home_color if event['team'] == home_team 
                                    else away_color
                                ),
                                'color': 'white',
                                'borderRadius': '10px',
                                'marginBottom': '8px',
                                'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
                            }, title=f"Team: {event['team']}")
                        ]) for event in key_events] if key_events else [
                            html.Div([
                                html.P("No key events recorded for this match.", 
                                       style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'margin': '20px 0'})
                            ])
                        ]
                    )
                ], style={
                    'backgroundColor': '#f8f9fa',
                    'padding': '20px',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                    'maxHeight': '400px',
                    'overflowY': 'auto'
                })
            ])
            
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
                margin=dict(l=100, r=50, t=80, b=50),
                hovermode='closest'
            )
            
            fig.update_traces(
                hovertemplate="<b>%{y}</b><br>Goals: %{x}<extra></extra>"
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
                xaxis={'tickangle': 45},
                hovermode='closest'
            )
            
            fig.update_traces(
                hovertemplate="<b>%{x}</b><br>Points: %{y}<extra></extra>"
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
                margin=dict(l=60, r=50, t=80, b=50),
                hovermode='closest'
            )
            
            fig.update_traces(
                hovertemplate="Goals: %{x}<br>Matches: %{y}<extra></extra>"
            )

            return dcc.Graph(figure=fig, style={'height': '400px'})

            
    except Exception as e:
        return html.P(f"Error creating overview: {str(e)}", 
                     style={'color': '#e74c3c', 'textAlign': 'center'})
