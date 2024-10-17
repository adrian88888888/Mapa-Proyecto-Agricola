from google.oauth2.service_account import Credentials
import gspread
import os
import pandas as pd
import numpy as np
import folium
from folium import plugins

def get_tuple_of_coords_from_string(string):
    lat_str, lon_str = string.split(',')
    lat = float(lat_str)
    lon = float(lon_str)
    return (lat, lon)

def add_client_marker_from_dataframe(folium_map, dataframe):
    rows, columns = dataframe.shape
    for each_row in range(rows):
        id = dataframe.iloc[each_row, id_col]
        if not pd.isna(id):
            if 'UAM' in id:
                continue

            coords_string = dataframe.iloc[each_row, coords_col]
            if not pd.isna(coords_string):
            	print(coords_string)
            	coords = get_tuple_of_coords_from_string(coords_string)
            	lat, lon = coords

            frecuencia_de_compra = dataframe.iloc[each_row, frecuencia_de_compra_col]
            if frecuencia_de_compra == '1-Frecuente':
                icon = 'contact green.png'
            elif frecuencia_de_compra == '2-Esporadico':
                icon = 'contact yellow.png'
            elif frecuencia_de_compra == '3-No Establecida':
                icon = 'contact gray.png'
            elif frecuencia_de_compra == '4-Muy Esporadico':
                continue
                # icon = 'contact red.png'

            current_directory = 'C:\Work in Progress\Repos en GitHub\Mapa-Proyecto-Agricola\map-creator'
            icon_path = os.path.join(current_directory, 'icons', icon)
            icono_personalizado = folium.CustomIcon(icon_path, icon_size=(32, 32))

            link_wwp = 'https://wa.me/' + str(dataframe.iloc[each_row, wwp_col])

            folium.Marker(
                        location=coords,
                        popup=str(dataframe.iloc[each_row, id_col]) + '<a href=' + link_wwp + '>Abrir Chat de Wwp</a>',
                        icon=icono_personalizado
                        ).add_to(folium_map)
    return folium_map

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

def transformar_telefono(telefono):
	if pd.isna(telefono):
		return ''
	else:
		return '+598' + telefono[:8].replace('-', '')

def get_clients_df(spreadsheet, dataframe_mapping):
	worksheet = spreadsheet.worksheet(dataframe_mapping['sheetname'])
	raw_data = worksheet.get_all_values(value_render_option='UNFORMATTED_VALUE')
	data = get_a1_notation_section_by_cropping_raw_data(raw_data, dataframe_mapping['A1_notation'])

	headers = data.pop(0)
	df = pd.DataFrame(data, columns=headers)

	df = asign_dtype_to_each_col(df, dataframe_mapping['headers_and_dtypes'])

	columnas_deseadas = ['🏷️ID', '💬WhatsApp', '🛒Frecuencia de Compra', '🗺️Coordenadas', 'Place ID']
	df = df[columnas_deseadas].copy()
	df = df.replace('', np.nan)
	df = df.dropna(subset=['🗺️Coordenadas'])
	df['💬WhatsApp'] = df['💬WhatsApp'].apply(transformar_telefono)

	return df

dataframe_mapping = {
	'sheetname' : '🤝Clientes',
    'A1_notation': 'A2:I',
    'headers_and_dtypes': {
        '🏷️ID':							'str',
        '💬Chat':						'str',
        '👤Nombre':						'str',
        '🏪Local':						'str',
        '📍Direccion':					'str',
        '💬WhatsApp':					'str',
        '🛒Frecuencia de Compra':		'str',
        '🗺️Coordenadas':				'str',
        'Place ID':						'str',
    }
}

creds = get_google_sheets_credentials()
sheet_id = '1VnMDV-mMQKzDLg0i7eU_Gv7mHsb60mGNlu0h4RJrHZ0'
spreadsheet = authenticate_and_get_spreadsheet(sheet_id, creds)
df = get_clients_df(spreadsheet, dataframe_mapping)
print(df.to_string())

id_col = 0
wwp_col = 1
frecuencia_de_compra_col = 2
coords_col = 3
place_id_col = 4

punto_de_inicio = [-34.8590, -56.2248]
zoom_inicial = [13] # un numero mas bajo corresponde a menos zoom

folium_map = folium.Map(location=(punto_de_inicio), zoom_start=zoom_inicial, crs='EPSG3857') # crs='EPSG3857' es para usar el mismo sistema de coordenadas q el de google maps
add_client_marker_from_dataframe(folium_map, df)

map_output_name = 'map.html'
repo_path = r'C:\Work in Progress\Repos en GitHub\Mapa-Proyecto-Agricola'
map_path = os.path.join(repo_path, 'map-creator', map_output_name)
folium_map.save(map_path)
full_map_path = os.path.abspath(map_path)
os.startfile(full_map_path)