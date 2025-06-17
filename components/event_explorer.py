import matplotlib
matplotlib.use('Agg')
import dash
from dash import dcc, html, Input, Output, callback, dash_table
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.data_loader import load_euro_2024_matches, load_match_data, get_all_teams

def layout():
    return html.Div([
        # Header
        html.Div([
            html.H2("🔍 Event Data Explorer", className="text-center mb-4"),
            html.P("Explore and filter raw event data from Euro 2024 matches", 
                   className="text-center text-muted")
        ], className="mb-4"),
        
        # Filters
        html.Div([
            html.H4("🎛️ Filters", className="mb-3"),
            html.Div([
                html.Div([
                    html.Label("Select Team:", className="fw-bold"),
                    dcc.Dropdown(
                        id='explorer-team-dropdown',
                        options=[],
                        placeholder="Select a team...",
                        className="mb-2"
                    )
                ], className="col-md-3"),
                html.Div([
                    html.Label("Select Match:", className="fw-bold"),
                    dcc.Dropdown(
                        id='explorer-match-dropdown',
                        placeholder="Select a match...",
                        className="mb-2"
                    )
                ], className="col-md-3"),
                html.Div([
                    html.Label("Event Type:", className="fw-bold"),
                    dcc.Dropdown(
                        id='event-type-dropdown',
                        options=[
                            {'label': 'All Events', 'value': 'all'},
                            {'label': 'Pass', 'value': 'Pass'},
                            {'label': 'Shot', 'value': 'Shot'},
                            {'label': 'Dribble', 'value': 'Dribble'},
                            {'label': 'Tackle', 'value': 'Tackle'},
                            {'label': 'Interception', 'value': 'Interception'},
                            {'label': 'Carry', 'value': 'Carry'},
                            {'label': 'Foul Committed', 'value': 'Foul Committed'},
                            {'label': 'Card', 'value': 'Card'}
                        ],
                        value='all',
                        className="mb-2"
                    )
                ], className="col-md-3"),
                html.Div([
                    html.Label("Player:", className="fw-bold"),
                    dcc.Dropdown(
                        id='explorer-player-dropdown',
                        placeholder="Select a player...",
                        className="mb-2"
                    )
                ], className="col-md-3"),
            ], className="row"),
            
            html.Div([
                html.Div([
                    html.Label("Time Range (minutes):", className="fw-bold"),
                    dcc.RangeSlider(
                        id='time-range-slider',
                        min=0,
                        max=120,
                        step=1,
                        value=[0, 90],
                        marks={i: str(i) for i in range(0, 121, 15)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], className="col-md-12 mt-3"),
            ], className="row")
        ], className="card p-3 mb-4"),
        
        # Summary statistics
        html.Div(id='event-summary-stats', className="mb-4"),
        
        # Event timeline
        html.Div([
            html.H4("📈 Event Timeline", className="mb-3"),
            dcc.Graph(id='event-timeline')
        ], className="card p-3 mb-4"),
        
        # Data table
        html.Div([
            html.H4("📋 Event Data Table", className="mb-3"),
            html.Div([
                html.Button("Export to CSV", id="export-btn", className="btn btn-primary mb-3"),
                dcc.Download(id="download-dataframe-csv"),
            ]),
            dash_table.DataTable(
                id='events-table',
                columns=[],
                data=[],
                page_size=20,
                sort_action="native",
                filter_action="native",
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                style_data={'backgroundColor': 'rgb(248, 248, 248)'},
                export_format="csv"
            )
        ], className="card p-3"),
        
    ], className="container-fluid p-4")

@callback(
    Output('explorer-team-dropdown', 'options'),
    Input('explorer-team-dropdown', 'id')
)
def update_explorer_team_options(_):
    teams = get_all_teams()
    return [{'label': team, 'value': team} for team in teams]

@callback(
    Output('explorer-match-dropdown', 'options'),
    Output('explorer-match-dropdown', 'value'),
    Input('explorer-team-dropdown', 'value')
)
def update_explorer_match_options(selected_team):
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
    Output('explorer-player-dropdown', 'options'),
    Input('explorer-match-dropdown', 'value')
)
def update_explorer_player_options(match_id):
    if not match_id:
        return []
    
    try:
        events_df = load_match_data(match_id)
        players = events_df['player'].apply(
            lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
        ).unique()
        players = [p for p in players if p != 'Unknown' and pd.notna(p)]
        players.sort()
        
        options = [{'label': 'All Players', 'value': 'all'}]
        options.extend([{'label': player, 'value': player} for player in players])
        return options
        
    except Exception as e:
        print(f"Error loading players: {e}")
        return []

@callback(
    Output('event-summary-stats', 'children'),
    Input('explorer-match-dropdown', 'value'),
    Input('event-type-dropdown', 'value'),
    Input('explorer-player-dropdown', 'value'),
    Input('time-range-slider', 'value')
)
def update_event_summary(match_id, event_type, player, time_range):
    if not match_id:
        return html.P("Please select a match to view event statistics.")
    
    try:
        events_df = load_match_data(match_id)
        
        # Apply filters
        filtered_df = events_df.copy()
        
        # Filter by event type
        if event_type != 'all':
            filtered_df = filtered_df[filtered_df['type'] == event_type]
        
        # Filter by player
        if player and player != 'all':
            filtered_df = filtered_df[
                filtered_df['player'].apply(
                    lambda x: x.get('name', '') == player if isinstance(x, dict) else str(x) == player
                )
            ]
        
        # Filter by time range
        if time_range:
            filtered_df = filtered_df[
                (filtered_df['minute'] >= time_range[0]) & 
                (filtered_df['minute'] <= time_range[1])
            ]
        
        # Calculate statistics
        total_events = len(filtered_df)
        unique_players = len(filtered_df['player'].apply(
            lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
        ).unique())
        
        event_types = filtered_df['type'].value_counts().head(5)
        
        return html.Div([
            html.H4("📊 Event Summary", className="text-center text-primary"),
            html.Div([
                html.Div([
                    html.H3(f"{total_events}", className="text-success text-center"),
                    html.P("Total Events", className="text-center text-muted")
                ], className="col-md-3"),
                html.Div([
                    html.H3(f"{unique_players}", className="text-info text-center"),
                    html.P("Players Involved", className="text-center text-muted")
                ], className="col-md-3"),
                html.Div([
                    html.H3(f"{event_types.iloc[0] if not event_types.empty else 0}", className="text-warning text-center"),
                    html.P(f"Most Common: {event_types.index[0] if not event_types.empty else 'N/A'}", 
                           className="text-center text-muted")
                ], className="col-md-3"),
                html.Div([
                    html.H3(f"{time_range[1] - time_range[0]}min", className="text-primary text-center"),
                    html.P("Time Window", className="text-center text-muted")
                ], className="col-md-3"),
            ], className="row")
        ], className="card p-3")
        
    except Exception as e:
        return html.Div([
            html.P(f"Error loading event summary: {str(e)}", className="text-danger")
        ])

@callback(
    Output('event-timeline', 'figure'),
    Input('explorer-match-dropdown', 'value'),
    Input('event-type-dropdown', 'value'),
    Input('explorer-player-dropdown', 'value'),
    Input('time-range-slider', 'value')
)
def update_event_timeline(match_id, event_type, player, time_range):
    if not match_id:
        return go.Figure().add_annotation(text="Select a match to view timeline", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    try:
        events_df = load_match_data(match_id)
        
        # Apply filters
        filtered_df = events_df.copy()
        
        if event_type != 'all':
            filtered_df = filtered_df[filtered_df['type'] == event_type]
        
        if player and player != 'all':
            filtered_df = filtered_df[
                filtered_df['player'].apply(
                    lambda x: x.get('name', '') == player if isinstance(x, dict) else str(x) == player
                )
            ]
        
        if time_range:
            filtered_df = filtered_df[
                (filtered_df['minute'] >= time_range[0]) & 
                (filtered_df['minute'] <= time_range[1])
            ]
        
        # Create timeline
        if filtered_df.empty:
            return go.Figure().add_annotation(text="No events match the current filters", 
                                            xref="paper", yref="paper", x=0.5, y=0.5)
        
        # Group events by minute and type
        timeline_data = filtered_df.groupby(['minute', 'type']).size().reset_index(name='count')
        
        fig = px.line(timeline_data, x='minute', y='count', color='type',
                      title='Event Frequency Over Time',
                      labels={'minute': 'Match Minute', 'count': 'Number of Events'})
        
        fig.update_layout(height=400, hovermode='x unified')
        
        return fig
        
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error creating timeline: {str(e)}", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)

@callback(
    Output('events-table', 'data'),
    Output('events-table', 'columns'),
    Input('explorer-match-dropdown', 'value'),
    Input('event-type-dropdown', 'value'),
    Input('explorer-player-dropdown', 'value'),
    Input('time-range-slider', 'value')
)
def update_events_table(match_id, event_type, player, time_range):
    if not match_id:
        return [], []
    
    try:
        events_df = load_match_data(match_id)
        
        # Apply filters
        filtered_df = events_df.copy()
        
        if event_type != 'all':
            filtered_df = filtered_df[filtered_df['type'] == event_type]
        
        if player and player != 'all':
            filtered_df = filtered_df[
                filtered_df['player'].apply(
                    lambda x: x.get('name', '') == player if isinstance(x, dict) else str(x) == player
                )
            ]
        
        if time_range:
            filtered_df = filtered_df[
                (filtered_df['minute'] >= time_range[0]) & 
                (filtered_df['minute'] <= time_range[1])
            ]
        
        # Select relevant columns for display
        display_columns = ['minute', 'second', 'type', 'team', 'player', 'position', 'location']
        
        # Flatten complex columns
        display_df = filtered_df[display_columns].copy()
        
        # Process nested data
        display_df['team'] = display_df['team'].apply(
            lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
        )
        display_df['player'] = display_df['player'].apply(
            lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
        )
        display_df['position'] = display_df['position'].apply(
            lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else str(x)
        )
        display_df['location'] = display_df['location'].apply(
            lambda x: f"({x[0]:.1f}, {x[1]:.1f})" if isinstance(x, list) and len(x) >= 2 else 'N/A'
        )
        
        # Create columns for DataTable
        columns = [{"name": col.title(), "id": col} for col in display_df.columns]
        
        return display_df.head(1000).to_dict('records'), columns
        
    except Exception as e:
        print(f"Error updating table: {e}")
        return [], []

@callback(
    Output("download-dataframe-csv", "data"),
    Input("export-btn", "n_clicks"),
    Input('explorer-match-dropdown', 'value'),
    Input('event-type-dropdown', 'value'),
    Input('explorer-player-dropdown', 'value'),
    Input('time-range-slider', 'value'),
    prevent_initial_call=True,
)
def export_data(n_clicks, match_id, event_type, player, time_range):
    if not n_clicks or not match_id:
        return dash.no_update
    
    try:
        events_df = load_match_data(match_id)
        
        # Apply same filters as table
        filtered_df = events_df.copy()
        
        if event_type != 'all':
            filtered_df = filtered_df[filtered_df['type'] == event_type]
        
        if player and player != 'all':
            filtered_df = filtered_df[
                filtered_df['player'].apply(
                    lambda x: x.get('name', '') == player if isinstance(x, dict) else str(x) == player
                )
            ]
        
        if time_range:
            filtered_df = filtered_df[
                (filtered_df['minute'] >= time_range[0]) & 
                (filtered_df['minute'] <= time_range[1])
            ]
        
        return dcc.send_data_frame(filtered_df.to_csv, "euro2024_events.csv")
        
    except Exception as e:
        return dash.no_update
