import folium
import json
import os
import pprint

def get_formated_open_time_from_complementary_data(place_id, complementary_data):
    for place in complementary_data:
        if place['place_id'] == place_id:
            return place.get('formatted_open_time')

starting_zoom = 12
coords_plaza_ejercito = (-34.86304757940927, -56.169061198494575)
starting_location = coords_plaza_ejercito

current_directory = os.path.dirname(os.path.abspath(__file__))
data_path = r'\data'
data_from_googleplaces_path = current_directory + data_path + r'\data_from_googleplaces.json'
complementary_data_path = current_directory + data_path + r'\complementary_data.json'
map_path = current_directory + r'\user_folium_map_from_data.html'

with open(data_from_googleplaces_path, 'r') as file:
    googleplaces_data = json.load(file)

with open(complementary_data_path, 'r') as file:
    complementary_data = json.load(file)

folium_map = folium.Map(location=starting_location, zoom_start=starting_zoom, crs='EPSG3857') # crs='EPSG3857' es para usar el mismo sistema de coordenadas q el de google maps

for place in googleplaces_data:
    name = place['name']
    place_id = place['place_id']
    lat = place['geometry']['location']['lat']
    lng = place['geometry']['location']['lng']
    link_to_place = place['url']
    resenias = place.get('user_ratings_total', 0)
    estrellas = place.get('rating')
    search_term = place['additional_info']['search_term']
    formated_open_time = get_formated_open_time_from_complementary_data(place_id, complementary_data)
    if search_term == "Verduleria":
        icono_personalizado = folium.CustomIcon(current_directory + r'\icons\verduleria.png', icon_size=(32, 32))
    elif search_term == 'Agropecuaria':
        icono_personalizado = folium.CustomIcon(current_directory + r'\icons\agropecuaria.png', icon_size=(32, 32))
    elif search_term == 'Floreria':
        icono_personalizado = folium.CustomIcon(current_directory + r'\icons\floreria.png', icon_size=(32, 32))
    elif search_term == 'Feria':
        icono_personalizado = folium.CustomIcon(current_directory + r'\icons\feria.png', icon_size=(32, 32))
    else:
        icono_personalizado = folium.CustomIcon(current_directory + r'\icons\pina.png', icon_size=(32, 32))

    folium.Marker(
        location=[lat, lng],
        popup='Id: <br>' + place_id + '<br><br>Nombre: <br>' + name + '<br><br>' + '<a href="' + link_to_place + '" target="_blank">Abrir en Maps &boxbox;</a>' + '<br><br>Reseñas: <br>' + str(resenias) + '<br><br>Estrellas: <br>' + str(estrellas) + '<br><br>' + 'Horarios:<br>' + formated_open_time,
        icon=icono_personalizado
        ).add_to(folium_map)

nelson = [-34.8265, -56.2651]
uam = [-34.8192, -56.2639]
folium.Marker(
    location=nelson,
    popup="Nelson",
    icon=folium.Icon(color="purple"),
).add_to(folium_map)

folium.Marker(
    location=uam,
    popup="UAM",
    icon=folium.Icon(color="purple"),
).add_to(folium_map)

folium_map.save(map_path)
full_map_path = os.path.abspath(map_path)
os.startfile(full_map_path)
