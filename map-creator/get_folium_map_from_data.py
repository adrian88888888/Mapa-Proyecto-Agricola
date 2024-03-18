import folium
import json
from folium.plugins import Draw, AntPath
import os
import pprint
import csv
import rutes

def get_formated_open_time(place_id, formatted_open_time):
    for place in formatted_open_time:
        if place['place_id'] == place_id:
            return place.get('formatted_open_time')

def load_single_col_tsv_into_set(file):
    with open(file, 'r', newline='') as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter='\t')
        first_column_set = {row[0] for row in tsvreader}
    return first_column_set

starting_zoom = 12
coords_plaza_ejercito = (-34.86304757940927, -56.169061198494575)
starting_location = coords_plaza_ejercito

current_directory = os.path.dirname(os.path.abspath(__file__))
data_path = r'\data'
data_from_googleplaces_path = current_directory + data_path + r'\data_from_googleplaces.json'
formatted_open_time_path = current_directory + data_path + r'\formatted_open_time.json'
map_path = current_directory + r'\folium_map_from_data.html'

with open(data_from_googleplaces_path, 'r') as file:
    googleplaces_data = json.load(file)

with open(formatted_open_time_path, 'r') as file:
    formatted_open_time = json.load(file)

# load tsv's
candidatos_fuera_de_las_rutas_path = current_directory + r'\data\Candidatos fuera de las rutas.tsv'
dados_de_baja_por_cualquier_motivo_path = current_directory + r'\data\Dados de baja por cualquier motivo.tsv'
pertenecientes_a_ruta_a_path = current_directory + r'\data\Pertenecientes a Ruta A.tsv'

candidatos_fuera_de_las_rutas = load_single_col_tsv_into_set(candidatos_fuera_de_las_rutas_path)
dados_de_baja_por_cualquier_motivo = load_single_col_tsv_into_set(dados_de_baja_por_cualquier_motivo_path)
pertenecientes_a_ruta_a = load_single_col_tsv_into_set(pertenecientes_a_ruta_a_path)

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
    formated_open_time = get_formated_open_time(place_id, formatted_open_time)
    if place_id in candidatos_fuera_de_las_rutas:
        icon_name = 'tick.png'
    elif place_id in dados_de_baja_por_cualquier_motivo:
        icon_name = 'cancel.png'
    elif place_id in pertenecientes_a_ruta_a:
        icon_name = 'truck.png'
    else:
        if search_term == "Verduleria":
            icon_name = 'verduleria.png'
        elif search_term == 'Agropecuaria':
            icon_name = 'agropecuaria.png'
        elif search_term == 'Floreria':
            icon_name = 'floreria.png'
        elif search_term == 'Feria':
            icon_name = 'feria.png'
        else:
            icon_name = 'no-icon.png'

    icon_path = os.path.join(current_directory, 'icons', icon_name)
    icono_personalizado = folium.CustomIcon(icon_path, icon_size=(32, 32))

    popup = 'Id: <br>' + place_id + '<br><br>Nombre: <br>' + name + '<br><br>' + '<a href="' + link_to_place + '" target="_blank">Abrir en Maps &boxbox;</a>' + '<br><br>Reseñas: <br>' + str(resenias) + '<br><br>Estrellas: <br>' + str(estrellas) + '<br><br>' + 'Horarios:<br>' + formated_open_time
    folium.Marker(
        location=[lat, lng],
        popup=folium.Popup(popup, max_width=3000),
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

folium.plugins.AntPath(locations=rutes.ruta_a, delay=5000, opacity=1, color='orange', weight=5, dash_array=[20, 30]).add_to(folium_map)

# folium.PolyLine(ruta_a, color='blue', weight=2.5, opacity=1).add_to(folium_map)

Draw(export=True).add_to(folium_map)
folium_map.save(map_path)
full_map_path = os.path.abspath(map_path)
os.startfile(full_map_path)
