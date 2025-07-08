# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ENV
conda env named viz

## Project Overview

This is a comprehensive UEFA Euro 2024 analytics dashboard built with Dash/Plotly for interactive data visualization. The project analyzes StatsBomb's open football data to provide tactical insights, performance metrics, and match analysis through a multi-tab web interface.

## Development Commands

### Running the Application
```bash
python app.py
```
The dashboard will be available at `http://localhost:8050`

### Dependencies Management
```bash
pip install -r requirements.txt
```

### Testing Data Loading
```bash
python test.py
```
Basic script to verify match data loading functionality.

## Architecture

### Core Components
- **app.py**: Main application entry point with Dash app initialization
- **dashboards/layout.py**: Main layout orchestrator that creates the tabbed interface
- **utils/data_loader.py**: Data loading and caching layer with StatsBomb API integration
- **utils/plot_utils.py**: Plotly-based visualization utilities
- **utils/plot_utils_mpl.py**: Matplotlib-based visualization utilities

### Dashboard Modules
The application is organized into five main dashboard components:
- **components/match_overview_simple.py**: Tournament overview and detailed match analysis
- **components/player_dashboard.py**: Individual player statistics and comparisons  
- **components/tactical_view.py**: Formation analysis and tactical visualizations
- **components/event_explorer.py**: Raw event data exploration with filtering

### Data Pipeline
- Uses StatsBomb's free Euro 2024 dataset via `statsbombpy` library
- Implements LRU caching for performance optimization (`@lru_cache` decorators)
- Two data loading approaches: standard StatsBomb API and `mplsoccer.Sbopen` parser
- Data preprocessing includes coordinate extraction from nested location fields

### Key Features
- Interactive shot maps with xG visualization
- Pass network analysis using force-directed graphs  
- Expected Goals (xG) timeline tracking
- Player heatmaps and radar charts
- Formation visualization with position density
- Comprehensive event filtering and export

## Technical Notes

### Multiprocessing Considerations
The app includes specific resource cleanup mechanisms for multiprocessing semaphore management. The `cleanup_resources()` function and signal handlers prevent semaphore leaks when the application shuts down.

### Caching Strategy
- Tournament data: cached once (`maxsize=1`)
- Match data: cached for up to 20 matches (`maxsize=20`) 
- Team rosters: cached for all 24 teams (`maxsize=24`)
- SBOpen match data: cached for 10 matches (`maxsize=10`)

### Data Structure
The main event DataFrame includes processed coordinate columns:
- `x`, `y`: event locations
- `pass_end_x`, `pass_end_y`: pass destination coordinates  
- `carry_end_x`, `carry_end_y`: ball carry end positions

### Visualization Philosophy
The dashboard follows perception-driven design principles with consistent color coding, progressive disclosure of complex information, and coordinated views across visualizations to facilitate cross-analysis insights.