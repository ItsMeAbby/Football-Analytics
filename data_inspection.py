import pandas as pd
from utils.data_loader import load_tournament_data

# Load the tournament data
df = load_tournament_data()

# Basic info
print("DataFrame shape:", df.shape)
print("\nDataFrame columns:", df.columns.tolist())

# Check for specific columns needed for visualizations
print("\nChecking for shot map required columns...")
print("'x' in columns:", 'x' in df.columns)
print("'y' in columns:", 'y' in df.columns)
print("'shot_statsbomb_xg' in columns:", 'shot_statsbomb_xg' in df.columns)
print("'shot_outcome' in columns:", 'shot_outcome' in df.columns)

# Check for heatmap required columns (already checked x, y above)

# Check for progressive passes required columns
print("\nChecking for progressive passes required columns...")
print("'pass_end_x' in columns:", 'pass_end_x' in df.columns)

# Check structure of specific fields
print("\nSample structure of first shot event:")
shot_row = df[df['type'] == 'Shot'].iloc[0] if any(df['type'] == 'Shot') else None
if shot_row is not None:
    print("x:", shot_row.get('x', 'Not found'))
    print("y:", shot_row.get('y', 'Not found'))
    print("shot_statsbomb_xg:", shot_row.get('shot_statsbomb_xg', 'Not found'))
    print("shot_outcome:", shot_row.get('shot_outcome', 'Not found'))
    
# Check if coordinates are in a nested structure
print("\nChecking if coordinates might be in a nested structure...")
if 'location' in df.columns:
    first_loc = df['location'].iloc[0]
    print("'location' first value:", first_loc)
    
if 'pass_end_location' in df.columns:
    first_pass_end = df['pass_end_location'].iloc[0]
    print("'pass_end_location' first value:", first_pass_end)