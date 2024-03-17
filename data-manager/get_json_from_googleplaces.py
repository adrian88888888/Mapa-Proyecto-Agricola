'''
# Documentacion

1-obtener modelo con pandas
2-crear set con modelo
3-hacer grilla de requests
4-logear entrada si la id no esta repetida en el set

luego ejecutar esto para con cada categoria:
    verduleria
    agropecuaria
    agroveterinaria
    feria
    floreria
    etc(fijarse si me falta alguna)
me falta sacar la foto de cada lugar y verlas de forma facil
tambien podes buscar por tag, tenes q mirar los tags q tienen xq tienen muchos, es el dict llamado types cuando haces pprint a los resultados de la query
tambien se puede extraer informacion de horarios si le preguntas a gpt: https://chat.openai.com/share/a0713f11-db90-4f17-8aae-31718474cd00
y la informacion de trafico de un lugar: https://chat.openai.com/share/c4cc167e-15dc-495c-95e4-c74d2daaef50
me falta sacar el dato de opening hours:
    https://stackoverflow.com/questions/20735016/how-to-get-opening-hours-from-google-places-api
y el dato de la densidad de trafico de cada punto
y me faltan las ferias de la pagina de la intendencia


de google places api ahora mismo necesito:
los horarios de todo, especialente ferias
poder agregar un dia y hora en folium y q se muestren solo esos, quiza hacer una version animada si es facil
las ferias q tienen la categoria fruteria u otra parecida separarlas del resto de ferias y quedarmelas?
aun no tengo claro si todas esas ferias sirven, muchas son en momentos del año :s
agregar la posibilidad de agregarle q anda en determinadas fechas del año a cada feria?

quiza google puede trazar la ruta x mi
'''
'''
me queda extraer el dia de la semana q la feria esta abierta
me queda sacar una db para q papa la pueda usar
me queda establecer desde el mapa booleanos hacia el json
me queda calcular la ruta
usar el plugin ant para dibujar la ruta
creador de db en base a json y crear tabla: Ruta A

extras:
mejorar iconos
funcionalidades de localizacion desde chrome de andoid
mirar el resto de pliguns de folium y metodos
'''
import googlemaps
import json
import pprint
import os

def append_on_json_by_walking_on_map(start_coords, end_coords, search_terms, json_path):
    a_km_on_x = 0.008975375596399715
    a_km_on_y = 0.016008349893120055
    y = 0
    x = 1
    search_radius = 500

    # Bidimensional walk:
    current_coords = start_coords
    while current_coords[x] < end_coords[x]:
        while current_coords[y] < end_coords[y]:
            append_data_from_googleplaces_to_json_if_not_in_json(search_terms, current_coords, search_radius, json_path)

            current_coords = (current_coords[y] + a_km_on_y, current_coords[x])
        current_coords = (start_coords[y], current_coords[x])
        current_coords = (current_coords[y], current_coords[x] + a_km_on_x)

    print(f'downloaded info of {appended_places_data_count} places.')

def append_data_from_googleplaces_to_json_if_not_in_json(search_terms, search_coords, search_radius, json_path):
    global total_requests
    for search_term in search_terms:
        near_places = gmaps.places(query=search_term, location=search_coords, radius=search_radius)
        total_requests += 1
        print('+1 request por busqueda general, total_requests: ', total_requests)
        for place in near_places['results']:
            append_place_data_if_not_in_json(place, json_path, search_term)

def append_place_data_if_not_in_json(place, json_path, search_term):
    global appended_places_data_count, total_requests
    place_id = place.get('place_id')
    json_data = load_or_create_json_data(json_path)
    id_set_from_json_data = get_id_set_from_json_data(json_data)
    if place_id not in id_set_from_json_data:
        place_data = gmaps.place(place_id)
        total_requests += 1
        print('+1 request por analisis de place, total_requests: ', total_requests)
        additional_info = {
            'search_term': search_term,
        }
        place_data['result']['additional_info'] = additional_info
        json_data.append(place_data['result'])
        with open(json_path, 'w') as file:
            json.dump(json_data, file, indent=4)
        appended_places_data_count += 1
        print('+1 place added: ' + str(appended_places_data_count) + ' places, name: ' + place_data['result']['name'])

def load_or_create_json_data(json_path):
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        with open(json_path, 'w') as f:
            json.dump([], f)
        return []

def get_id_set_from_json_data(json_data):
    id_set = set()

    if not json_data or len(json_data) == 0:
        return id_set

    for place in json_data:
        if 'place_id' in place:
            id_set.add(place['place_id'])
    return id_set

api_key = 'AIzaSyAfXEWBHx6Md3IaCfjlavnV-z1GxYzYu1w'
search_terms = [
    'Verduleria',
    'Agropecuaria',
    'Feria',
    'Floreria',
]

gmaps = googlemaps.Client(key=api_key)
start_coords = (-34.935391778354024, -56.291984234152466)
end_coords = (-34.78361370488121, -56.025142425805505)
# start_coords = (-34.89372594537904, -56.18520568447019)
# end_coords = (-34.88174498110068, -56.17397026479177)
appended_places_data_count = 0
total_requests = 0
current_directory = os.getcwd()

current_directory = os.path.dirname(os.path.abspath(__file__))

json_path = current_directory + r'\json_from_googleplaces.json'
append_on_json_by_walking_on_map(start_coords, end_coords, search_terms, json_path)
print('Done!: added ' + str(appended_places_data_count) + ' places')
# requests antes de iniciar el .py: 2538
# iniciado a las 3:03:05
