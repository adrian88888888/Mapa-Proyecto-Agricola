import requests
import polyline as pl
import os
import csv
import json

def get_polyline(api_key, origin, destination):
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={api_key}'
    response = requests.get(url)
    data = response.json()
    encoded_polyline = response.json()['routes'][0]['overview_polyline']['points']
    polyline = pl.decode(encoded_polyline)
    return polyline

def get_combined_polyline(locations, api_key):
    combined_polyline = []
    for i in range(len(locations) - 1):
        origin = f"{locations[i][0]},{locations[i][1]}"
        destination = f"{locations[i+1][0]},{locations[i+1][1]}"
        polyline = get_polyline(api_key, origin, destination)
        combined_polyline.append(polyline)
    return combined_polyline

def get_locations(api_key, googleplaces_data, ruta_a_ids):
    locations = []
    for id in ruta_a_ids:
        for place in googleplaces_data:
            place_id = place['place_id']
            if id == place_id:
                lat = place['geometry']['location']['lat']
                lng = place['geometry']['location']['lng']
                coords = (lat, lng)
                locations.append(coords)
    return locations

def load_single_col_tsv_into_list(file):
    with open(file, 'r', newline='') as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter='\t')
        first_column_list = [row[0] for row in tsvreader]
    return first_column_list

def save_polyline_to_file(polyline, filename):
    with open(filename, 'w') as file:
        json.dump(polyline, file)

current_directory = os.path.dirname(os.path.abspath(__file__))

# load tsv's
ruta_a_path = os.path.join(current_directory, 'Ruta A v2.tsv')
ruta_a_ids = load_single_col_tsv_into_list(ruta_a_path)

# load json
json_from_googleplaces_path = os.path.join(current_directory, 'json_from_googleplaces.json')
with open(json_from_googleplaces_path, 'r') as file:
    googleplaces_data = json.load(file)

api_key = 'AIzaSyApbvwG7WZYTkcno9Pxfgwl005pKoU6YrM'
locations = get_locations(api_key, googleplaces_data, ruta_a_ids)

combined_polyline = get_combined_polyline(locations, api_key)
# print(combined_polyline, '<--------------------------')

save_name = 'ruta_a.json'
current_directory = os.getcwd()
save_path = os.path.join(current_directory, 'map-creator', 'data', save_name)
save_polyline_to_file(combined_polyline, save_path)
