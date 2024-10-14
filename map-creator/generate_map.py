import folium
import json
from folium.plugins import Draw, AntPath, LocateControl
import os
import pprint
import csv
import polyline
import pandas as pd

# quiza esta linea te sirva en este proyecto: current_path = os.getcwd()

def get_formatted_open_time(place_id, formatted_open_time):
    for place in formatted_open_time:
        if place['place_id'] == place_id:
            return place['formatted_open_time']

def load_single_col_tsv_into_set(file):
    with open(file, 'r', newline='') as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter='\t')
        first_column_set = {row[0] for row in tsvreader}
    return first_column_set

def get_tuple_of_coords_from_string(string):
    print(string)
    lat_str, lon_str = string.split(',')
    lat = float(lat_str)
    lon = float(lon_str)
    return (lat, lon)

def add_clients_from_dataframe(mapa, dataframe):
    rows, columns = dataframe.shape
    for each_row in range(rows):
        nombre_en_tabla_ventas = dataframe.iloc[each_row, nombre_en_tabla_ventas_col]
        if not pd.isna(nombre_en_tabla_ventas):
            categoria = dataframe.iloc[each_row, categoria_col]
            if categoria == 'UAM':
                continue

            coords_string = dataframe.iloc[each_row, coords_col]
            if not pd.isna(coords_string):
                coords = get_tuple_of_coords_from_string(coords_string)
                lat, lon = coords

            frecuencia_de_compra = dataframe.iloc[each_row, frecuencia_de_compra_col]
            if frecuencia_de_compra == '1-Frecuente':
                icon_name = 'contact green.png'
            elif frecuencia_de_compra == '2-Esporadico':
                icon_name = 'contact yellow.png'
            elif frecuencia_de_compra == '3-No Establecida':
                icon_name = 'contact gray.png'
            elif frecuencia_de_compra == '4-Muy Esporadico':
                icon_name = 'contact red.png'

            icon_path = repo_path + '\map-creator\icons\\' + icon_name
            icono_personalizado = folium.CustomIcon(icon_path, icon_size=(32, 32))

            link_wwp = 'https://wa.me/' + str(dataframe.iloc[each_row, wwp_col])

            folium.Marker(
                        location=coords,
                        popup=str(dataframe.iloc[each_row, nombre_en_tabla_ventas_col]) + '<a href=' + link_wwp + '>Abrir Chat de Wwp</a>',
                        icon=icono_personalizado
                        ).add_to(mapa)
    return mapa

def letra_a_numero(letra):
    return ord(letra.lower()) - ord('a')

# config
map_output_name = 'map.html'
repo_path = r'C:\Work in Progress\Repos en GitHub\Mapa-Proyecto-Agricola'
wwp_col = letra_a_numero('H')
place_nombre_en_tabla_ventas_col = letra_a_numero('M')
coords_col = letra_a_numero('L')
nombre_en_tabla_ventas_col = letra_a_numero('I')
frecuencia_de_compra_col = letra_a_numero('F')
categoria_col = letra_a_numero('E')

# paths
# map
map_path = os.path.join(repo_path, 'map-creator', map_output_name)
# data
clientes_database_path                  = repo_path + r'\map-creator\data\from-google-sheets-clientes-database\using tsv + pandas\Administración Agricola - 🤝Clientes.tsv'
data_from_googleplaces_path             = repo_path + r'\map-creator\data\from-google-places\json_from_googleplaces.json'
formatted_open_time_path                = repo_path + r'\map-creator\data\from-google-places\formatted_open_time.json'
clientes_macetas_de_albahaca_path       = repo_path + r'\map-creator\data\agrupando-lugares\potenciales clientes para macetas de albahaca.tsv'
dados_de_baja_por_cualquier_motivo_path = repo_path + r'\map-creator\data\agrupando-lugares\dados de baja por cualquier motivo.tsv'
florerias_de_eventos_o_cementerios_path = repo_path + r'\map-creator\data\agrupando-lugares\florerias de eventos o cementerios.tsv'
polyline_rute_sayago_path               = repo_path + r'\map-creator\data\rutas\ruta_sayago\polilinea ruta.json'
polyline_rute_del_prado_path            = repo_path + r'\map-creator\data\rutas\ruta_del_prado\polilinea ruta.json'
# icons
nelson_icon_path    = repo_path + r'\map-creator\icons\nelson.png'
uam_icon_path       = repo_path + r'\map-creator\icons\uam.png'

# load data
with open(data_from_googleplaces_path, 'r') as file:
    googleplaces_data = json.load(file)

with open(formatted_open_time_path, 'r') as file:
    json_of_formatted_open_time = json.load(file)

with open(polyline_rute_sayago_path, 'r') as file:
    rute_sayago = json.load(file)

with open(polyline_rute_del_prado_path, 'r') as file:
    rute_del_prado = json.load(file)

dataframe = pd.read_csv(clientes_database_path, sep='\t')
dataframe = dataframe.drop(index=[0, 1]).reset_index(drop=True)

clientes_macetas_de_albahaca = load_single_col_tsv_into_set(clientes_macetas_de_albahaca_path)
dados_de_baja_por_cualquier_motivo = load_single_col_tsv_into_set(dados_de_baja_por_cualquier_motivo_path)
florerias_de_eventos_o_cementerios = load_single_col_tsv_into_set(florerias_de_eventos_o_cementerios_path)

starting_zoom = 12
coords_plaza_ejercito = (-34.86304757940927, -56.169061198494575)
starting_location = coords_plaza_ejercito

folium_map = folium.Map(location=starting_location, zoom_start=starting_zoom, crs='EPSG3857') # crs='EPSG3857' es para usar el mismo sistema de coordenadas q el de google maps

# populate map
nelson = [-34.8265, -56.2651]
uam = [-34.8192, -56.2639]

folium.Marker(
    location=nelson,
    popup="Nelson",
    icon=folium.CustomIcon(nelson_icon_path, icon_size=(32, 32)),
).add_to(folium_map)

folium.Marker(
    location=uam,
    popup="UAM",
    icon=folium.CustomIcon(uam_icon_path, icon_size=(32, 64)),
).add_to(folium_map)

add_clients_from_dataframe(folium_map, dataframe)

for place in googleplaces_data:
    name = place['name']
    place_id = place['place_id']
    lat = place['geometry']['location']['lat']
    lng = place['geometry']['location']['lng']
    link_to_place = place['url']
    resenias = place.get('user_ratings_total', 0)
    estrellas = place.get('rating')
    search_term = place['additional_info']['search_term']
    formatted_open_time = get_formatted_open_time(place_id, json_of_formatted_open_time)
    if place_id in clientes_macetas_de_albahaca:
        icon_name = 'tick.png'
        # continue
    # elif place_id in dados_de_baja_por_cualquier_motivo:
    #     icon_name = 'cancel.png'
    elif place_id in dados_de_baja_por_cualquier_motivo:
        continue
    else:
        if search_term == "Verduleria":
            icon_name = 'verduleria.png'
        elif search_term == 'Agropecuaria':
            icon_name = 'agropecuaria.png'
        elif search_term == 'Floreria':
            icon_name = 'floreria.png'
        elif search_term == 'Feria':
            icon_name = 'feria.png'
        elif search_term == 'Vivero':
            icon_name = 'vivero.png'
        else:
            icon_name = 'no-icon.png'

    icon_path = repo_path + r'\map-creator\icons\\' + icon_name
    icono_personalizado = folium.CustomIcon(icon_path, icon_size=(32, 32))

    popup = 'Id: <br>' + place_id + '<br><br>Nombre: <br>' + name + '<br><br>' + '<a href="' + link_to_place + '" target="_blank">Abrir en Maps &boxbox;</a>' + '<br><br>Reseñas: <br>' + str(resenias) + '<br><br>Estrellas: <br>' + str(estrellas) + '<br><br>' + 'Horarios:<br>' + str(formatted_open_time)
    folium.Marker(
        location=[lat, lng],
        popup=folium.Popup(popup, max_width=3000),
        icon=icono_personalizado
        ).add_to(folium_map)

# folium.plugins.AntPath(locations=rute_sayago, delay=2000, opacity=1, color='blue', weight=5, dash_array=[20, 30]).add_to(folium_map)
# folium.plugins.AntPath(locations=rute_del_prado, delay=2000, opacity=1, color='green', weight=5, dash_array=[20, 30]).add_to(folium_map)

locate_control = LocateControl()
locate_control.add_to(folium_map)
Draw(export=True).add_to(folium_map)

folium_map.save(map_path)
full_map_path = os.path.abspath(map_path)
os.startfile(full_map_path)
