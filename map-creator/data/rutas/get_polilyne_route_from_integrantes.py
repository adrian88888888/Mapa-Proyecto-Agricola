import requests
import polyline as pl
import os
import csv
import json

api_key = ''

# un monton de paths q no se como establecer de forma facil todo de una
current_directory = os.path.dirname(os.path.abspath(__file__))
integrantes_ruta_sayago_path = os.path.join(current_directory, 'ruta_sayago', 'integrantes de la ruta.tsv')
json_from_googleplaces_path = r'C:\Work in Progress\Repos en GitHub\Mapa-Proyecto-Agricola\map-creator\data\from-google-places\json_from_googleplaces.json'
save_name = 'polilinea ruta.json'
save_path = os.path.join(current_directory, 'ruta_sayago', save_name)

def get_polyline(api_key, origin, destination):
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={api_key}'
    response = requests.get(url)
    data = response.json()
    encoded_polyline = response.json()['routes'][0]['overview_polyline']['points']
    polyline = pl.decode(encoded_polyline)
    return polyline

def get_combined_polyline(locations, api_key):
    combined_polyline = []
    origin = f"{-34.8265},{-56.2651}"
    destination = f"{locations[1][0]},{locations[1][1]}"
    polyline = get_polyline(api_key, origin, destination)
    combined_polyline.append(polyline)
    for i in range(len(locations) - 1):
        origin = f"{locations[i][0]},{locations[i][1]}"
        destination = f"{locations[i+1][0]},{locations[i+1][1]}"
        polyline = get_polyline(api_key, origin, destination)
        combined_polyline.append(polyline)
    origin = f"{locations[i+1][0]},{locations[i+1][1]}"
    destination = f"{-34.8265},{-56.2651}"
    polyline = get_polyline(api_key, origin, destination)
    combined_polyline.append(polyline)
    return combined_polyline

def get_locations(api_key, googleplaces_data, integrantes):
    locations = []
    for id in integrantes:
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


# load tsv's
integrantes_ruta_sayago = load_single_col_tsv_into_list(integrantes_ruta_sayago_path)

# load json
with open(json_from_googleplaces_path, 'r') as file:
    googleplaces_data = json.load(file)

locations = get_locations(api_key, googleplaces_data, integrantes_ruta_sayago)

combined_polyline = get_combined_polyline(locations, api_key)

save_polyline_to_file(combined_polyline, save_path)
