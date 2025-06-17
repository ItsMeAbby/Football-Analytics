# UEFA Euro 2024 Analytics Dashboard

A comprehensive data visualization dashboard for analyzing UEFA Euro 2024 football/soccer tournament data using StatsBomb's free dataset.

## 🌟 Features

### 🏟️ Match Overview
- **Tournament Statistics**: Total matches, teams, goals, and averages
- **Interactive Match Selection**: Choose teams and specific matches
- **Shot Maps**: Visualize shooting patterns for both teams
- **Pass Networks**: Analyze team passing connections and formations
- **Expected Goals (xG) Timeline**: Track match momentum over time
- **Team Performance Comparison**: Side-by-side statistical analysis

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