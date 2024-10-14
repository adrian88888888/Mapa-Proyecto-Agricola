import folium
from folium import plugins
import pandas as pd
import os

def get_tuple_of_coords_from_string(string):
    # print(string)
    lat_str, lon_str = string.split(',')
    lat = float(lat_str)
    lon = float(lon_str)
    return (lat, lon)

def add_marker_from_dataframe(mapa, dataframe):
    rows, columns = dataframe.shape
    for each_row in range(rows):
        id = dataframe.iloc[each_row, id_col]
        if not pd.isna(id):
            categoria = dataframe.iloc[each_row, categoria_col]
            if categoria == 'UAM':
                continue

            coords_string = dataframe.iloc[each_row, coords_col]
            if not pd.isna(coords_string):
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
                icon = 'contact red.png'

            current_directory = 'C:\Work in Progress\Repos en GitHub\Mapa-Proyecto-Agricola\map-creator'
            icon_path = os.path.join(current_directory, 'icons', icon)
            icono_personalizado = folium.CustomIcon(icon_path, icon_size=(32, 32))

            link_wwp = 'https://wa.me/' + str(dataframe.iloc[each_row, wwp_col])

            folium.Marker(
                        location=coords,
                        popup=str(dataframe.iloc[each_row, id_col]) + '<a href=' + link_wwp + '>Abrir Chat de Wwp</a>',
                        icon=icono_personalizado
                        ).add_to(mapa)
    return mapa

def letra_a_numero(letra):
        return ord(letra.lower()) - ord('a')

id_col = letra_a_numero('A')
wwp_col = letra_a_numero('F')
coords_col = letra_a_numero('O')
frecuencia_de_compra_col = letra_a_numero('J')
categoria_col = letra_a_numero('I')

punto_de_inicio = [-34.8590, -56.2248]
zoom_inicial = [13] # un numero mas bajo corresponde a menos zoom

mapa = folium.Map(location=(punto_de_inicio), zoom_start=zoom_inicial, crs='EPSG3857') # crs='EPSG3857' es para usar el mismo sistema de coordenadas q el de google maps

database_path = r'C:\Work in Progress\Repos en GitHub\Mapa-Proyecto-Agricola\map-creator\data\from-google-sheets-clientes-database\using tsv + pandas v2\Proy Agr - 🤝Clientes.tsv'
dataframe = pd.read_csv(database_path, sep='\t')
dataframe = dataframe.drop(index=[0, 1]).reset_index(drop=True)
add_marker_from_dataframe(mapa, dataframe)
mapa.save("Mapa.html")