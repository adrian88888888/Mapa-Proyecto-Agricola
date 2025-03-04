import folium
import json
from folium.plugins import Draw, AntPath, LocateControl
import os
import pprint
import csv
import polyline
import pandas as pd
import re
from google.oauth2.service_account import Credentials
import gspread
import numpy as np

# quiza esta linea te sirva en este proyecto: current_path = os.getcwd()

def get_tuple_of_coords_from_string(string):
    lat_str, lon_str = string.split(',')
    lat = float(lat_str)
    lon = float(lon_str)
    return (lat, lon)

def authenticate_and_get_spreadsheet(sheet_id, creds):
    # hecho con https://youtu.be/zCEJurLGFRk
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet

def get_google_sheets_credentials():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    if os.getenv('RUNNING_ENVIRONMENT') == 'adriano_pc':
        credentials_path = r'C:\Users\adria\Desktop\google sheets credentials for gspread.json'
        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    if os.getenv('RUNNING_ENVIRONMENT') == 'railway':
        credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FOR_GSPREAD')
        creds = Credentials.from_service_account_info(json.loads(credentials_json), scopes=scopes)
    return creds

def asign_dtype_to_each_col(df, headers_and_dtypes):
    for header, dtype in headers_and_dtypes.items():
        if dtype == 'date':
            df[header] = df[header].apply(get_date_from_time_stamp)
        elif dtype == 'float':
            df[header] = df[header].astype(float)
        elif dtype == 'str':
            df[header] = df[header].astype(str)
    return df

def get_a1_notation_section_by_cropping_raw_data(data, a1_notation):
    start_cell, end_cell = a1_notation.split(':')
    end_cell = end_cell + str(len(data))
    start_row, start_col = gspread.utils.a1_to_rowcol(start_cell)
    end_row, end_col = gspread.utils.a1_to_rowcol(end_cell)
    
    start_row -= 1
    end_row -= 1
    start_col -= 1
    end_col -= 1

    cropped_data = []
    for row in data[start_row:end_row + 1]:
        cropped_row = row[start_col:end_col + 1]
        cropped_data.append(cropped_row)

    return cropped_data

def get_clients_df(spreadsheet, dataframe_mapping):
    worksheet = spreadsheet.worksheet(dataframe_mapping['sheetname'])
    raw_data = worksheet.get_all_values(value_render_option='UNFORMATTED_VALUE')
    data = get_a1_notation_section_by_cropping_raw_data(raw_data, dataframe_mapping['A1_notation'])

    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)

    df = asign_dtype_to_each_col(df, dataframe_mapping['headers_and_dtypes'])

    columnas_deseadas = ['🏷️ID', '💬Wpp', '🗺️Coordenadas']
    df = df[columnas_deseadas].copy()
    df = df.replace('', np.nan)
    df = df.dropna(how='all')
    df = df.replace(np.nan, '')
    df['💬Wpp'] = df['💬Wpp'].apply(format_phone_number)
    # print(df.to_string())

    return df

def get_formatted_open_time(place_id, formatted_open_time):
    for place in formatted_open_time:
        if place['place_id'] == place_id:
            return place['formatted_open_time']

def load_single_col_tsv_into_set(file):
    with open(file, 'r', newline='') as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter='\t')
        first_column_set = {row[0] for row in tsvreader}
    return first_column_set

def add_markers_from_clients_df(dataframe, folium_map):
    rows, columns = dataframe.shape
    for each_row in range(rows):
        id = dataframe.iloc[each_row, id_col]
        if id:
            if 'UAM' in id:
                continue

            coords_string = dataframe.iloc[each_row, coords_col]
            if coords_string:
                coords = get_tuple_of_coords_from_string(coords_string)
                if coords:
                    lat, lon = coords
                    lat = round(lat, 7)
                    lon = round(lon, 7)
            
                    icon = 'contact green.png'
                    current_directory = r'C:\Work in Progress\Repos en GitHub\Mapa-Proyecto-Agricola\map-creator'
                    icon_path = os.path.join(current_directory, 'icons', icon)
                    icono_personalizado = folium.CustomIcon(icon_path, icon_size=(starting_icon_size))

                    # phone_number = str(dataframe.iloc[each_row, wwp_col])
                    # if phone_number:
                    #     link_wwp = 'https://wa.me/' + phone_number
                    #     popup_content = str(dataframe.iloc[each_row, id_col]) + '<br>' + '<a href=' + link_wwp + '>Abrir Chat 💬</a>'
                    # else:
                    #     popup_content = str(dataframe.iloc[each_row, id_col])
                    google_maps_nav_link = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
                    popup_content = str(dataframe.iloc[each_row, id_col])
                    popup_content += f'<br><a href="{google_maps_nav_link}" target="_blank">🚚 Obtener Indicaciones</a>'
                    popup = folium.Popup(popup_content, max_width=300)

                    folium.Marker(
                                location=coords,
                                popup=popup_content,
                                icon=icono_personalizado
                                ).add_to(folium_map)
    return folium_map

def format_phone_number(phone_number):
    if phone_number == '':
        return ''
    else:
        return '598' + phone_number[:8].replace('-', '')

def add_markers_from_google_maps(google_maps_json_data, clients_df, json_of_formatted_open_time, folium_map):
    for place in google_maps_json_data:
        name = place['name']
        place_id = place['place_id']
        lat = place['geometry']['location']['lat']
        lng = place['geometry']['location']['lng']
        lat = round(lat, 7)
        lng = round(lng, 7)
        link_to_place = place['url']
        resenias = place.get('user_ratings_total', 0)
        estrellas = place.get('rating')
        search_term = place['additional_info']['search_term']
        formatted_open_time = get_formatted_open_time(place_id, json_of_formatted_open_time)
        google_place_coords = str(lat) + ', ' + str(lng)
        
        if is_in_serie(google_place_coords, clients_df['🗺️Coordenadas']):
            continue
        if google_place_coords in coordenadas_dadas_de_baja_por_cualquier_motivo:
            # icon_name = 'cancel.png'
            continue
        else:
            if search_term == "Verduleria":
                # icon_name = 'verduleria.png'
                continue
            elif search_term == 'Agropecuaria':
                icon_name = 'agropecuaria.png'
            elif search_term == 'Floreria':
                icon_name = 'floreria.png'
            elif search_term == 'Feria':
                # continue
                icon_name = 'feria.png'
            elif search_term == 'Vivero':
                icon_name = 'vivero.png'
            else:
                icon_name = 'no-icon.png'

        icon_path = repo_path + r'\map-creator\icons\\' + icon_name
        icono_personalizado = folium.CustomIcon(icon_path, icon_size=starting_icon_size)

        # wpp_message_borrar_punto = 'https://wa.me/+59895930076?text=Adriano, borra este punto: ' + place_id
        # wpp_message_marcar_punto_como_cliente = 'https://wa.me/+59895930076?text=Adriano, este punto ahora es cliente: ' + place_id

        coords = f"{lat}, {lng}"

        google_maps_link = f"https://www.google.com/maps?q={lat},{lng}"
        google_maps_nav_link = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"

        popup = (
            'Nombre: <br>' + name + '<br><br>' +
            '<a href="#" onclick="navigator.clipboard.writeText(\'' + coords + '\'); return false;">✂️ Copiar Coordenadas</a>' + 
            '<br><br>' +
            '<a href="' + google_maps_link + '" target="_blank">🗺️ Abrir en Google Maps</a>' + 
            '<br><br>' +
            '<a href="' + google_maps_nav_link + '" target="_blank">🚚 Obtener Indicaciones</a>' +
            '<br><br>' +
            '📝 Reseñas: ' + str(resenias) + '<br><br>' +
            '⭐ Estrellas: ' + str(estrellas) + '<br><br>' +
            '🕙 Horarios:<br>' + str(formatted_open_time) + '<br>'
            # '⚙️ Id: <br>' + place_id + '<br><br>'
        )

        # version vieja q puede servir:
        # wpp_message_borrar_punto = 'https://wa.me/+59895930076?text=Adriano, borra este punto: ' + place_id
        # wpp_message_marcar_punto_como_cliente = 'https://wa.me/+59895930076?text=Adriano, este punto ahora es cliente: ' + place_id

        # popup = (
        #     'Nombre: <br>' + name + '<br><br>' +
        #     '<a href="' + wpp_message_borrar_punto + '" target="_blank">🗑️Borrar punto</a>' + 
        #     '<br><br>' +
        #     '<a href="' + wpp_message_marcar_punto_como_cliente + '" target="_blank">➕Marcar punto como cliente</a>' + 
        #     '<br><br>' +
        #     '<a href="' + link_to_place + '" target="_blank">🗺️Abrir en Google Maps</a>' + 
        #     '<br><br>' +
        #     '📝Reseñas: ' + str(resenias) + '<br><br>' +
        #     '⭐Estrellas: ' + str(estrellas) + '<br><br>' +
        #     '🕙Horarios:<br>' + str(formatted_open_time) + '<br>' +
        #     '⚙️Id: <br>' + place_id + '<br><br>'
        # )

        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup, max_width=3000),
            icon=icono_personalizado
            ).add_to(folium_map)
    
    return folium_map

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

def is_in_serie(search_term, serie):
    return serie.apply(lambda lista: search_term in lista).any()


clients_dataframe_mapping = {
    'sheetname' : '🤝Clientes',
    'A1_notation': 'B2:G',
    'headers_and_dtypes': {
        '🏷️ID':              'str',
        '👤Nombre':                     'str',
        '🏪Local':                      'str',
        '📍Direccion':                   'str',
        '💬Wpp':                        'str',
        '🗺️Coordenadas':                'str',
    }
}
sheet_id = '1E0plKQ7NhWHtP569QY6ksjLQXrHXKyBqfJUPn3Iw38o'
map_filename = 'map.html'
repo_path = r'C:\Work in Progress\Repos en GitHub\Mapa-Proyecto-Agricola'
map_path = os.path.join(repo_path, 'map-creator', map_filename)
data_from_googleplaces_path                         = repo_path + r'\map-creator\data\from-google-places\json_from_googleplaces.json'
formatted_open_time_path                            = repo_path + r'\map-creator\data\from-google-places\formatted_open_time.json'
coordenadas_dadas_de_baja_por_cualquier_motivo_path = repo_path + r'\map-creator\data\coordenadas_dadas_de_baja_por_cualquier_motivo.tsv'
nelson_icon_path    = repo_path + r'\map-creator\icons\nelson.png'
uam_icon_path       = repo_path + r'\map-creator\icons\uam.png'

with open(data_from_googleplaces_path, 'r') as file:
    google_maps_json_data = json.load(file)

with open(formatted_open_time_path, 'r') as file:
    json_of_formatted_open_time = json.load(file)

coordenadas_dadas_de_baja_por_cualquier_motivo = load_single_col_tsv_into_set(coordenadas_dadas_de_baja_por_cualquier_motivo_path)

starting_zoom = 12
starting_icon_size = (10, 10)
coords_plaza_ejercito = (-34.86304757940927, -56.169061198494575)
starting_location = coords_plaza_ejercito

folium_map = folium.Map(
    location=starting_location, 
    zoom_start=starting_zoom, 
    crs='EPSG3857' # crs='EPSG3857' es para usar el mismo sistema de coordenadas q el de google maps
    )

nelson = [-34.8265, -56.2651]
uam = [-34.8192, -56.2639]

folium.Marker(
    location=nelson,
    popup="Nelson",
    icon=folium.CustomIcon(nelson_icon_path, icon_size=starting_icon_size),
    ).add_to(folium_map)

folium.Marker(
    location=uam,
    popup="UAM",
    icon=folium.CustomIcon(uam_icon_path, icon_size=starting_icon_size),
    ).add_to(folium_map)

credentials = get_google_sheets_credentials()
spreadsheet = authenticate_and_get_spreadsheet(sheet_id, credentials)
clients_df = get_clients_df(spreadsheet, clients_dataframe_mapping)
# suppliers_df = get_suppliers_df(spreadsheet, suppliers_dataframe_mapping)

id_col = 0
wwp_col = 1
coords_col = 2

folium_map = add_markers_from_google_maps(google_maps_json_data, clients_df, json_of_formatted_open_time, folium_map)
folium_map = add_markers_from_clients_df(clients_df, folium_map)

locate_control = LocateControl()
locate_control.add_to(folium_map)
Draw(export=True).add_to(folium_map) # ===>>> descomentar para rayar el mapa

folium_map.save(map_path)

inject_script_into_html()

full_map_path = os.path.abspath(map_path)
os.startfile(full_map_path)
