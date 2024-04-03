import folium
import json
import os

def extract_coordinates_from_geojson(geojson_file):
    with open(geojson_file, 'r') as f:
        data = json.load(f)

    coordinates = data['features'][0]['geometry']['coordinates']

    inverted_coordinates = [(coord[1], coord[0]) for coord in coordinates]
    return inverted_coordinates

current_directory = os.path.dirname(os.path.abspath(__file__))
geojson_path = os.path.join(current_directory, 'data.geojson')

polilinea_coords = extract_coordinates_from_geojson(geojson_path)

print("Coordenadas de la polilínea invertidas:")
print(polilinea_coords)
