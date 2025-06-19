# UEFA Euro 2024 Analytics Dashboard

A comprehensive data visualization dashboard for analyzing UEFA Euro 2024 football/soccer tournament data using StatsBomb's free dataset.

## 🌟 Features

### 🏟️ Match Overview
- **Tournament Statistics**: Total matches, teams, goals, and averages
- **Interactive Match Selection**: Choose teams and specific matches
- **Shot Maps**: Visualize shooting patterns, outcomes, and Expected Goals (xG) values for both teams
- **Pass Networks**: Analyze team passing connections with position-based networks showing player roles
- **Expected Goals (xG) Timeline**: Track match momentum and goal-scoring chances throughout the match
- **Match Statistics**: Side-by-side statistical comparison including shots, passes, possession, and more
- **Key Events**: Chronological timeline of important match events including goals, cards, and substitutions
- **Formations**: View team formations with player position heatmaps showing movement patterns

### 🏃‍♂️ Player Dashboard
- **Individual Player Stats**: Goals, shots, passes, accuracy metrics
- **Performance Radar Charts**: Multi-dimensional player analysis
- **Touch Heatmaps**: Visualize player positioning and activity zones
- **Progressive Actions**: Track forward passes and ball progression
- **Player Comparison Tool**: Compare any two players across metrics

### ⚡ Tactical Analysis
- **Formation Analysis**: Average player positions and team shape
- **Pass Network Visualization**: Team connectivity and key players
- **Defensive Actions Heatmap**: Tackle, interception, and clearance zones
- **Attacking Patterns**: Final third activity and shot locations
- **Set Piece Analysis**: Corner, free kick, and throw-in statistics
- **Team Comparison**: Head-to-head tactical metrics

### 🔍 Event Explorer
- **Raw Data Access**: Filter and explore all match events
- **Advanced Filtering**: By team, player, event type, and time range
- **Event Timeline**: Visualize match activity over time
- **Data Export**: Download filtered data as CSV
- **Interactive Data Table**: Sort and search through events

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the dashboard**
   ```bash
   python app.py
   ```

3. **Open your browser**
   Navigate to `http://localhost:8050` to view the dashboard

## 📊 Data Source

This dashboard uses **StatsBomb's free Euro 2024 dataset**, which includes:
- All 51 matches from the tournament
- Detailed event data (passes, shots, tackles, etc.)
- Player and team information
- Advanced metrics like Expected Goals (xG)
- Positional data for tactical analysis

## 🎨 Dashboard Features

### Match Overview Tabs
- **Shot Maps**: Interactive visualization of all shot attempts with circle size representing Expected Goals (xG) value and different colors for various outcomes (goals, saved shots, etc.). Hover over shots for detailed information.

- **Pass Networks**: Network visualization showing team shape and passing connections. Players are displayed with their position acronyms (GK, CB, LW, etc.) and node size represents player involvement. Line thickness indicates pass frequency between players, and different shapes show substituted players.

- **xG Timeline**: Chart showing the cumulative Expected Goals (xG) for both teams throughout the match. Vertical dashed lines mark actual goals scored with player names. The visualization helps understand which team created better chances and when.

- **Match Stats**: Comprehensive comparison of match statistics including shots, shots on target, successful and failed passes, possession percentage, expected goals, and actual goals scored. Color-coded bars represent each team's performance.

- **Key Events**: Chronological timeline of important match events including goals, cards, substitutions, and fouls. Events are color-coded by team and include minute markers and detailed descriptions.

- **Formations**: Team formation visualizations with player position heatmaps showing where each player operated during the match. Players are labeled with position acronyms and their names, with heatmap intensity showing movement patterns.

### Visual Design
- **Modern UI**: Clean, professional interface with Euro 2024 theming
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Interactive Charts**: Hover, zoom, and click interactions with Plotly
- **Custom Styling**: Football-themed colors and soccer pitch visualizations

### Performance Features
- **Caching**: Data is cached to improve loading times
- **Error Handling**: Graceful handling of data loading issues
- **Loading States**: Visual feedback during data operations
- **Export Capabilities**: Download charts and data

---

**Happy Analyzing! ⚽📊**