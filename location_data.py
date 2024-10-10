import pandas as pd

# Load the data
stop_times = pd.read_csv('stop_times.txt')
stops = pd.read_csv('stops.txt')

# Filter stop_times to include only rows with trip_id present in trips
filtered_stops = stops[stops['stop_id'].isin(stop_times['stop_id'])]

# Write the filtered dataframe back to a CSV file
filtered_stops.to_csv('stops.txt', index=False)
