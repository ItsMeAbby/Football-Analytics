# UEFA Euro 2024 Analytics Dashboard

A comprehensive interactive data visualization platform for analyzing UEFA Euro 2024 football tournament data using StatsBomb's open dataset. Built with Python's Dash framework and combining Plotly's interactive web-based charts with Matplotlib's specialized football visualizations through the mplsoccer library. This project demonstrates advanced visualization techniques, robust data engineering practices, and professional-grade sports analytics capabilities.

## 🌟 Features

### � Tournament Overview Dashboard
- **Key Tournament Statistics**: Pre-calculated and cached metrics including total matches (51), participating teams, total goals, and goals per match ratios
- **Goals Analysis**: Horizontal bar charts ranking teams by total goals with color intensity mapping and hover functionality for efficiency analysis
- **Team Performance Analysis**: Dual visualization approach combining comprehensive standings table with color-coded metrics and stacked horizontal bar charts showing win/draw/loss percentages
- **Match Insights**: Tournament-wide statistical patterns through histograms (goals per match distribution, goal difference distribution) and pie charts for match outcome breakdown

### 🏟️ Match Overview Dashboard
- **Interactive Match Selection**: Hierarchical team and match selection interface with six coordinated visualization tabs
- **Shot Maps with Expected Goals (xG)**: Spatial positioning with size encoding proportional to xG values, color-coded by outcome (goals in red, shots in blue), using mplsoccer coordinate system
- **Pass Network Analysis**: Force-directed graph layouts with spatial positioning revealing team structure and player relationships. Node sizes represent passing involvement, edge thickness indicates pass frequency, with position acronym labels
- **Expected Goals Timeline**: Cumulative line charts with goal annotations showing match momentum and xG progression throughout match duration
- **Match Statistics**: Symmetric horizontal bar charts for direct team comparison, with metrics categorized by type (possession, shooting, passing, defensive)
- **Key Events Timeline**: Chronological visualization of goals, cards, and substitutions with color-coded team identification and temporal layout
- **Formation Analysis**: Individual player activity density plots using mplsoccer's formation grid system, with KDE plots showing movement patterns based on Ball Receipt events

### 🏃‍♂️ Player Performance Dashboard
- **Hierarchical Selection Interface**: Four specialized visualization tabs for individual player analysis
- **Shot Analysis**: Player-specific shot maps with spatial accuracy using mplsoccer coordinates, quality encoding through circle sizes, and outcome differentiation with distinct icons
- **Touch Heatmaps**: Grid-based spatial analysis using 6x5 standardized zones (30 regions) with percentage quantification and white-to-red gradient intensity mapping
- **Progressive Actions Analysis**: Horizontal bar charts showing forward ball progression (10+ meters toward goal) with team context and ranking visualization
- **Performance Metrics - Dual Radar Innovation**: Separates volume metrics (goals, shots, passes, dribbles, duels, interceptions) from success rate metrics (pass accuracy, shot accuracy, duel success) with color distinction and multi-player overlay capability

### ⚽ Tactical Analysis Component
- **Formation Analysis**: Team shape and player positioning with average position calculation, formation-specific offset algorithms, and role-based color coding
- **Defensive Actions Analysis**: Spatial analysis of tackles, interceptions, blocks, and clearances with density heatmapping and success rate overlays
- **Attacking Patterns**: Final third activity analysis (x > 80) with spatial mapping of shots, dribbles, key passes, and crosses
- **Set Piece Analysis**: Comprehensive evaluation of corners, free kicks, and throw-ins with frequency analysis, spatial distribution, and effectiveness metrics
- **Team Comparison**: Symmetric horizontal bar charts with normalized scaling for tactical metrics comparison
- **Pass Length Distribution & Event Timeline**: Secondary visualizations showing team passing patterns and match activity distribution

### 🔍 Event Explorer Interface
- **Comprehensive Filtering System**: Filter by team, player, event type, and time range with real-time updates
- **Event Timeline**: Temporal distribution visualization with activity peak identification and dynamic filtering integration
- **Event Heatmap**: Spatial density visualization using mplsoccer coordinates with density gradient encoding and filter integration
- **Event Distribution**: Categorical analysis of nine event types with team comparison and frequency ranking
- **Interactive Data Table**: Dynamic column display with native filtering, pagination (20 events per page), and CSV export functionality
- **Summary Statistics**: Real-time filtered dataset context including event counts, player involvement, dominant event types, and temporal windows

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

## 📊 Data Source & Technical Foundation

This dashboard uses **StatsBomb's comprehensive UEFA Euro 2024 dataset** accessed through their official Python API (`statsbombpy`), representing one of the most detailed publicly available football datasets:

### Dataset Characteristics
- **Competition Coverage**: All 51 matches from UEFA Euro 2024 (Competition ID: 55, Season ID: 282)  
- **Data Granularity**: Event-level data with millisecond timestamp precision (~45,000+ events per match)
- **Spatial Resolution**: Coordinate data with 120x80 pitch dimension normalization
- **Event Types**: Comprehensive coverage including passes, shots, tackles, carries, dribbles, and defensive actions
- **Advanced Metrics**: Expected Goals (xG), progressive actions, and tactical positioning data

### Technical Architecture
- **Dual Visualization Approach**: Combines Plotly's interactive web-based charts with Matplotlib's specialized football visualizations through mplsoccer
- **Performance Optimization**: Intelligent caching strategies, efficient coordinate transformation algorithms, and scalable component architecture
- **Real-time Interactivity**: Dynamic data filtering, cross-visualization highlighting, and coordinated view updates
- **Modular Design**: Encapsulated components for reusability and maintainability with graceful error handling

## 🎯 Target Audience & Applications

### Educators & Learners
- **Tactical Educators & Students**: Visual, data-driven tools for teaching and learning football tactics
- **Data Science Instructors**: Real-world case study for data visualization and sports analytics methodology  
- **Aspiring Sports Analysts**: Hands-on experience with professional-level analytics tools and methodologies

### Industry Professionals  
- **Coaching & Technical Staff**: In-depth visual insights for match analysis and tactical planning
- **Journalists & Broadcasters**: Engaging graphics and insights for enhanced storytelling and analysis
- **Football Analytics Community**: Advanced visualization techniques and open-source implementation examples

## 🎨 Visualization Design Philosophy

### Core Design Principles
- **Accessibility**: Intuitive interfaces for users with varying levels of football analytics expertise
- **Comprehensiveness**: Complete coverage from individual events to tournament-wide patterns  
- **Professional Quality**: Visualization standards meeting professional sports analytics requirements
- **Perception-Driven Design**: Visualization types chosen based on specific analytical tasks

### Innovative Approaches
- **Dual Radar Chart Methodology**: Separates volume metrics from success rate metrics to prevent analytical confusion
- **Grid-Based Spatial Analysis**: 6x5 standardized zones enabling quantifiable cross-player comparisons
- **Force-Directed Network Layouts**: Preserves football-specific spatial context while revealing tactical patterns
- **Formation Grid System**: Individual player density plots using mplsoccer's formation framework with predefined offsets

### Technical Implementation Highlights
- **Hybrid Visualization Strategy**: Plotly for interactivity, mplsoccer for specialized football visualizations
- **Coordinate Transformation**: Accurate pitch representations using professional sports visualization standards
- **Dynamic Filtering Architecture**: Real-time updates across all visualization components
- **Memory-Optimized Processing**: LRU caching and lazy loading for large dataset performance

---

**Explore Professional Football Analytics! ⚽📊**