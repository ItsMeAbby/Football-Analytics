from utils.data_loader import load_tournament_data
import pandas as pd

# Load the tournament data
df = load_tournament_data()

# Get shots
shot_df = df[df['type'] == 'Shot']
first_shot = shot_df.iloc[0] if not shot_df.empty else None

if first_shot is not None:
    print('Shot outcome:', first_shot['shot_outcome'] if 'shot_outcome' in first_shot else 'Not found')
    print('Shot xG:', first_shot['shot_statsbomb_xg'] if 'shot_statsbomb_xg' in first_shot else 'Not found')
    print('X coordinate:', first_shot['x'] if 'x' in first_shot else 'Not found')
    print('Y coordinate:', first_shot['y'] if 'y' in first_shot else 'Not found')
    
    # Let's see what's actually in the shot object
    print('\nShot object structure:')
    if 'shot' in first_shot:
        print(first_shot['shot'])
else:
    print("No shots found in the data")