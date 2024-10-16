import folium
import json
from folium.plugins import Draw, AntPath, LocateControl
import os
import pprint
import csv
import polyline
import pandas as pd
import re

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
    # print(string)
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
                continue
                # icon_name = 'contact red.png'

            icon_path = repo_path + '\map-creator\icons\\' + icon_name
            icono_personalizado = folium.CustomIcon(icon_path, icon_size=icon_size)

            link_wwp = 'https://wa.me/' + str(dataframe.iloc[each_row, wwp_col])

            folium.Marker(
                        location=coords,
                        popup=str(dataframe.iloc[each_row, nombre_en_tabla_ventas_col]) + '<a href=' + link_wwp + '>Abrir Chat de Wwp</a>',
                        icon=icono_personalizado
                        ).add_to(mapa)
    return mapa

def letra_a_numero(letra):
    return ord(letra.lower()) - ord('a')

def inject_script_into_html():
    with open('map.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    '''la siguiente linea:
    en el html cambia cosas como map_2d7121202b175e2f1001820765164300 a map 
    ya q folium crea una instancia de map pero le agrega todo eso para q puedas 
    hacer varios mapas unicos, luego en el .js necesito hacer referencia a esa
    instancia para capturar los eventos, asique deberia cambiar el contenido de
    js cada vez q genere el mapa, ya q al generarse denuevo se inventa una nueva
    "id":
    '''
    html_content = re.sub(r'map_\w+', 'map', html_content)

    
    '''lo siguiente agrega un entry point para el icon_resizer.js
    es asi de retorcido xq necesita agregarlo al final del todo
    ya q si llamas al script antes trabajaria sobre un objeto map
    q aun no fue creado en el html
    '''
    last_script_index = html_content.rfind('</script>')

    script_tag = '<script src="script.js"></script>'
    
    if last_script_index != -1:
        html_content = (html_content[:last_script_index + len('</script>')] + 
                        f'\n{script_tag}\n' + 
                        html_content[last_script_index + len('</script>'):])
    else:
        body_end_index = html_content.rfind('</body>')
        html_content = (html_content[:body_end_index] + 
                        f'{script_tag}\n' + 
                        html_content[body_end_index:])

    with open('map.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

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
icon_size = (15, 15)
coords_plaza_ejercito = (-34.86304757940927, -56.169061198494575)
starting_location = coords_plaza_ejercito

folium_map = folium.Map(location=starting_location, zoom_start=starting_zoom, crs='EPSG3857') # crs='EPSG3857' es para usar el mismo sistema de coordenadas q el de google maps

# populate map
nelson = [-34.8265, -56.2651]
uam = [-34.8192, -56.2639]

folium.Marker(
    location=nelson,
    popup="Nelson",
    icon=folium.CustomIcon(nelson_icon_path, icon_size=icon_size),
).add_to(folium_map)

folium.Marker(
    location=uam,
    popup="UAM",
    icon=folium.CustomIcon(uam_icon_path, icon_size=icon_size),
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
    # if place_id in clientes_macetas_de_albahaca:
    #     icon_name = 'tick.png'
        # continue
    # elif place_id in dados_de_baja_por_cualquier_motivo:
    #     icon_name = 'cancel.png'
    if place_id in dados_de_baja_por_cualquier_motivo:
        continue
    elif place_id in florerias_de_eventos_o_cementerios:
        continue
    else:
        if search_term == "Verduleria":
            continue
            # icon_name = 'verduleria.png'
        elif search_term == 'Agropecuaria':
            icon_name = 'agropecuaria.png'
        elif search_term == 'Floreria':
            icon_name = 'floreria.png'
        elif search_term == 'Feria':
            continue
            # icon_name = 'feria.png'
        elif search_term == 'Vivero':
            icon_name = 'vivero.png'
        else:
            icon_name = 'no-icon.png'

    icon_path = repo_path + r'\map-creator\icons\\' + icon_name
    icono_personalizado = folium.CustomIcon(icon_path, icon_size=icon_size)

    wpp_message_borrar_punto = 'https://wa.me/+59895930076?text=Adriano, borra este punto: ' + place_id
    wpp_message_marcar_punto_como_cliente = 'https://wa.me/+59895930076?text=Adriano, este punto ahora es cliente: ' + place_id

    popup = 'Nombre: <br>' + name + '<br><br>' + '<a href="' + wpp_message_borrar_punto + '" target="_blank">🗑️Borrar punto</a>' + '<br><br>' + '<a href="' + wpp_message_marcar_punto_como_cliente + '" target="_blank">➕Marcar punto como cliente</a>' + '<br><br>' + '<a href="' + link_to_place + '" target="_blank">🗺️Abrir en Google Maps</a>' + '<br><br>' + '📝Reseñas: ' + str(resenias) + '<br><br>' + '⭐Estrellas: ' + str(estrellas) + '<br><br>' + '🕙Horarios:<br>' + str(formatted_open_time) + '<br>' + '⚙️Id: <br>' + place_id
    folium.Marker(
        location=[lat, lng],
        popup=folium.Popup(popup, max_width=3000),
        icon=icono_personalizado
        ).add_to(folium_map)

# folium.plugins.AntPath(locations=rute_sayago, delay=2000, opacity=1, color='blue', weight=5, dash_array=[20, 30]).add_to(folium_map)
# folium.plugins.AntPath(locations=rute_del_prado, delay=2000, opacity=1, color='green', weight=5, dash_array=[20, 30]).add_to(folium_map)

# zona_central = [
#     [-34.900926, -56.200132],
#     [-34.906065, -56.199102],
#     [-34.908669, -56.200304],
#     [-34.910499, -56.196098],
#     [-34.913526, -56.185713],
#     [-34.913033, -56.178761],
#     [-34.911836, -56.176186],
#     [-34.903601, -56.173611],
#     [-34.904657, -56.163397],
#     [-34.913455, -56.160994],
#     [-34.920986, -56.161852],
#     [-34.91986, -56.147776],
#     [-34.910218, -56.146746],
#     [-34.906135, -56.134987],
#     [-34.899518, -56.138163],
#     [-34.897266, -56.15078],
#     [-34.898181, -56.162109],
#     [-34.896491, -56.166658],
#     [-34.899518, -56.174212],
#     [-34.900645, -56.188717],
#     [-34.895576, -56.191292],
#     [-34.900926, -56.200132]
# ]

# zona_avenida_italia = [
#     [-34.868327, -56.131039],
#     [-34.862271, -56.134901],
#     [-34.862764, -56.140652],
#     [-34.870651, -56.137991],
#     [-34.874384, -56.14666],
#     [-34.868257, -56.15593],
#     [-34.874595, -56.162024],
#     [-34.882059, -56.160564],
#     [-34.884241, -56.154385],
#     [-34.889662, -56.150179],
#     [-34.890155, -56.139364],
#     [-34.8998, -56.135845],
#     [-34.905783, -56.12606],
#     [-34.9017, -56.120825],
#     [-34.891845, -56.112671],
#     [-34.895576, -56.101427],
#     [-34.886635, -56.087008],
#     [-34.886846, -56.074905],
#     [-34.883115, -56.0604],
#     [-34.872201, -56.063147],
#     [-34.86537, -56.045465],
#     [-34.860651, -56.044865],
#     [-34.859876, -56.057138],
#     [-34.867764, -56.068039],
#     [-34.874102, -56.075249],
#     [-34.879524, -56.088724],
#     [-34.882551, -56.094131],
#     [-34.886142, -56.111383],
#     [-34.884593, -56.1234],
#     [-34.882059, -56.131039],
#     [-34.877482, -56.135931],
#     [-34.870651, -56.131039],
#     [-34.867975, -56.11928],
#     [-34.864384, -56.119623],
#     [-34.868327, -56.131039]
# ]

# zona_sayago = [
#     [-34.813662, -56.214123],
#     [-34.826346, -56.233177],
#     [-34.843676, -56.213264],
#     [-34.848325, -56.213264],
#     [-34.854665, -56.196098],
#     [-34.865933, -56.199017],
#     [-34.867764, -56.186829],
#     [-34.856918, -56.156616],
#     [-34.847903, -56.161766],
#     [-34.843958, -56.187687],
#     [-34.830432, -56.193352],
#     [-34.818595, -56.19215],
#     [-34.812958, -56.207771],
#     [-34.813662, -56.214123]
# ]

# zona_102 = [
#     [-34.74796, -56.106148],
#     [-34.749088, -56.085033],
#     [-34.759525, -56.09396],
#     [-34.76573, -56.091728],
#     [-34.775601, -56.08572],
#     [-34.77687, -56.053104],
#     [-34.782651, -56.055164],
#     [-34.807038, -56.079025],
#     [-34.801964, -56.091213],
#     [-34.794775, -56.098766],
#     [-34.792519, -56.107178],
#     [-34.79999, -56.109238],
#     [-34.804642, -56.124172],
#     [-34.808729, -56.132069],
#     [-34.81789, -56.132412],
#     [-34.835927, -56.136875],
#     [-34.835082, -56.146317],
#     [-34.801682, -56.14357],
#     [-34.812394, -56.152325],
#     [-34.806192, -56.167088],
#     [-34.799568, -56.160908],
#     [-34.796043, -56.170692],
#     [-34.783074, -56.158848],
#     [-34.771935, -56.160908],
#     [-34.74796, -56.106148]
# ]

# ruta_a_zona_102 = [
#     [-34.793506, -56.168118],
#     [-34.793365, -56.199875],
#     [-34.781805, -56.233177],
#     [-34.780959, -56.251545],
#     [-34.771935, -56.273346],
#     [-34.791109, -56.273689],
#     [-34.824796, -56.250343],
#     [-34.834377, -56.252747]
# ]

# ruta_a_avenida_italia = [
#     [-34.828178, -56.263046],
#     [-34.834941, -56.253433],
#     [-34.850298, -56.253262],
#     [-34.858609, -56.256866],
#     [-34.863398, -56.254292],
#     [-34.86706, -56.246052],
#     [-34.873539, -56.238842],
#     [-34.868891, -56.224079],
#     [-34.874102, -56.211891],
#     [-34.872693, -56.200905],
#     [-34.871285, -56.190948],
#     [-34.869454, -56.167088],
#     [-34.868187, -56.162796],
#     [-34.879594, -56.147346]
# ]

# ruta_a_zona_central = [
#     [-34.874947, -56.211119],
#     [-34.881566, -56.200905],
#     [-34.885368, -56.197901],
#     [-34.888818, -56.197643],
#     [-34.891774, -56.195412],
#     [-34.898533, -56.195154]
# ]

# ruta_a_sayago = [
#     [-34.823307, -56.227384],
#     [-34.818824, -56.235645],
#     [-34.823105, -56.241353],
#     [-34.825236, -56.249399]
# ]

# polyline = folium.PolyLine(locations=ruta_a_sayago, color="blue", weight=2.5)
# polyline.add_to(folium_map)
# polyline = folium.PolyLine(locations=ruta_a_zona_central, color="blue", weight=2.5)
# polyline.add_to(folium_map)
# polyline = folium.PolyLine(locations=ruta_a_avenida_italia, color="blue", weight=2.5)
# polyline.add_to(folium_map)
# polyline = folium.PolyLine(locations=ruta_a_zona_102, color="blue", weight=2.5)
# polyline.add_to(folium_map)
# polyline = folium.PolyLine(locations=zona_102, color="black", weight=2.5)
# polyline.add_to(folium_map)
# polyline = folium.PolyLine(locations=zona_sayago, color="black", weight=2.5)
# polyline.add_to(folium_map)
# polyline = folium.PolyLine(locations=zona_avenida_italia, color="black", weight=2.5)
# polyline.add_to(folium_map)
# polyline = folium.PolyLine(locations=zona_central, color="black", weight=2.5)
# polyline.add_to(folium_map)

# polilinea = folium.PolyLine(puntos, color="blue", weight=2.5, opacity=1, tooltip="Mi Polilínea")

locate_control = LocateControl()
locate_control.add_to(folium_map)
# Draw(export=True).add_to(folium_map)

folium_map.save(map_path)

inject_script_into_html()

full_map_path = os.path.abspath(map_path)
os.startfile(full_map_path)
