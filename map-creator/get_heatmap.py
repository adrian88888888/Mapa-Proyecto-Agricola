import folium
from folium.plugins import HeatMap
import json
import os

def get_heatmap_data(googleplaces_data):
    heatmap_data = []
    for place in googleplaces_data:
        search_term = place['additional_info']['search_term']
        if search_term == "Verduleria":
            continue
        lat = place['geometry']['location']['lat']
        lng = place['geometry']['location']['lng']
        heatpoint = [lat, lng]
        heatmap_data.append(heatpoint)
    return heatmap_data

current_directory = os.getcwd()
json_path = os.path.join(current_directory, 'map-creator', 'data', 'json_from_googleplaces.json')
with open(json_path, 'r') as f:
    googleplaces_data = json.load(f)
heatmap_data = get_heatmap_data(googleplaces_data)
starting_zoom = 12
coords_plaza_ejercito = (-34.86304757940927, -56.169061198494575)
starting_location = coords_plaza_ejercito
folium_map = folium.Map(location=starting_location, zoom_start=starting_zoom, crs='EPSG3857') # crs='EPSG3857' es para usar el mismo sistema de coordenadas q el de google maps
HeatMap(heatmap_data).add_to(folium_map)
map_path = os.path.join(current_directory, 'map-creator', 'folium_heatmap.html')
folium_map.save(map_path)
