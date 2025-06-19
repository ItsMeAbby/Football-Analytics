# UEFA Euro 2024 Analytics Dashboard

A comprehensive interactive data visualization dashboard for analyzing UEFA Euro 2024 football/soccer tournament data using StatsBomb's open data. This project demonstrates advanced visualization techniques to provide tactical insights, performance metrics, and match analysis.

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

## 🎨 Dashboard Design and Visualization Strategy

### Match Overview Components
- **Shot Maps**: Interactive scatter plots showing shot locations with size encoding for Expected Goals (xG) value. This visualization choice allows users to quickly identify shot quality beyond mere position, with larger circles representing higher-probability chances. Color-coding differentiates outcomes (goals, saved shots, missed), providing immediate pattern recognition of shooting effectiveness.

- **Pass Networks**: Force-directed graph visualization revealing team shape and passing connections. Players appear as nodes with position-based labels, while edges represent passing connections with line thickness proportional to passing frequency. This approach reveals tactical structure more effectively than traditional heatmaps by highlighting key playmakers and team connectivity.

- **xG Timeline**: Cumulative line chart displaying Expected Goals (xG) progression through the match. This visualization method was selected over bar charts to better illustrate momentum shifts and periods of dominance. Vertical markers for actual goals provide context for conversion efficiency and pivotal moments.

- **Match Stats**: Horizontal comparative bar charts for team metrics. This side-by-side approach was chosen over radar charts for its clearer quantitative comparisons while maintaining consistent color-coding for team identification. The custom design ensures precise value display within a compact visual footprint.

- **Key Events**: Chronological timeline using card-based event visualization. Events are color-coded by team with standardized icons (⚽,🟨,🟥,🔄) for rapid pattern recognition. This sequential approach preserves match narrative better than categorized groupings would.

- **Formations**: Kernel density estimation overlaid on pitch diagram showing positional tendencies. This hybrid approach combines the familiarity of traditional formation diagrams with the analytical depth of heatmaps, revealing both tactical setup and player movement ranges.

### Design Principles & Visualization Choices
- **Consistent Visual Language**: Standardized color coding across visualizations (green for positive outcomes, red for negative) to reduce cognitive load and increase learnability.
- **Progressive Disclosure**: Complex visualizations include collapsible detailed explanations that reveal design rationale, alternatives considered, and interpretation guidance.
- **Coordinated Views**: Related visualizations share consistent x-axes, color schemes, and interaction paradigms to facilitate cross-visualization insights.
- **Hierarchical Information Architecture**: Most important metrics are emphasized through size, position, and color contrast while maintaining accessibility guidelines.
- **Perception-Driven Design**: Visualization types chosen based on specific analytical tasks - scatter plots for positional data, line charts for temporal trends, bar charts for comparisons.

### Technical Implementation
- **Data Preprocessing Pipeline**: Event data is normalized, filtered, and aggregated before visualization to ensure optimal performance.
- **Modular Component Structure**: Dashboard components are encapsulated for reusability and maintainability.
- **Real-time Interactions**: Callbacks enable dynamic data filtering and cross-visualization highlighting without page reloads.
- **Memory Optimization**: LRU caching and lazy loading of data minimize memory footprint for large datasets.
- **Error Resilience**: Graceful degradation when data is incomplete or unavailable, with informative error messages.

---

**Happy Analyzing! ⚽📊**