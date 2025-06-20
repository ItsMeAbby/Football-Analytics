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
            html.H2("🔍 Event Data Explorer", 
                   style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50'}),
            html.P("Explore and filter raw event data from Euro 2024 matches. Use the filters below to analyze specific events, players, and time periods.", 
                   style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'lineHeight': '1.5'})
        ], style={
            'backgroundColor': 'white', 
            'padding': '25px', 
            'borderRadius': '15px',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
            'marginBottom': '25px'
        }),
        
        # Filters
        html.Div([
            html.H4("🎛️ Filter Options", style={'marginBottom': '20px', 'color': '#2c3e50'}),
            
            # Description of filters
            html.Div([
                html.P("Select filters to narrow down the event data. You can filter by team, match, event type, player, and time range to focus on specific aspects of the game.",
                      style={'color': '#7f8c8d', 'marginBottom': '20px', 'fontSize': '14px'})
            ]),
            
            html.Div([
                html.Div([
                    html.Label("Select Team:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='explorer-team-dropdown',
                        options=[],
                        placeholder="Select a team...",
                        style={'marginBottom': '15px', 'borderRadius': '8px'}
                    )
                ], style={'width': '24%', 'display': 'inline-block', 'paddingRight': '10px'}),
                
                html.Div([
                    html.Label("Select Match:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='explorer-match-dropdown',
                        placeholder="Select a match...",
                        style={'marginBottom': '15px', 'borderRadius': '8px'}
                    )
                ], style={'width': '24%', 'display': 'inline-block', 'paddingRight': '10px'}),
                
                html.Div([
                    html.Label("Event Type:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='event-type-dropdown',
                        options=[
                            {'label': 'All Events', 'value': 'all'},
                            {'label': '⚽ Pass', 'value': 'Pass'},
                            {'label': '🎯 Shot', 'value': 'Shot'},
                            {'label': '🏃 Dribble', 'value': 'Dribble'},
                            {'label': '⚔️ Duel', 'value': 'Duel'},
                            {'label': '🛑 Interception', 'value': 'Interception'},
                            {'label': '🏃‍♂️ Carry', 'value': 'Carry'},
                            {'label': '⚠️ Foul Committed', 'value': 'Foul Committed'},
                            {'label': '🟨 Card', 'value': 'Card'}
                        ],
                        value='all',
                        style={'marginBottom': '15px', 'borderRadius': '8px'}
                    )
                ], style={'width': '24%', 'display': 'inline-block', 'paddingRight': '10px'}),
                
                html.Div([
                    html.Label("Player:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='explorer-player-dropdown',
                        placeholder="Select a player...",
                        style={'marginBottom': '15px', 'borderRadius': '8px'}
                    )
                ], style={'width': '24%', 'display': 'inline-block'}),
            ]),
            
            html.Div([
                html.Div([
                    html.Label("Time Range (minutes):", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                    dcc.RangeSlider(
                        id='time-range-slider',
                        min=0,
                        max=120,
                        step=1,
                        value=[0, 90],
                        marks={i: {'label': str(i), 'style': {'transform': 'rotate(0deg)'}} for i in range(0, 121, 15)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False
                    )
                ], style={'width': '100%', 'paddingTop': '10px'})
            ])
        ], style={
            'backgroundColor': 'white', 
            'padding': '20px', 
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        }),
        
        # Summary statistics
        html.Div(id='event-summary-stats'),
        
        # Visualizations section with tabs
        html.Div([
            html.H4("📊 Event Visualizations", style={'marginBottom': '20px', 'color': '#2c3e50'}),
            
            # Description
            html.Div([
                html.P("These visualizations help you understand event patterns and distribution throughout the match. Explore frequency, location, and team-specific event data.",
                      style={'color': '#7f8c8d', 'marginBottom': '20px', 'fontSize': '14px'})
            ]),
            
            # Tabs for different visualizations
            dcc.Tabs([
                dcc.Tab(label="📈 Event Timeline", style={'padding': '12px', 'fontWeight': 'bold'}, children=[
                    html.Div([
                        html.P("This timeline shows the frequency of events across the match duration. Peaks indicate periods of high activity.", 
                               style={'color': '#7f8c8d', 'margin': '15px 0', 'fontSize': '14px'}),
                        dcc.Graph(id='event-timeline')
                    ], style={'padding': '15px'})
                ]),
                
                dcc.Tab(label="🗺️ Event Heatmap", style={'padding': '12px', 'fontWeight': 'bold'}, children=[
                    html.Div([
                        html.P("The heatmap shows event concentration by pitch location. Darker areas indicate higher event frequency.",
                               style={'color': '#7f8c8d', 'margin': '15px 0', 'fontSize': '14px'}),
                        html.Div(id='event-heatmap')
                    ], style={'padding': '15px'})
                ]),
                
                dcc.Tab(label="📊 Event Distribution", style={'padding': '12px', 'fontWeight': 'bold'}, children=[
                    html.Div([
                        html.P("This chart shows the distribution of event types, breaking down events by category and team.",
                               style={'color': '#7f8c8d', 'margin': '15px 0', 'fontSize': '14px'}),
                        html.Div(id='event-distribution')
                    ], style={'padding': '15px'})
                ])
            ], style={'marginBottom': '20px'})
        ], style={
            'backgroundColor': 'white', 
            'padding': '20px', 
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        }),
        
        # Data table
        html.Div([
            html.H4("📋 Event Data Table", style={'marginBottom': '20px', 'color': '#2c3e50'}),
            
            # Description
            html.Div([
                html.P("Browse detailed event data in tabular format. Use the search and filter options to find specific events. You can export the filtered data to CSV for further analysis.",
                      style={'color': '#7f8c8d', 'marginBottom': '20px', 'fontSize': '14px'})
            ]),
            
            html.Div([
                html.Button("Export to CSV", id="export-btn", 
                           style={'backgroundColor': '#3498db', 
                                  'color': 'white', 
                                  'border': 'none',
                                  'padding': '10px 15px',
                                  'borderRadius': '5px',
                                  'marginBottom': '15px',
                                  'cursor': 'pointer',
                                  'fontWeight': 'bold'}),
                dcc.Download(id="download-dataframe-csv"),
            ]),
            
            dash_table.DataTable(
                id='events-table',
                columns=[],
                data=[],
                page_size=20,
                sort_action="native",
                filter_action="native",
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left', 
                    'padding': '10px',
                    'fontFamily': 'Arial, sans-serif',
                    'minWidth': '100px', 
                    'maxWidth': '300px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },
                style_header={
                    'backgroundColor': '#34495e', 
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'border': 'none'
                },
                style_data={
                    'backgroundColor': '#f8f9fa',
                    'border': 'none'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#ecf0f1',
                    }
                ],
                export_format="csv"
            )
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
    Output('explorer-team-dropdown', 'options'),
    Output('explorer-team-dropdown', 'value'),
    Input('explorer-team-dropdown', 'id')
)
def update_explorer_team_options(_):
    teams = get_all_teams()
    options = [{'label': team, 'value': team} for team in teams]
    default_team = 'Spain' if 'Spain' in teams else teams[0] if teams else None
    return options, default_team

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
            html.H4("📊 Event Summary", style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50'}),
            
            # Description
            html.Div([
                html.P("This summary provides key metrics about the filtered event data. View total events, player involvement, most common event type, and the selected time window.",
                      style={'color': '#7f8c8d', 'marginBottom': '20px', 'fontSize': '14px', 'textAlign': 'center'})
            ]),
            
            html.Div([
                html.Div([
                    html.H3(f"{total_events}", style={'fontSize': '28px', 'color': '#2ecc71', 'margin': '0', 'fontWeight': 'bold', 'textAlign': 'center'}),
                    html.P("Total Events", style={'fontSize': '14px', 'color': '#7f8c8d', 'margin': '10px 0 0 0', 'textAlign': 'center'})
                ], style={'width': '25%', 'display': 'inline-block'}),
                
                html.Div([
                    html.H3(f"{unique_players}", style={'fontSize': '28px', 'color': '#3498db', 'margin': '0', 'fontWeight': 'bold', 'textAlign': 'center'}),
                    html.P("Players Involved", style={'fontSize': '14px', 'color': '#7f8c8d', 'margin': '10px 0 0 0', 'textAlign': 'center'})
                ], style={'width': '25%', 'display': 'inline-block'}),
                
                html.Div([
                    html.H3(f"{event_types.iloc[0] if not event_types.empty else 0}", style={'fontSize': '28px', 'color': '#f39c12', 'margin': '0', 'fontWeight': 'bold', 'textAlign': 'center'}),
                    html.P(f"Most Common: {event_types.index[0] if not event_types.empty else 'N/A'}", 
                           style={'fontSize': '14px', 'color': '#7f8c8d', 'margin': '10px 0 0 0', 'textAlign': 'center'})
                ], style={'width': '25%', 'display': 'inline-block'}),
                
                html.Div([
                    html.H3(f"{time_range[1] - time_range[0]}min", style={'fontSize': '28px', 'color': '#9b59b6', 'margin': '0', 'fontWeight': 'bold', 'textAlign': 'center'}),
                    html.P("Time Window", style={'fontSize': '14px', 'color': '#7f8c8d', 'margin': '10px 0 0 0', 'textAlign': 'center'})
                ], style={'width': '25%', 'display': 'inline-block'}),
            ])
        ], style={
            'backgroundColor': 'white', 
            'padding': '20px', 
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        })
        
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
        
        # Improved timeline visualization
        fig = px.line(timeline_data, x='minute', y='count', color='type',
                      labels={'minute': 'Match Minute', 'count': 'Number of Events'},
                      line_shape='spline', render_mode='svg')
        
        # Mark halftime and fulltime with vertical lines
        fig.add_vline(x=45, line_dash="dash", line_color="#e74c3c", 
                      annotation_text="Half Time", annotation_position="top")
        fig.add_vline(x=90, line_dash="dash", line_color="#e74c3c", 
                      annotation_text="Full Time", annotation_position="top")
                      
        # Enhance the styling
        fig.update_layout(
            height=500,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': '#2c3e50', 'family': 'Arial, sans-serif'},
            margin=dict(l=40, r=40, t=40, b=40),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.1)',
                borderwidth=1
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(211,211,211,0.3)',
                tickmode='linear',
                tick0=0,
                dtick=15,
                title_font=dict(size=14)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(211,211,211,0.3)',
                title_font=dict(size=14)
            )
        )
        
        # Enhance line styling
        for trace in fig.data:
            trace.update(
                line=dict(width=3),
                mode='lines+markers',
                marker=dict(size=6)
            )
        
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

@callback(
    Output('event-heatmap', 'children'),
    Input('explorer-match-dropdown', 'value'),
    Input('event-type-dropdown', 'value'),
    Input('explorer-player-dropdown', 'value'),
    Input('time-range-slider', 'value')
)
def update_event_heatmap(match_id, event_type, player, time_range):
    if not match_id:
        return html.P("Please select a match to view the event heatmap.",
                     style={'textAlign': 'center', 'color': '#7f8c8d', 'padding': '20px'})
    
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
        
        # Check if we have location data
        if filtered_df.empty or 'location' not in filtered_df.columns:
            return html.P("No location data available for the selected filters.",
                         style={'textAlign': 'center', 'color': '#7f8c8d', 'padding': '20px'})
        
        # Extract x, y coordinates from location
        x_coords = []
        y_coords = []
        
        for loc in filtered_df['location']:
            if isinstance(loc, list) and len(loc) >= 2:
                x_coords.append(loc[0])
                y_coords.append(loc[1])
        
        if not x_coords:
            return html.P("No valid location data available for the selected filters.",
                         style={'textAlign': 'center', 'color': '#7f8c8d', 'padding': '20px'})
        
        # Create a soccer field as background
        field_length = 120
        field_width = 80
        
        fig = go.Figure()
        
        # Add field background
        fig.add_shape(
            type="rect",
            x0=0, y0=0, x1=field_length, y1=field_width,
            line=dict(color="#3498db", width=2),
            fillcolor="rgba(46, 204, 113, 0.3)",
        )
        
        # Add center line
        fig.add_shape(
            type="line",
            x0=field_length/2, y0=0, x1=field_length/2, y1=field_width,
            line=dict(color="#3498db", width=2),
        )
        
        # Add center circle
        fig.add_shape(
            type="circle",
            x0=field_length/2-10, y0=field_width/2-10, 
            x1=field_length/2+10, y1=field_width/2+10,
            line=dict(color="#3498db", width=2),
            fillcolor="rgba(46, 204, 113, 0.0)",
        )
        
        # Add penalty areas
        fig.add_shape(  # Left penalty area
            type="rect",
            x0=0, y0=field_width/2-20, x1=16, y1=field_width/2+20,
            line=dict(color="#3498db", width=2),
            fillcolor="rgba(46, 204, 113, 0.0)",
        )
        
        fig.add_shape(  # Right penalty area
            type="rect",
            x0=field_length, y0=field_width/2-20, x1=field_length-16, y1=field_width/2+20,
            line=dict(color="#3498db", width=2),
            fillcolor="rgba(46, 204, 113, 0.0)",
        )
        
        # Add goal areas
        fig.add_shape(  # Left goal area
            type="rect",
            x0=0, y0=field_width/2-9, x1=5.5, y1=field_width/2+9,
            line=dict(color="#3498db", width=2),
            fillcolor="rgba(46, 204, 113, 0.0)",
        )
        
        fig.add_shape(  # Right goal area
            type="rect",
            x0=field_length, y0=field_width/2-9, x1=field_length-5.5, y1=field_width/2+9,
            line=dict(color="#3498db", width=2),
            fillcolor="rgba(46, 204, 113, 0.0)",
        )
        
        # Add goals
        fig.add_shape(  # Left goal
            type="rect",
            x0=-2, y0=field_width/2-3.5, x1=0, y1=field_width/2+3.5,
            line=dict(color="#e74c3c", width=2),
            fillcolor="rgba(231, 76, 60, 0.3)",
        )
        
        fig.add_shape(  # Right goal
            type="rect",
            x0=field_length, y0=field_width/2-3.5, x1=field_length+2, y1=field_width/2+3.5,
            line=dict(color="#e74c3c", width=2),
            fillcolor="rgba(231, 76, 60, 0.3)",
        )
        
        # Create heatmap
        fig.add_trace(go.Histogram2dContour(
            x=x_coords,
            y=y_coords,
            colorscale='Viridis',
            reversescale=True,
            showscale=True,
            hoverinfo='none',
            contours=dict(
                coloring='heatmap',
                showlabels=True,
            ),
            colorbar=dict(
                title='Event Density',
                titleside='right',
                titlefont=dict(size=14)
            ),
            opacity=0.7
        ))
        
        # Add scatter points for individual events
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers',
            marker=dict(
                color='rgba(255, 255, 255, 0.5)',
                size=5,
                line=dict(color='rgba(0, 0, 0, 0.5)', width=1)
            ),
            hoverinfo='none',
            showlegend=False
        ))
        
        # Update layout
        fig.update_layout(
            title=f"{event_type if event_type != 'all' else 'All Events'} Heatmap",
            title_x=0.5,
            title_font=dict(size=18, color='#2c3e50'),
            width=1000,
            height=600,
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-5, field_length+5]
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                scaleanchor="x",
                scaleratio=1,
                range=[-5, field_width+5]
            ),
            margin=dict(l=20, r=20, t=50, b=20),
            autosize=True,
        )
        
        return dcc.Graph(figure=fig)
        
    except Exception as e:
        return html.P(f"Error creating heatmap: {str(e)}",
                     style={'textAlign': 'center', 'color': '#e74c3c', 'padding': '20px'})

@callback(
    Output('event-distribution', 'children'),
    Input('explorer-match-dropdown', 'value'),
    Input('time-range-slider', 'value')
)
def update_event_distribution(match_id, time_range):
    if not match_id:
        return html.P("Please select a match to view event distribution.",
                     style={'textAlign': 'center', 'color': '#7f8c8d', 'padding': '20px'})
    
    try:
        events_df = load_match_data(match_id)
        matches = load_euro_2024_matches()
        match_info = matches[matches['match_id'] == match_id].iloc[0]
        
        home_team = match_info['home_team']
        away_team = match_info['away_team']
        
        # Apply time range filter
        if time_range:
            filtered_df = events_df[
                (events_df['minute'] >= time_range[0]) & 
                (events_df['minute'] <= time_range[1])
            ]
        else:
            filtered_df = events_df
        
        # Get event types by team
        team_events = []
        
        for team_name in [home_team, away_team]:
            team_data = filtered_df[
                filtered_df['team'].apply(
                    lambda x: x.get('name', '') == team_name if isinstance(x, dict) else str(x) == team_name
                )
            ]
            
            event_counts = team_data['type'].value_counts().reset_index()
            event_counts.columns = ['Event_Type', 'Count']
            event_counts['Team'] = team_name
            
            # Only keep top events for cleaner visualization
            if len(event_counts) > 8:
                top_events = event_counts.head(7)
                other_count = event_counts.iloc[7:]['Count'].sum()
                other_row = pd.DataFrame({'Event_Type': ['Other Events'], 'Count': [other_count], 'Team': [team_name]})
                event_counts = pd.concat([top_events, other_row], ignore_index=True)
            
            team_events.append(event_counts)
        
        # Combine the data
        if team_events:
            combined_events = pd.concat(team_events, ignore_index=True)
            
            # Create stacked bar chart
            fig = px.bar(
                combined_events, 
                x='Event_Type', 
                y='Count', 
                color='Team',
                barmode='group',
                color_discrete_map={
                    home_team: '#2ecc71',  # Green for home team
                    away_team: '#3498db'   # Blue for away team
                },
                text='Count'
            )
            
            # Update layout
            fig.update_layout(
                title=f"Event Distribution: {home_team} vs {away_team}",
                title_x=0.5,
                title_font=dict(size=18, color='#2c3e50'),
                xaxis_title=None,
                yaxis_title="Number of Events",
                legend_title="Team",
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50', 'family': 'Arial, sans-serif'},
                margin=dict(l=40, r=40, t=80, b=40),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='rgba(0,0,0,0.1)',
                    borderwidth=1
                ),
                xaxis=dict(
                    categoryorder='total descending',  # Order by total count
                    tickangle=-45,
                    title_font=dict(size=14)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(211,211,211,0.3)',
                    title_font=dict(size=14)
                )
            )
            
            fig.update_traces(
                textposition='auto',
                textfont=dict(size=12),
            )
            
            return dcc.Graph(figure=fig)
        else:
            return html.P("No event data available for the selected teams.",
                         style={'textAlign': 'center', 'color': '#7f8c8d', 'padding': '20px'})
        
    except Exception as e:
        return html.P(f"Error creating event distribution: {str(e)}",
                     style={'textAlign': 'center', 'color': '#e74c3c', 'padding': '20px'})
