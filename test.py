from utils.data_loader import load_match_data
match_id = 69304
events_df = load_match_data(match_id)
event_types = set(events_df['type'])
print('Available event types:', event_types)
if 'Shot' in event_types: print('\nExample shot:', events_df[events_df['type'] == 'Shot'].iloc[0].to_dict())
if 'Dribble' in event_types: print('\nExample dribble:', events_df[events_df['type'] =='Dribble'].iloc[0].to_dict())