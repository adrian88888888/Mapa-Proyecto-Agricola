import folium
import json
from folium.plugins import Draw, AntPath
import os
import pprint
import csv

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

ruta_a = [(-34.826575, -56.265219), (-34.829212, -56.262161), (-34.828838, -56.261609), (-34.829481, -56.260943), (-34.832678, -56.25736), (-34.832986, -56.257929), (-34.833796, -56.258841), (-34.835883, -56.255375), (-34.835963, -56.253723), (-34.836077, -56.253197), (-34.836755, -56.252156), (-34.837319, -56.251223), (-34.838032, -56.251856), (-34.853186, -56.225152), (-34.853784, -56.225753), (-34.85437, -56.226241), (-34.857816, -56.228998), (-34.858741, -56.22703), (-34.85908, -56.227427), (-34.859793, -56.228301), (-34.860466, -56.227512), (-34.859247, -56.226016), (-34.859564, -56.225436), (-34.857856, -56.223913), (-34.85713, -56.225109), (-34.854902, -56.222352), (-34.855345, -56.221563), (-34.855373, -56.221386), (-34.855347, -56.221295), (-34.85529, -56.221276), (-34.855173, -56.221303), (-34.855043, -56.22141), (-34.854407, -56.221944), (-34.854869, -56.222317), (-34.854927, -56.222277), (-34.855748, -56.220877), (-34.85691, -56.21945), (-34.860849, -56.214289), (-34.861122, -56.213828), (-34.862341, -56.211864), (-34.86257, -56.211601), (-34.863077, -56.211001), (-34.863625, -56.21058), (-34.863176, -56.209788), (-34.862696, -56.208871), (-34.863081, -56.206248), (-34.863239, -56.204671), (-34.8639, -56.202729), (-34.861488, -56.199446), (-34.860977, -56.19656), (-34.857473, -56.196506), (-34.857772, -56.194822), (-34.85794, -56.193877), (-34.858309, -56.192418), (-34.859102, -56.189994), (-34.859489, -56.189296), (-34.860026, -56.188416), (-34.861171, -56.186067), (-34.862315, -56.183749), (-34.862429, -56.183371), (-34.861494, -56.183049), (-34.862099, -56.180622), (-34.861091, -56.180244), (-34.861551, -56.178573), (-34.861639, -56.178334), (-34.862922, -56.17908), (-34.865968, -56.180316), (-34.866175, -56.178889), (-34.866435, -56.176878), (-34.866408, -56.176682), (-34.86649, -56.176591), (-34.867058, -56.176601), (-34.867161, -56.180812), (-34.868134, -56.181217), (-34.870722, -56.182247), (-34.872148, -56.182795), (-34.872852, -56.183052), (-34.87428, -56.184213), (-34.876417, -56.179576), (-34.876628, -56.179737), (-34.877825, -56.180332), (-34.879634, -56.181169), (-34.880796, -56.181727), (-34.882367, -56.182612), (-34.884422, -56.183749), (-34.886556, -56.184951), (-34.886961, -56.18516), (-34.887277, -56.184297), (-34.887299, -56.184189), (-34.887546, -56.18354), (-34.887682, -56.183165), (-34.887775, -56.182993), (-34.888439, -56.181239), (-34.889249, -56.1817), (-34.889522, -56.181561), (-34.890683, -56.181411), (-34.889944, -56.178997), (-34.890872, -56.178924), (-34.890802, -56.177744), (-34.890701, -56.176695), (-34.889733, -56.176813), (-34.889618, -56.175628), (-34.889513, -56.17463), (-34.88946, -56.171958), (-34.889038, -56.168064), (-34.892954, -56.167517), (-34.893886, -56.167495), (-34.894854, -56.167377), (-34.895884, -56.167238), (-34.895532, -56.166143), (-34.896834, -56.166047), (-34.897213, -56.167088), (-34.899677, -56.16683), (-34.899993, -56.166787), (-34.901076, -56.16668), (-34.900944, -56.164395), (-34.902246, -56.164266), (-34.901956, -56.165189), (-34.902176, -56.169105), (-34.900381, -56.169319), (-34.899562, -56.169802), (-34.899996, -56.170883), (-34.900268, -56.170692), (-34.900376, -56.170566), (-34.900979, -56.170218), (-34.901117, -56.170556), (-34.901606, -56.170242), (-34.90227, -56.170175), (-34.902574, -56.17021), (-34.906073, -56.169823), (-34.906161, -56.17095), (-34.904138, -56.171186), (-34.904243, -56.172366), (-34.90434, -56.173557), (-34.903434, -56.173632), (-34.903443, -56.172431), (-34.903355, -56.171304), (-34.901727, -56.172076), (-34.901076, -56.172473), (-34.900469, -56.171004), (-34.90112, -56.170682), (-34.90167, -56.170349), (-34.902264, -56.170301), (-34.902259, -56.172071), (-34.902211, -56.173868), (-34.901665, -56.174941), (-34.901436, -56.175156), (-34.90053, -56.175681), (-34.899615, -56.176561), (-34.899228, -56.177012), (-34.899527, -56.177752), (-34.900337, -56.177291), (-34.901093, -56.176883), (-34.902765, -56.181067), (-34.901243, -56.181968), (-34.90266, -56.185691), (-34.902774, -56.187129), (-34.902844, -56.188309), (-34.903786, -56.188213), (-34.903619, -56.186239), (-34.904564, -56.186115), (-34.904696, -56.188095), (-34.905018, -56.192601), (-34.90544, -56.198201), (-34.90449, -56.19833), (-34.904419, -56.197193), (-34.907296, -56.196892), (-34.907033, -56.193523), (-34.907965, -56.193416)]









folium.plugins.AntPath(locations=ruta_a, delay=5000, opacity=1, color='orange', weight=5, dash_array=[20, 30]).add_to(folium_map)

# folium.PolyLine(ruta_a, color='blue', weight=2.5, opacity=1).add_to(folium_map)

Draw(export=True).add_to(folium_map)
folium_map.save(map_path)
full_map_path = os.path.abspath(map_path)
os.startfile(full_map_path)
