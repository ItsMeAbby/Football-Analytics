import matplotlib
matplotlib.use('Agg')
import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_euro_2024_matches, load_match_data, get_all_teams, get_tournament_stats, load_sbopen_match_data
from utils.plot_utils import create_shot_map as create_shot_map_plotly, create_pass_network as create_pass_network_plotly, create_xg_timeline as create_xg_timeline_plotly, create_formation_viz, matplotlib_plot_as_base64

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
                dcc.Tab(label="⚽ Goals Analysis", value="goals-tab", style={'padding': '12px', 'fontWeight': 'bold'}),
                dcc.Tab(label="🏆 Team Performance", value="team-tab", style={'padding': '12px', 'fontWeight': 'bold'}, ),
                dcc.Tab(label="📈 Match Insights", value="stats-tab", style={'padding': '12px', 'fontWeight': 'bold'}),
                # dcc.Tab(label="🔎 Top Performers", value="players-tab", style={'padding': '12px', 'fontWeight': 'bold'}, title="See leading players and team statistics"),
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
                dcc.Tab(label="📍 Shot Maps", value="shots", style={'padding': '12px', 'fontWeight': 'bold'}, ),
                dcc.Tab(label="🔗 Pass Networks", value="passes", style={'padding': '12px', 'fontWeight': 'bold'},),
                dcc.Tab(label="📈 xG Timeline", value="xg", style={'padding': '12px', 'fontWeight': 'bold'}, ),
                dcc.Tab(label="📊 Match Stats", value="stats", style={'padding': '12px', 'fontWeight': 'bold'},),
                dcc.Tab(label="🎯 Key Events", value="events", style={'padding': '12px', 'fontWeight': 'bold'}),
                dcc.Tab(label="💰 Formations", value="formations", style={'padding': '12px', 'fontWeight': 'bold'}),
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
        sb_event,sb_related, sb_freeze, sb_tactics = load_sbopen_match_data(match_id)
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
            # Create interactive Plotly shot maps
            home_shot_map_fig = create_shot_map_plotly(events_df, home_team)
            away_shot_map_fig = create_shot_map_plotly(events_df, away_team)
            
            # Set titles with team colors
            home_shot_map_fig.update_layout(
                title=f"<b><span style='color:{home_color}'>{home_team} Shots</span></b>",
                title_x=0.5,
                margin=dict(t=50, b=20, l=20, r=20),
                paper_bgcolor='#f8f9fa',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            away_shot_map_fig.update_layout(
                title=f"<b><span style='color:{away_color}'>{away_team} Shots</span></b>",
                title_x=0.5,
                margin=dict(t=50, b=20, l=20, r=20),
                paper_bgcolor='#f8f9fa',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            return html.Div([
                # Statistics summary for shots
                html.Div([
                    html.H5("📊 Match Statistics", style={'color': '#2c3e50', 'marginBottom': '15px', 'textAlign': 'center'}),
                    html.Div([
                        html.Div([
                            html.H6(f"{len(events_df[(events_df['type'] == 'Shot') & (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == home_team)])}", 
                                   style={'fontSize': '24px', 'color': home_color, 'margin': '0', 'fontWeight': 'bold'}),
                            html.P(f"{home_team} Shots", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '16.6%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{len(events_df[(events_df['type'] == 'Shot') & (events_df['team'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == away_team)])}", 
                                   style={'fontSize': '24px', 'color': away_color, 'margin': '0', 'fontWeight': 'bold'}),
                            html.P(f"{away_team} Shots", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '16.6%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{match_info['home_score'] + match_info['away_score']}", 
                                   style={'fontSize': '24px', 'color': '#2ecc71', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Total Goals", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '16.6%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{len(events_df[events_df['type'] == 'Foul Committed'])}", 
                                   style={'fontSize': '24px', 'color': '#e74c3c', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Total Fouls", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '16.6%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{len(events_df[(events_df['type'] == 'Shot') & (events_df['shot_outcome'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == 'Goal')])}", 
                                   style={'fontSize': '24px', 'color': '#f39c12', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Player Goals", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0', 'title': 'Goals scored directly by players (not own goals)'})
                        ], style={'width': '16.6%', 'display': 'inline-block', 'textAlign': 'center'}),
                        html.Div([
                            html.H6(f"{len(events_df[events_df['type'] == 'Own Goal For'])}", 
                                   style={'fontSize': '24px', 'color': '#9b59b6', 'margin': '0', 'fontWeight': 'bold'}),
                            html.P("Own Goals", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                        ], style={'width': '16.6%', 'display': 'inline-block', 'textAlign': 'center'}),
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
                        }, title="Shot maps show location and quality of shot attempts. Circle size = xG value. Hover over shots for details.")
                    ]),
                    html.Div([
                        html.P("Shot maps show the location and quality of all shot attempts during the match. Circle size represents Expected Goals (xG) value - larger circles indicate higher probability of scoring. Different colors indicate different shot outcomes, with goals highlighted with gold circles and labeled with ⚽. Hover over any shot for detailed information including the player's name, xG value, and outcome. Note: Own goals are not shown on shot maps as they are not recorded as shots.", 
                               style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '10px'}),
                        html.Div([
                            html.P([
                                "Own goals in this match: ",
                                html.Span(f"{len(events_df[events_df['type'] == 'Own Goal For'])}", 
                                        style={'fontWeight': 'bold', 'color': '#9b59b6'})
                            ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '5px', 'fontStyle': 'italic'}),
                        ]) if 'Own Goal For' in events_df['type'].values else None,
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
                
                # Interactive Shot maps
                html.Div([
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                figure=home_shot_map_fig,
                                config={'displayModeBar': False},
                                style={
                                    'height': '500px',
                                    'width': '100%',
                                    'borderRadius': '12px',
                                    'boxShadow': '0 4px 15px rgba(0,0,0,0.15)'
                                }
                            )
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': '15px',
                            'borderRadius': '12px',
                            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '50%', 'display': 'inline-block', 'paddingRight': '10px'}),
                    
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                figure=away_shot_map_fig,
                                config={'displayModeBar': False},
                                style={
                                    'height': '500px',
                                    'width': '100%',
                                    'borderRadius': '12px',
                                    'boxShadow': '0 4px 15px rgba(0,0,0,0.15)'
                                }
                            )
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
            # Create interactive Plotly pass networks
            home_pass_network_fig = create_pass_network_plotly(events_df, home_team)
            away_pass_network_fig = create_pass_network_plotly(events_df, away_team)
            
            # Set titles with team colors
            home_pass_network_fig.update_layout(
                title=f"<b><span style='color:{home_color}'>{home_team} Pass Network</span></b>",
                title_x=0.5,
                margin=dict(t=50, b=20, l=20, r=20),
                paper_bgcolor='#f8f9fa',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            away_pass_network_fig.update_layout(
                title=f"<b><span style='color:{away_color}'>{away_team} Pass Network</span></b>",
                title_x=0.5,
                margin=dict(t=50, b=20, l=20, r=20),
                paper_bgcolor='#f8f9fa',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
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
                        }, title="Pass networks show team shape and passing relationships. Hover over players and connections for details.")
                    ]),
                    html.Div([
                        html.P("Pass networks show team shape and passing relationships. Player nodes are labeled with position acronyms (GK, CB, LW, etc.) instead of names for better tactical understanding. Node size represents passing involvement, node position shows average field position, and line thickness shows pass frequency between players. Different node shapes indicate substituted players. Hover over nodes or connections for detailed information including player names, positions, and passing statistics.", 
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
                
                # Interactive Pass networks
                html.Div([
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                figure=home_pass_network_fig,
                                config={'displayModeBar': False},
                                style={
                                    'height': '500px',
                                    'width': '100%',
                                    'borderRadius': '12px',
                                    'boxShadow': '0 4px 15px rgba(0,0,0,0.15)'
                                }
                            )
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': '15px',
                            'borderRadius': '12px',
                            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '50%', 'display': 'inline-block', 'paddingRight': '10px'}),
                    
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                figure=away_pass_network_fig,
                                config={'displayModeBar': False},
                                style={
                                    'height': '500px',
                                    'width': '100%',
                                    'borderRadius': '12px',
                                    'boxShadow': '0 4px 15px rgba(0,0,0,0.15)'
                                }
                            )
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
            # Create interactive Plotly xG timeline
            xg_timeline_fig = create_xg_timeline_plotly(events_df, match_info)
            
            # Set colors for teams - carefully check for string match
            for trace in xg_timeline_fig.data:
                if trace.name and home_team in str(trace.name):
                    trace.line.color = home_color
                elif trace.name and away_team in str(trace.name):
                    trace.line.color = away_color
            
            # Update layout
            xg_timeline_fig.update_layout(
                title=f"<b>Expected Goals (xG) Timeline</b>",
                title_x=0.5,
                margin=dict(t=50, b=20, l=50, r=20),
                paper_bgcolor='#f8f9fa',
                plot_bgcolor='white'
            )
            
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
                        }, title="xG timeline shows cumulative goal-scoring chances over time. Hover for details.")
                    ]),
                    html.Div([
                        html.P("Expected Goals (xG) timeline shows the cumulative goal-scoring chances throughout the match. Each point represents a shot attempt, with the line showing how goal threat accumulated over time. Vertical dashed lines mark actual goals scored with player names displayed. Lines are color-coded by team for easy comparison. Hover over any point to see detailed information and use the unified hover mode to compare teams at specific minutes of the match.", 
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
                
                # Interactive xG Timeline
                html.Div([
                    dcc.Graph(
                        figure=xg_timeline_fig,
                        config={'displayModeBar': False},
                        style={
                            'height': '500px',
                            'width': '100%',
                            'borderRadius': '12px',
                            'boxShadow': '0 4px 15px rgba(0,0,0,0.15)'
                        }
                    )
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
                        html.P("Comprehensive match statistics comparing both teams across key performance metrics. The color-coded bars represent each team's relative performance, with the exact values displayed inside. Statistics include shots, shots on target, successful and failed passes, possession percentage, expected goals (xG), and actual goals scored. This visualization provides a clear side-by-side comparison of team performance across multiple dimensions.", 
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
        
        elif active_tab == "formations":
            # Create formation visualizations for both teams
            try:
                home_formation_fig = create_formation_viz(sb_event,sb_related,sb_freeze,sb_tactics,home_team,True)
                away_formation_fig = create_formation_viz(sb_event,sb_related,sb_freeze,sb_tactics,away_team)
            except Exception as e:
                print(f"Error creating formation visualizations: {e}")
                return html.Div([
                    html.P(f"Error creating formation visualizations: {str(e)}", 
                          style={'color': '#e74c3c', 'textAlign': 'center'})
                ])
            
            # Note: We don't need to update_layout since the figures are already styled in the create_formation_viz function
            # Set titles with team colors
            # Update matplotlib figures with titles and styling
            home_formation_fig.suptitle(f"{home_team} Formation", 
                                        color=home_color, 
                                        fontweight='bold', 
                                        fontsize=16, 
                                        y=0.98)
            
            away_formation_fig.suptitle(f"{away_team} Formation", 
                                        color=away_color, 
                                        fontweight='bold', 
                                        fontsize=16, 
                                        y=0.98)
            
            # Set figure background colors
            home_formation_fig.patch.set_facecolor('#f8f9fa')
            away_formation_fig.patch.set_facecolor('#f8f9fa')
            
            # Adjust layout for better display
            home_formation_fig.tight_layout(rect=[0, 0, 1, 0.96])
            away_formation_fig.tight_layout(rect=[0, 0, 1, 0.96])
            return html.Div([
                # Description section
                html.Div([
                    html.Div([
                        html.H5("💰 Team Formations", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                        html.Span(" ℹ️", style={
                            'marginLeft': '10px', 
                            'cursor': 'pointer', 
                            'fontSize': '16px',
                            'color': '#3498db'
                        }, title="Hover over players for details")
                    ]),
                    html.Div([
                        html.P("Team formations with player position heatmaps showing where each player operated during the match. Players are labeled with position acronyms (GK, CB, LW, etc.) and their names. The heatmaps reveal player movement patterns and positional tendencies through color intensity. Brighter areas indicate zones where players spent more time.", 
                               style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '10px'}),
                        html.Details([
                            html.Summary("📖 Why Formation Visualizations?", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                            html.Div([
                                html.P("• Shows actual tactical setup beyond the nominal formation", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Reveals player movement patterns and positional flexibility", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Alternative visualizations: Static formation diagrams or player tracking maps", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• We chose heatmap overlays to show both position and movement range", style={'margin': '5px 0', 'fontSize': '13px'})
                            ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                        ], style={'marginTop': '10px'})
                    ])
                ], style={
                    'backgroundColor': '#f8f9fa', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '20px'
                }),
                
                # Interactive Formation Visualizations
                html.Div([
                    html.Div([
                        html.Div([
                            html.Img(
                                src=matplotlib_plot_as_base64(home_formation_fig),
                                style={
                                    'height': '1000px',
                                    'width': '100%',
                                    'borderRadius': '12px',
                                    'boxShadow': '0 4px 15px rgba(0,0,0,0.15)',
                                    'objectFit': 'contain'
                                }
                            )
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': '15px',
                            'borderRadius': '12px',
                            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '50%', 'display': 'inline-block', 'paddingRight': '10px'}),
                    
                    html.Div([
                        html.Div([
                            html.Img(
                                src=matplotlib_plot_as_base64(away_formation_fig),
                                style={
                                    'height': '1000px',
                                    'width': '100%',
                                    'borderRadius': '12px',
                                    'boxShadow': '0 4px 15px rgba(0,0,0,0.15)',
                                    'objectFit': 'contain'
                                }
                            )
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': '15px',
                            'borderRadius': '12px',
                            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '50%', 'display': 'inline-block', 'paddingLeft': '10px'}),
                ], style={'textAlign': 'center'})
            ])
            
        elif active_tab == "events":
            # Key Events Timeline
            key_events = []
            
            # Get regular goals
            goals = events_df[
                (events_df['type'] == 'Shot') & 
                (events_df['shot_outcome'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else str(x)) == 'Goal')
            ]
            
            # Get own goals
            own_goals_for = events_df[events_df['type'] == 'Own Goal For'] if 'Own Goal For' in events_df['type'].values else pd.DataFrame()
            own_goals_against = events_df[events_df['type'] == 'Own Goal Against'] if 'Own Goal Against' in events_df['type'].values else pd.DataFrame()
            
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
                
            # Process own goals if there are any - avoid double counting
            processed_og_ids = set()  # Track which events we've already processed
            
            # Only process Own Goal For events to avoid duplicates
            for _, og in own_goals_for.iterrows():
                # Skip if we've already processed this event
                if og['id'] in processed_og_ids:
                    continue
                    
                # Add this event to processed list
                processed_og_ids.add(og['id'])
                
                # Find the team that benefited
                beneficiary_team = og['team'] if isinstance(og['team'], str) else og['team'].get('name', 'Unknown') if isinstance(og['team'], dict) else 'Unknown'
                
                # Try to find the other team and player involved from related events
                related_events = og.get('related_events', [])
                scorer_team = None
                scorer_name = 'Unknown'
                
                # Look for related Own Goal Against event to get the scorer
                if related_events and not own_goals_against.empty:
                    for _, related_og in own_goals_against.iterrows():
                        if related_og['id'] in related_events:
                            # Add related event to processed list
                            processed_og_ids.add(related_og['id'])
                            
                            scorer_team = related_og['team'] if isinstance(related_og['team'], str) else related_og['team'].get('name', 'Unknown') if isinstance(related_og['team'], dict) else 'Unknown'
                            scorer_name = related_og['player'] if isinstance(related_og['player'], str) else related_og['player'].get('name', 'Unknown') if isinstance(related_og['player'], dict) else 'Unknown'
                            break
                            
                # Add the own goal to key events
                key_events.append({
                    'minute': og['minute'],
                    'type': 'Own Goal 🥅',
                    'team': scorer_team if scorer_team else 'Unknown',  # Team of the player who scored the own goal
                    'player': scorer_name,
                    'description': f"Own goal by {scorer_name} (for {beneficiary_team})"
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
                        html.P("Chronological timeline of important match events including goals, cards, substitutions, and fouls. Events are color-coded by team and include minute markers, event type with icons (⚽ for goals, 🟨 for yellow cards, etc.), and detailed descriptions. This visualization helps track the match narrative and identify key turning points. Hover over events for additional information.", 
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
        # print error trace for debugging
        import traceback
        traceback.print_exc()
        return html.P(f"Error creating visualization: {str(e)}", 
                     style={'color': '#e74c3c', 'textAlign': 'center'})

@callback(
    Output('overview-content', 'children'),
    Input('overview-tabs', 'value')
)
def update_overview_content(active_tab):
    try:
        matches = load_euro_2024_matches()
        
        if active_tab == "players-tab":
            # Create Top Performers tab with player statistics
            # Placeholder data for demonstration
            top_scorers = [
                {"player": "C. Ronaldo", "team": "Portugal", "goals": 5, "assists": 2},
                {"player": "R. Lewandowski", "team": "Poland", "goals": 4, "assists": 1},
                {"player": "K. Mbappé", "team": "France", "goals": 4, "assists": 3},
                {"player": "R. Lukaku", "team": "Belgium", "goals": 3, "assists": 2},
                {"player": "P. Schick", "team": "Czech Republic", "goals": 3, "assists": 0},
                {"player": "G. Xhaka", "team": "Switzerland", "goals": 2, "assists": 3},
                {"player": "M. Depay", "team": "Netherlands", "goals": 2, "assists": 2},
                {"player": "K. Havertz", "team": "Germany", "goals": 2, "assists": 1}
            ]
            
            top_keepers = [
                {"player": "T. Courtois", "team": "Belgium", "clean_sheets": 4, "saves": 18, "save_ratio": 0.92},
                {"player": "J. Pickford", "team": "England", "clean_sheets": 3, "saves": 12, "save_ratio": 0.86},
                {"player": "G. Donnarumma", "team": "Italy", "clean_sheets": 3, "saves": 15, "save_ratio": 0.85},
                {"player": "M. Neuer", "team": "Germany", "clean_sheets": 2, "saves": 14, "save_ratio": 0.82},
                {"player": "Y. Sommer", "team": "Switzerland", "clean_sheets": 2, "saves": 16, "save_ratio": 0.80}
            ]
            
            # Create top scorers bar chart with assists overlay
            players = [p["player"] for p in top_scorers]
            goals = [p["goals"] for p in top_scorers]
            assists = [p["assists"] for p in top_scorers]
            teams = [p["team"] for p in top_scorers]
            
            # Create color gradient based on goals
            max_goals = max(goals)
            colors = [
                f'rgba(46, 204, 113, {0.6 + 0.4 * (g / max_goals)})' 
                for g in goals
            ]
            
            # Create scorers figure
            scorers_fig = go.Figure()
            
            # Add goals bars
            scorers_fig.add_trace(go.Bar(
                y=players,
                x=goals,
                orientation='h',
                name='Goals',
                marker=dict(color=colors, line=dict(color='rgba(46, 204, 113, 1)', width=1)),
                hovertemplate='<b>%{y}</b> (%{customdata})<br>Goals: %{x}<extra></extra>',
                customdata=teams
            ))
            
            # Add assists as overlay
            scorers_fig.add_trace(go.Bar(
                y=players,
                x=assists,
                orientation='h',
                name='Assists',
                marker=dict(color='rgba(52, 152, 219, 0.8)', line=dict(color='rgba(52, 152, 219, 1)', width=1)),
                hovertemplate='<b>%{y}</b> (%{customdata})<br>Assists: %{x}<extra></extra>',
                customdata=teams,
                opacity=0.7
            ))
            
            # Update layout
            scorers_fig.update_layout(
                title={
                    'text': "⚽ Top Goal Scorers",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#2c3e50'}
                },
                xaxis_title="Goals / Assists",
                yaxis_title=None,
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50'},
                margin=dict(l=100, r=20, t=80, b=30),
                hovermode='closest',
                barmode='overlay',
                xaxis=dict(gridcolor='rgba(211, 211, 211, 0.3)')
            )
            
            # Create goalkeeper stats visualization
            keeper_names = [k["player"] for k in top_keepers]
            clean_sheets = [k["clean_sheets"] for k in top_keepers]
            save_ratios = [k["save_ratio"] * 100 for k in top_keepers]  # Convert to percentage
            keeper_teams = [k["team"] for k in top_keepers]
            
            keepers_fig = go.Figure()
            
            # Add clean sheets bars
            keepers_fig.add_trace(go.Bar(
                x=keeper_names,
                y=clean_sheets,
                name='Clean Sheets',
                marker=dict(color='rgba(155, 89, 182, 0.8)', line=dict(color='rgba(155, 89, 182, 1)', width=1)),
                hovertemplate='<b>%{x}</b> (%{customdata})<br>Clean Sheets: %{y}<extra></extra>',
                customdata=keeper_teams,
                width=0.4,
                offset=-0.2
            ))
            
            # Add save ratio as second axis
            keepers_fig.add_trace(go.Scatter(
                x=keeper_names,
                y=save_ratios,
                mode='markers',
                name='Save Ratio (%)',
                marker=dict(
                    size=12,
                    color='rgba(241, 196, 15, 0.9)',
                    line=dict(color='rgba(243, 156, 18, 1)', width=2),
                    symbol='diamond'
                ),
                hovertemplate='<b>%{x}</b> (%{customdata})<br>Save Ratio: %{y:.1f}%<extra></extra>',
                customdata=keeper_teams,
                yaxis='y2'
            ))
            
            # Update layout with dual y-axis
            keepers_fig.update_layout(
                title={
                    'text': "🧤 Top Goalkeepers",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#2c3e50'}
                },
                xaxis_title=None,
                yaxis=dict(
                    title="Clean Sheets",
                    side="left",
                    range=[0, max(clean_sheets) * 1.2]
                ),
                yaxis2=dict(
                    title="Save Ratio (%)",
                    side="right",
                    range=[70, 100],
                    overlaying="y",
                    tickmode="linear",
                    dtick=5
                ),
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50'},
                margin=dict(l=50, r=70, t=80, b=50),
                hovermode='closest',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            # Create radar chart comparing top 5 players
            # Placeholder data for demonstration - would use real stats in production
            radar_data = [
                # Goals, Assists, Key Passes, Pass Accuracy, Shots per Game
                {'name': 'C. Ronaldo', 'stats': [5, 2, 1.8, 78, 4.2]},
                {'name': 'K. Mbappé', 'stats': [4, 3, 2.3, 82, 3.8]},
                {'name': 'R. Lewandowski', 'stats': [4, 1, 1.2, 75, 3.5]},
                {'name': 'R. Lukaku', 'stats': [3, 2, 1.0, 68, 2.9]},
                {'name': 'G. Xhaka', 'stats': [2, 3, 2.5, 91, 1.5]}
            ]
            
            # Categories for radar chart
            categories = ['Goals', 'Assists', 'Key Passes', 'Pass Accuracy', 'Shots per Game']
            
            # Create radar chart
            radar_fig = go.Figure()
            
            # Add each player as a separate trace
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
            for i, player in enumerate(radar_data):
                radar_fig.add_trace(go.Scatterpolar(
                    r=player['stats'],
                    theta=categories,
                    fill='toself',
                    name=player['name'],
                    line=dict(color=colors[i % len(colors)], width=2),
                    fillcolor=colors[i % len(colors)].replace(')', ', 0.2)').replace('rgb', 'rgba')
                ))
            
            radar_fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )
                ),
                title={
                    'text': "🌟 Player Comparison",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#2c3e50'}
                },
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50'},
                margin=dict(l=80, r=80, t=100, b=80)
            )
            
            return html.Div([
                # Description section
                html.Div([
                    html.Div([
                        html.H5("🔎 Top Performers", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                        html.Span(" ℹ️", style={
                            'marginLeft': '10px', 
                            'cursor': 'pointer', 
                            'fontSize': '16px',
                            'color': '#3498db'
                        }, title="Tournament's leading players across different statistics")
                    ]),
                    html.Div([
                        html.P("This dashboard showcases the tournament's top performers across multiple categories. Examine the leading goal scorers and assist providers, top goalkeepers based on clean sheets and save percentages, and compare elite players across various performance metrics using the radar chart visualization.", 
                               style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '10px'}),
                        html.Details([
                            html.Summary("📖 Player Analysis Insights", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                            html.Div([
                                html.P("• Goal scorers chart shows both goals (green) and assists (blue) for comparison", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Goalkeeper performance measured by clean sheets and save percentage", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Radar chart allows multi-dimensional comparison of top players", style={'margin': '5px 0', 'fontSize': '13px'}),
                                html.P("• Hover over visualizations for detailed player and team information", style={'margin': '5px 0', 'fontSize': '13px'})
                            ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                        ], style={'marginTop': '10px'})
                    ])
                ], style={
                    'backgroundColor': '#f8f9fa', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '20px'
                }),
                
                # Scorers and keepers in a row
                html.Div([
                    html.Div([
                        dcc.Graph(figure=scorers_fig, style={'height': '400px'})
                    ], style={'width': '50%', 'display': 'inline-block', 'paddingRight': '10px'}),
                    
                    html.Div([
                        dcc.Graph(figure=keepers_fig, style={'height': '400px'})
                    ], style={'width': '50%', 'display': 'inline-block', 'paddingLeft': '10px'}),
                ], style={'marginBottom': '20px'}),
                
                # Radar chart in full width
                html.Div([
                    dcc.Graph(figure=radar_fig, style={'height': '500px'})
                ])
            ])
        
        elif active_tab == "goals-tab":
            # Calculate team goal statistics
            team_goals_stats = []
            
            for team in get_all_teams():
                team_matches = matches[
                    (matches['home_team'] == team) | (matches['away_team'] == team)
                ]
                
                # Calculate goals for and against
                home_match_count = len(team_matches[team_matches['home_team'] == team])
                away_match_count = len(team_matches[team_matches['away_team'] == team])
                total_matches = home_match_count + away_match_count
                
                goals_scored_home = team_matches[team_matches['home_team'] == team]['home_score'].sum()
                goals_scored_away = team_matches[team_matches['away_team'] == team]['away_score'].sum()
                total_goals_scored = goals_scored_home + goals_scored_away
                
                goals_conceded_home = team_matches[team_matches['home_team'] == team]['away_score'].sum()
                goals_conceded_away = team_matches[team_matches['away_team'] == team]['home_score'].sum()
                total_goals_conceded = goals_conceded_home + goals_conceded_away
                
                # Calculate first/second half goals
                # This would require event data, simplifying for now
                
                # Calculate metrics
                goals_per_match = total_goals_scored / total_matches if total_matches > 0 else 0
                goal_difference = total_goals_scored - total_goals_conceded
                clean_sheets = len(team_matches[
                    ((team_matches['home_team'] == team) & (team_matches['away_score'] == 0)) | 
                    ((team_matches['away_team'] == team) & (team_matches['home_score'] == 0))
                ])
                
                team_goals_stats.append({
                    'team': team,
                    'goals_scored': total_goals_scored,
                    'goals_conceded': total_goals_conceded,
                    'goal_difference': goal_difference,
                    'goals_per_match': goals_per_match,
                    'clean_sheets': clean_sheets,
                    'matches_played': total_matches
                })
            
            # Convert to DataFrame and sort
            df_goals = pd.DataFrame(team_goals_stats)
            df_goals = df_goals.sort_values('goals_scored', ascending=False)
            
            # Create a color gradient based on goals scored
            max_goals = df_goals['goals_scored'].max()
            colors = [
                f'rgba(52, 152, 219, {0.5 + 0.5 * (goals / max_goals)})' 
                for goals in df_goals['goals_scored']
            ]
            
            # Create goals scored bar chart
            goals_fig = go.Figure()
            
            # Add goals scored bars
            goals_fig.add_trace(go.Bar(
                y=df_goals['team'],
                x=df_goals['goals_scored'],
                orientation='h',
                name='Goals Scored',
                marker=dict(color=colors, line=dict(color='rgba(52, 152, 219, 1)', width=1)),
                hovertemplate='<b>%{y}</b><br>Goals Scored: %{x}<br>Goals per Match: %{customdata[0]:.2f}<extra></extra>',
                customdata=df_goals[['goals_per_match']].values
            ))
            
            # Update layout with tournament logo/theme styling
            goals_fig.update_layout(
                title={
                    'text': "⚽ Goals Scored by Team",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#2c3e50'}
                },
                xaxis_title="Goals",
                yaxis_title=None,
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50'},
                margin=dict(l=100, r=20, t=80, b=30),
                hovermode='closest',
                barmode='overlay',
                xaxis=dict(gridcolor='rgba(211, 211, 211, 0.3)')
            )
            
            # Create metrics grid for top 5 teams
            top_teams = df_goals.head(5)['team'].tolist()
            
            return html.Div([
                # Description section
                html.Div([
                    html.Div([
                        html.H5("⚽ Goals Analysis", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                        html.Span(" ℹ️", style={
                            'marginLeft': '10px', 
                            'cursor': 'pointer', 
                            'fontSize': '16px',
                            'color': '#3498db'
                        }, title="Goal scoring patterns across the tournament")
                    ]),
                    html.Div([
                        html.P("This horizontal bar chart presents a comprehensive analysis of each team's goal-scoring performance throughout the tournament. Teams are meticulously ranked by their total goals scored, with the bar's color intensity proportionally representing scoring efficiency - deeper blues indicate more prolific attacking teams. This approach allows for instant visual identification of the most dangerous offensive sides.", 
                               style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '10px'}),
                        html.Details([
                            html.Summary("📖 Visualization Design Choices", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                            html.Div([
                                html.P(["• ", html.Strong("Why Horizontal Bars?"), " Horizontal bars provide clearer team name readability and better accommodate varying goal totals compared to vertical bar charts or radar charts. They also allow for immediate visual ranking."], style={'margin': '12px 0', 'fontSize': '13px'}),
                                html.P(["• ", html.Strong("Color Intensity Mapping:"), " The gradient blue color scheme visually reinforces the numerical data, making it easier to identify top scoring teams at a glance without relying solely on bar length."], style={'margin': '12px 0', 'fontSize': '13px'}),
                                html.P(["• ", html.Strong("Interactive Elements:"), " Hover details provide critical context by revealing goals per match statistics, offering insight into scoring efficiency beyond raw totals."], style={'margin': '12px 0', 'fontSize': '13px'}),
                                html.P(["• ", html.Strong("Alternative Approaches:"), " While we could have used scatter plots (goals vs. matches) or heat maps, the horizontal bar chart provides the clearest hierarchical view of offensive performance across all teams."], style={'margin': '12px 0', 'fontSize': '13px'}),
                                html.P(["• ", html.Strong("Complementary Displays:"), " The summary cards below spotlight top performers, providing additional metrics like goals per match and clean sheets for a more nuanced understanding of team performance."], style={'margin': '12px 0', 'fontSize': '13px'})
                            ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                        ], style={'marginTop': '10px'})
                    ])
                ], style={
                    'backgroundColor': '#f8f9fa', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '20px'
                }),
                
                # Goals visualization
                dcc.Graph(figure=goals_fig, style={'height': '500px'}),
                
                # Top teams goal statistics
                html.Div([
                    html.H5("⭐ Top Goal Scoring Teams", style={'color': '#2c3e50', 'marginBottom': '15px', 'textAlign': 'center'}),
                    html.Div([
                        # Create a container for the team cards
                        html.Div([
                            # Generate individual team cards
                            *[html.Div([
                                # Card content wrapper with team name and stats
                                html.Div([
                                    # Team name header - enlarged and styled better
                                    html.H4(team, style={
                                        'textAlign': 'center', 
                                        'color': '#2c3e50', 
                                        'margin': '0 0 15px 0',
                                        'padding': '10px 0',
                                        'borderBottom': '1px solid #ecf0f1',
                                        'fontSize': '20px'
                                    }),
                                    # Stats container
                                    html.Div([
                                        # Goals scored stat
                                        html.Div([
                                            html.H3(str(int(row['goals_scored'])), style={'fontSize': '28px', 'color': '#3498db', 'margin': '0', 'fontWeight': 'bold'}),
                                            html.P("Goals Scored", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                                        ], style={'width': '33%', 'display': 'inline-block', 'textAlign': 'center'}),
                                        # Goals per match stat
                                        html.Div([
                                            html.H3(f"{row['goals_per_match']:.1f}", style={'fontSize': '28px', 'color': '#2ecc71', 'margin': '0', 'fontWeight': 'bold'}),
                                            html.P("Goals/Match", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                                        ], style={'width': '33%', 'display': 'inline-block', 'textAlign': 'center'}),
                                        # Clean sheets stat
                                        html.Div([
                                            html.H3(str(int(row['clean_sheets'])), style={'fontSize': '28px', 'color': '#9b59b6', 'margin': '0', 'fontWeight': 'bold'}),
                                            html.P("Clean Sheets", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                                        ], style={'width': '33%', 'display': 'inline-block', 'textAlign': 'center'}),
                                    ])
                                ], style={
                                    'padding': '15px',
                                    'backgroundColor': 'white',
                                    'borderRadius': '10px',
                                    'boxShadow': '0 2px 5px rgba(0,0,0,0.1)',
                                    'marginBottom': '10px',
                                    'height': '100%'
                                })
                            ], style={'width': '19%', 'display': 'inline-block', 'padding': '0 5px'}) 
                              for team, row in zip(top_teams, [df_goals[df_goals['team'] == team].iloc[0] for team in top_teams])]
                        ], style={'display': 'flex', 'justifyContent': 'space-between'})
                    ])
                ], style={
                    'backgroundColor': '#ecf0f1', 
                    'padding': '20px', 
                    'borderRadius': '10px', 
                    'marginTop': '25px'
                })
            ])

        
        elif active_tab == "team-tab":
            # Comprehensive team performance metrics
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
                match_results = []
                match_dates = []
                opponents = []
                
                for _, match in team_matches.iterrows():
                    match_date = match['match_date']
                    match_dates.append(match_date)
                    
                    if match['home_team'] == team:
                        opponent = match['away_team']
                        goals_for += match['home_score']
                        goals_against += match['away_score']
                        score = f"{match['home_score']}-{match['away_score']}"
                        
                        if match['home_score'] > match['away_score']:
                            wins += 1
                            result = 'W'
                        elif match['home_score'] == match['away_score']:
                            draws += 1
                            result = 'D'
                        else:
                            losses += 1
                            result = 'L'
                    else:
                        opponent = match['home_team']
                        goals_for += match['away_score']
                        goals_against += match['home_score']
                        score = f"{match['away_score']}-{match['home_score']}"
                        
                        if match['away_score'] > match['home_score']:
                            wins += 1
                            result = 'W'
                        elif match['away_score'] == match['home_score']:
                            draws += 1
                            result = 'D'
                        else:
                            losses += 1
                            result = 'L'
                    
                    opponents.append(opponent)
                    match_results.append({
                        'date': match_date,
                        'opponent': opponent,
                        'result': result,
                        'score': score
                    })
                
                # Sort matches by date
                match_results = sorted(match_results, key=lambda x: x['date'])
                
                # Calculate progression through tournament
                matches_played = wins + draws + losses
                points = wins * 3 + draws
                goal_difference = goals_for - goals_against
                avg_goals_scored = goals_for / matches_played if matches_played > 0 else 0
                avg_goals_conceded = goals_against / matches_played if matches_played > 0 else 0
                win_percentage = (wins / matches_played * 100) if matches_played > 0 else 0
                
                team_stats.append({
                    'Team': team,
                    'Matches': matches_played,
                    'Wins': wins,
                    'Draws': draws,
                    'Losses': losses,
                    'Goals_For': goals_for,
                    'Goals_Against': goals_against,
                    'Goal_Difference': goal_difference,
                    'Points': points,
                    'Win_Percentage': win_percentage,
                    'Match_Results': match_results,
                    'Avg_Goals_Scored': avg_goals_scored,
                    'Avg_Goals_Conceded': avg_goals_conceded
                })
            
            # Convert to DataFrame and sort
            df_stats = pd.DataFrame(team_stats).sort_values('Points', ascending=False)
            
            # Create team standings visualization
            standings_data = df_stats[['Team', 'Matches', 'Wins', 'Draws', 'Losses', 
                                     'Goals_For', 'Goals_Against', 'Goal_Difference', 'Points']]
            
            # Generate a color gradient based on points
            max_points = standings_data['Points'].max()
            colorscale = [
                [0, 'rgba(247, 247, 247, 0.8)'],  # Light gray for bottom teams
                [0.6, 'rgba(252, 243, 207, 0.8)'],  # Light gold for middle teams
                [1, 'rgba(241, 196, 15, 0.8)']   # Gold for top teams
            ]
            
            # Create standings table with colored cells
            standings_fig = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Rank</b>', '<b>Team</b>', '<b>MP</b>', '<b>W</b>', '<b>D</b>', '<b>L</b>', 
                            '<b>GF</b>', '<b>GA</b>', '<b>GD</b>', '<b>Pts</b>'],
                    fill_color='#2c3e50',
                    align='center',
                    font=dict(color='white', size=14)
                ),
                cells=dict(
                    values=[
                        list(range(1, len(standings_data) + 1)),  # Rank column
                        standings_data['Team'],
                        standings_data['Matches'],
                        standings_data['Wins'],
                        standings_data['Draws'],
                        standings_data['Losses'],
                        standings_data['Goals_For'],
                        standings_data['Goals_Against'],
                        standings_data['Goal_Difference'],
                        standings_data['Points']
                    ],
                    fill_color=[
                        ['rgba(247, 247, 247, 0.8)'] * len(standings_data),  # Rank column
                        ['rgba(247, 247, 247, 0.8)'] * len(standings_data),  # Team column
                        ['rgba(247, 247, 247, 0.8)'] * len(standings_data),  # MP column
                        ['rgba(52, 152, 219, 0.8)'] * len(standings_data),  # W column (blue)
                        ['rgba(241, 196, 15, 0.8)'] * len(standings_data),  # D column (yellow)
                        ['rgba(231, 76, 60, 0.8)'] * len(standings_data),   # L column (red)
                        ['rgba(46, 204, 113, 0.8)'] * len(standings_data),  # GF column (green)
                        ['rgba(155, 89, 182, 0.8)'] * len(standings_data),  # GA column (purple)
                        [
                            'rgba(46, 204, 113, 0.8)' if gd > 0 else 
                            'rgba(231, 76, 60, 0.8)' if gd < 0 else 
                            'rgba(149, 165, 166, 0.8)' 
                            for gd in standings_data['Goal_Difference']
                        ],  # GD column (colored by value)
                        [
                            f'rgba(241, 196, 15, {0.4 + 0.6 * (pts / max_points)})'
                            for pts in standings_data['Points']
                        ]  # Points column (gradient by value)
                    ],
                    align='center',
                    font=dict(color='black', size=13),
                    height=28
                )
            )])
            
            standings_fig.update_layout(
                title={
                    'text': "🏆 Tournament Standings",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#2c3e50'}
                },
                height=500,
                margin=dict(l=0, r=0, t=50, b=0),
            )
            
            # Create win/draw/loss visualization for top teams - sort by win percentage
            # First calculate win percentages for sorting
            df_stats['win_percentage'] = df_stats.apply(lambda row: row['Wins'] / row['Matches'] * 100 if row['Matches'] > 0 else 0, axis=1)
            # Sort by win percentage first, then by total points as a tiebreaker
            top_teams_df = df_stats.sort_values(['win_percentage', 'Points'], ascending=[False, False]).head(8)
            top_teams = top_teams_df['Team'].tolist()
            
            # Calculate win/draw/loss percentages
            win_percentages = []
            draw_percentages = []
            loss_percentages = []
            teams = []
            
            # Ensure we use the right teams order directly from top_teams list
            for team in top_teams:
                row = top_teams_df[top_teams_df['Team'] == team].iloc[0]
                total = row['Matches']
                if total > 0:
                    win_percentages.append(row['Wins'] / total * 100)
                    draw_percentages.append(row['Draws'] / total * 100)
                    loss_percentages.append(row['Losses'] / total * 100)
                    teams.append(team)
            
            # Create stacked bar chart for results
            results_fig = go.Figure()
            
            # Add win bars
            results_fig.add_trace(go.Bar(
                y=teams,
                x=win_percentages,
                name='Wins',
                orientation='h',
                marker=dict(color='rgba(46, 204, 113, 0.8)'),
                hovertemplate='<b>%{y}</b><br>Wins: %{customdata[0]} (%{x:.1f}%)<extra></extra>',
                customdata=[[int(top_teams_df[top_teams_df['Team'] == team]['Wins'].values[0])] for team in teams]
            ))
            
            # Add draw bars
            results_fig.add_trace(go.Bar(
                y=teams,
                x=draw_percentages,
                name='Draws',
                orientation='h',
                marker=dict(color='rgba(241, 196, 15, 0.8)'),
                hovertemplate='<b>%{y}</b><br>Draws: %{customdata[0]} (%{x:.1f}%)<extra></extra>',
                customdata=[[int(top_teams_df[top_teams_df['Team'] == team]['Draws'].values[0])] for team in teams]
            ))
            
            # Add loss bars
            results_fig.add_trace(go.Bar(
                y=teams,
                x=loss_percentages,
                name='Losses',
                orientation='h',
                marker=dict(color='rgba(231, 76, 60, 0.8)'),
                hovertemplate='<b>%{y}</b><br>Losses: %{customdata[0]} (%{x:.1f}%)<extra></extra>',
                customdata=[[int(top_teams_df[top_teams_df['Team'] == team]['Losses'].values[0])] for team in teams]
            ))
            
            # Update layout
            results_fig.update_layout(
                title={
                    'text': "Match Results - Top 8 Teams",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50'}
                },
                xaxis_title="Percentage of Matches",
                yaxis_title=None,
                barmode='stack',
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50'},
                margin=dict(l=100, r=20, t=50, b=30),
                hovermode='closest',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                xaxis=dict(range=[0, 100]),
                yaxis=dict(autorange="reversed")
            )
            
            return html.Div([
                # Description section
                html.Div([
                    html.Div([
                        html.H5("🏆 Team Performance", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                        html.Span(" ℹ️", style={
                            'marginLeft': '10px', 
                            'cursor': 'pointer', 
                            'fontSize': '16px',
                            'color': '#3498db'
                        }, title="Tournament standings and team performance metrics")
                    ]),
                    html.Div([
                        html.P("This dual visualization presents a comprehensive analysis of team performance. The standings table employs color-coding to instantly communicate key metrics - wins (blue), draws (yellow), losses (red), goals scored (green), and goal difference (green/red). Below, the stacked horizontal bar chart for the top 8 teams transforms win/draw/loss statistics into proportional segments, revealing performance patterns that may not be apparent from the standings table alone.", 
                               style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '10px'}),
                        html.Details([
                            html.Summary("📖 Visualization Design Rationale", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                            html.Div([
                                html.P(["• ", html.Strong("Table vs. Chart Approach:"), " We've paired a traditional standings table with a proportional bar chart to balance familiarity with visual insight. While tables provide precise values, the stacked bars reveal patterns of consistency and performance distribution at a glance."], style={'margin': '12px 0', 'fontSize': '13px'}),
                                html.P(["• ", html.Strong("Color Semantics:"), " The color scheme maintains conventional associations (green for wins, yellow for draws, red for losses) to facilitate intuitive understanding while providing sufficient contrast for accessibility."], style={'margin': '12px 0', 'fontSize': '13px'}),
                                html.P(["• ", html.Strong("Interactive Elements:"), " Hover tooltips on the stacked bars reveal exact match counts and percentages, preserving precision while maintaining a clean visual presentation."], style={'margin': '12px 0', 'fontSize': '13px'}),
                                html.P(["• ", html.Strong("Alternatives Considered:"), " While radar charts could show multiple metrics simultaneously and heat maps might emphasize extremes, the stacked bar approach best communicates the proportional relationship between wins, draws, and losses - the fundamental metrics of team performance."], style={'margin': '12px 0', 'fontSize': '13px'}),
                                html.P(["• ", html.Strong("Key Metrics Explained:"), " ", html.Strong("MP"), " (Matches Played), ", html.Strong("W/D/L"), " (Wins/Draws/Losses), ", html.Strong("GF/GA"), " (Goals For/Against), ", html.Strong("GD"), " (Goal Difference), ", html.Strong("Pts"), " (Points: 3 for win, 1 for draw)"], style={'margin': '12px 0', 'fontSize': '13px'})
                            ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                        ], style={'marginTop': '10px'})
                    ])
                ], style={
                    'backgroundColor': '#f8f9fa', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '20px'
                }),
                
                # Tournament standings table
                dcc.Graph(figure=standings_fig, style={'height': '500px', 'marginBottom': '25px'}),
                
                # Results breakdown visualization
                dcc.Graph(figure=results_fig, style={'height': '400px'})
            ])

        
        elif active_tab == "stats-tab":
            # Enhanced match statistics analysis
            matches['total_goals'] = matches['home_score'] + matches['away_score']
            matches['goals_diff'] = abs(matches['home_score'] - matches['away_score'])
            matches['home_win'] = matches['home_score'] > matches['away_score']
            matches['away_win'] = matches['home_score'] < matches['away_score']
            matches['draw'] = matches['home_score'] == matches['away_score']
            
            # Calculate aggregate statistics
            total_matches = len(matches)
            total_goals = matches['total_goals'].sum()
            avg_goals = total_goals / total_matches
            home_wins = matches['home_win'].sum()
            away_wins = matches['away_win'].sum()
            draws = matches['draw'].sum()
            home_win_pct = home_wins / total_matches * 100
            away_win_pct = away_wins / total_matches * 100
            draw_pct = draws / total_matches * 100
            matches_with_goals = len(matches[matches['total_goals'] > 0])
            clean_sheets = len(matches[matches['home_score'] == 0]) + len(matches[matches['away_score'] == 0])
            
            # Create goals per match histogram
            goals_fig = go.Figure()
            
            # Add histogram with custom styling
            goals_fig.add_trace(go.Histogram(
                x=matches['total_goals'],
                marker=dict(
                    color='rgba(52, 152, 219, 0.7)',
                    line=dict(color='rgba(52, 152, 219, 1)', width=1)
                ),
                hovertemplate='<b>%{x} goals</b>: %{y} matches<extra></extra>'
            ))
            
            # Add mean line
            goals_fig.add_vline(
                x=avg_goals,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Avg: {avg_goals:.2f}",
                annotation_position="top right"
            )
            
            # Update layout
            goals_fig.update_layout(
                title={
                    'text': "📈 Goals per Match Distribution",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50'}
                },
                xaxis_title="Total Goals per Match",
                yaxis_title="Number of Matches",
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50'},
                margin=dict(l=60, r=50, t=80, b=50),
                hovermode='closest',
                bargap=0.1
            )
            
            # Create goal difference histogram
            diff_fig = go.Figure()
            
            # Add histogram with custom styling
            diff_fig.add_trace(go.Histogram(
                x=matches['goals_diff'],
                marker=dict(
                    color='rgba(155, 89, 182, 0.7)',
                    line=dict(color='rgba(155, 89, 182, 1)', width=1)
                ),
                hovertemplate='<b>%{x} goal difference</b>: %{y} matches<extra></extra>'
            ))
            
            # Update layout
            diff_fig.update_layout(
                title={
                    'text': "Goal Difference Distribution",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50'}
                },
                xaxis_title="Goal Difference (absolute)",
                yaxis_title="Number of Matches",
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50'},
                margin=dict(l=60, r=50, t=80, b=50),
                hovermode='closest',
                bargap=0.1
            )
            
            # Create pie chart for match outcomes
            outcomes_fig = go.Figure()
            
            # Add pie chart
            outcomes_fig.add_trace(go.Pie(
                labels=['Home Wins', 'Away Wins', 'Draws'],
                values=[home_wins, away_wins, draws],
                marker=dict(
                    colors=['rgba(46, 204, 113, 0.7)', 'rgba(52, 152, 219, 0.7)', 'rgba(241, 196, 15, 0.7)'],
                    line=dict(color='white', width=2)
                ),
                textinfo='percent+label',
                insidetextfont=dict(color='white'),
                hovertemplate='<b>%{label}</b><br>Count: %{value} (%{percent})<extra></extra>'
            ))
            
            # Update layout
            outcomes_fig.update_layout(
                title={
                    'text': "Match Outcomes",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50'}
                },
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50'},
                margin=dict(l=20, r=20, t=80, b=20),
                hovermode='closest',
                showlegend=False
            )
            
            return html.Div([
                # Description section
                html.Div([
                    html.Div([
                        html.H5("📈 Match Insights", style={'color': '#2c3e50', 'marginBottom': '10px', 'display': 'inline-block'}),
                        html.Span(" ℹ️", style={
                            'marginLeft': '10px', 
                            'cursor': 'pointer', 
                            'fontSize': '16px',
                            'color': '#3498db'
                        }, title="Statistical analysis of match patterns across the tournament")
                    ]),
                    html.Div([
                        html.P("This multi-visualization dashboard illuminates the statistical patterns underlying the tournament's matches. The histograms reveal the distribution of goals per match and goal differences, while the pie chart breaks down match outcomes into wins (home/away) and draws. Together, these visualizations expose the tournament's competitive balance, scoring trends, and home advantage effects that aren't apparent from examining individual match results.", 
                               style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '10px'}),
                        html.Details([
                            html.Summary("📖 Data Visualization Strategy", style={'fontWeight': 'bold', 'color': '#34495e', 'cursor': 'pointer'}),
                            html.Div([
                                html.P(["• ", html.Strong("Histogram Benefits:"), " Histograms reveal the complete distribution of goals and margins of victory, showing not just averages but the full range and frequency of different outcomes. This exposes whether the tournament featured predominantly close matches or had significant outliers."], style={'margin': '12px 0', 'fontSize': '13px'}),
                                html.P(["• ", html.Strong("Pie Chart Rationale:"), " While pie charts are sometimes criticized for making precise comparisons difficult, in this context they provide an immediate visual impression of the balance between home wins, away wins, and draws - a fundamental tournament characteristic."], style={'margin': '12px 0', 'fontSize': '13px'}),
                                html.P(["• ", html.Strong("Key Findings:"), " Home teams won {:.1f}% of matches, {:.1f}% ended in draws, and matches averaged {:.2f} goals with {} clean sheets ({:.1f}% of team appearances).".format(home_win_pct, draw_pct, avg_goals, clean_sheets, clean_sheets / (total_matches * 2) * 100)], style={'margin': '12px 0', 'fontSize': '13px'}),
                                html.P(["• ", html.Strong("Alternative Approaches:"), " Line graphs tracking goals over time could show tournament progression but would miss the distributional insights. Box plots could highlight outliers but are less intuitive for general audiences than histograms."], style={'margin': '12px 0', 'fontSize': '13px'}),
                                html.P(["• ", html.Strong("Complementary Information:"), " The summary cards above provide immediate access to key tournament statistics, while the visualizations below offer deeper insight into the patterns those numbers represent."], style={'margin': '12px 0', 'fontSize': '13px'})
                            ], style={'paddingLeft': '15px', 'marginTop': '8px'})
                        ], style={'marginTop': '10px'})
                    ])
                ], style={
                    'backgroundColor': '#f8f9fa', 
                    'padding': '15px', 
                    'borderRadius': '10px', 
                    'marginBottom': '20px'
                }),
                
                # Key tournament statistics cards
                html.Div([
                    html.Div([
                        html.H5("Tournament Summary", style={'color': '#2c3e50', 'marginBottom': '15px', 'textAlign': 'center'}),
                        html.Div([
                            html.Div([
                                html.H3(f"{total_matches}", style={'fontSize': '28px', 'color': '#3498db', 'margin': '0', 'fontWeight': 'bold'}),
                                html.P("Total Matches", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                            ], style={'width': '25%', 'display': 'inline-block', 'textAlign': 'center'}),
                            html.Div([
                                html.H3(f"{total_goals}", style={'fontSize': '28px', 'color': '#2ecc71', 'margin': '0', 'fontWeight': 'bold'}),
                                html.P("Total Goals", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                            ], style={'width': '25%', 'display': 'inline-block', 'textAlign': 'center'}),
                            html.Div([
                                html.H3(f"{avg_goals:.2f}", style={'fontSize': '28px', 'color': '#f39c12', 'margin': '0', 'fontWeight': 'bold'}),
                                html.P("Goals per Match", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                            ], style={'width': '25%', 'display': 'inline-block', 'textAlign': 'center'}),
                            html.Div([
                                html.H3(f"{clean_sheets}", style={'fontSize': '28px', 'color': '#9b59b6', 'margin': '0', 'fontWeight': 'bold'}),
                                html.P("Clean Sheets", style={'fontSize': '12px', 'color': '#7f8c8d', 'margin': '0'})
                            ], style={'width': '25%', 'display': 'inline-block', 'textAlign': 'center'})
                        ])
                    ], style={'backgroundColor': '#ecf0f1', 'padding': '15px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                    
                    # Visualizations in a grid
                    html.Div([
                        html.Div([
                            dcc.Graph(figure=goals_fig, style={'height': '350px'})
                        ], style={'width': '50%', 'display': 'inline-block', 'paddingRight': '10px'}),
                        
                        html.Div([
                            dcc.Graph(figure=diff_fig, style={'height': '350px'})
                        ], style={'width': '50%', 'display': 'inline-block', 'paddingLeft': '10px'})
                    ], style={'marginBottom': '20px'}),
                    
                    html.Div([
                        html.Div([
                            dcc.Graph(figure=outcomes_fig, style={'height': '350px'})
                        ], style={'width': '100%', 'display': 'inline-block'})
                    ])
                ])
            ])

            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return html.P(f"Error creating overview: {str(e)}", 
                     style={'color': '#e74c3c', 'textAlign': 'center'})
