from datetime import datetime, date
import requests
import pandas as pd

# Load your data
silver_loop = pd.read_csv('route_data/13c.txt')
black_loop = pd.read_csv('route_data/14c.txt')
tower_acres_loop = pd.read_csv('route_data/15c.txt')
bronze_loop = pd.read_csv('route_data/16c.txt')


def get_weather(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=imperial"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        temperature = data["main"]["temp"]
        weather_description = data["weather"][0]["description"]
        cloudy_percentage = data["clouds"]["all"]

        return temperature, weather_description, cloudy_percentage
    else:
        print("City not found or API request failed")


# Replace with your actual API key
api_key = "8979b854c91b24e83bce616a52562c2b"
lat = 40.4259
lon = -86.9081


def get_bus_locations(time, bus_loop):
    # Parse the target time to a datetime object for consistent comparisons
    target_time = pd.to_datetime(time, format="%H:%M:%S").time()

    # Convert the 'arrival_time' column to datetime.time for comparison
    bus_loop['arrival_time'] = pd.to_datetime(bus_loop['arrival_time'], format="%H:%M:%S").dt.time

    # Group the data by 'trip_id' and get the min and max arrival time for each trip
    trip_time_bounds = bus_loop.groupby('trip_id')['arrival_time'].agg(['min', 'max']).reset_index()

    # Filter trips where the target time is within the range of min and max arrival times
    valid_trip_ids = trip_time_bounds[
        (trip_time_bounds['min'] <= target_time) & (trip_time_bounds['max'] > target_time)
        ]['trip_id']

    # Filter the original bus loop data for only those valid trip IDs
    filtered_data = bus_loop[bus_loop['trip_id'].isin(valid_trip_ids)]

    grouped_data = filtered_data.groupby('trip_id')

    results = []

    for trip_id, group in grouped_data:
        bus_location = {}
        next_time = "00:00:00"
        previous_row = None
        for _, row in group.iterrows():
            next_time = row['arrival_time']
            if next_time >= target_time:
                next_stop = row
                bus_location['next_arrival_time'] = next_time
                if previous_row is not None:
                    bus_location['previous_stop'] = previous_row['stop_name']
                    next_time = datetime.combine(date.today(), next_stop['arrival_time'])
                    previous_time = datetime.combine(date.today(), previous_row['arrival_time'])
                    current_drive_time = (next_time - previous_time).total_seconds()
                    current_time = datetime.combine(date.today(), target_time)
                    seconds_into_drive = (current_time - previous_time).total_seconds()
                    bus_location['percentage_till_next'] = (seconds_into_drive / current_drive_time) * 100
                    seconds_till_next_stop = (next_time - current_time).total_seconds()
                    bus_location['seconds_till_next_stop'] = seconds_till_next_stop
                else:
                    bus_location['previous_stop'] = 'None'
                    bus_location['percentage_till_next'] = 100.00
                    bus_location['seconds_till_next_stop'] = 0.00

                bus_location['next_stop'] = next_stop['stop_name']
                break

            previous_row = row

        results.append(bus_location)

    return results


# Set display options to show all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)  # Adjust width as necessary to fit all columns

time = "10:30:00"  # Adjust the time format if necessary

results = get_bus_locations(time, tower_acres_loop)

temp, desc, cloudy = get_weather(lat, lon, api_key)

print(f"CURRENT TIME: {time}")
print(f"Weather in West Lafayette, IN:")
print(f"Temperature: {temp}")
print(f"Weather Description: {desc}")
print(f"Cloud Percentage: {cloudy}")
print("----------------------------")
print("Bus Locations:")
print(" ")

for bus in results:
    print(f"Bus is coming from: {bus['previous_stop']}")
    print(f"Will be at: {bus['next_stop']} in {bus['seconds_till_next_stop']} seconds ({bus['percentage_till_next']}%)")
    print("----------------------------------")
