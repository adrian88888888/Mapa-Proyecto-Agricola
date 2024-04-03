import json
import os
import pprint

def load_or_create_json_data(json_path):
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        with open(json_path, 'w') as f:
            json.dump([], f)
        return []

def get_formatted_open_time(weekday_text):
    days_mapping = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }

    formatted_entry = []
    if not weekday_text:
        return 'Horario no Disponible'
    for entry in weekday_text:
        day, hours = entry.split(': ')
        day_es = days_mapping[day]
        if 'Closed' not in hours:
            if 'Open 24 hours' in hours:
                formatted_entry.append(f"{day_es}: Abierto las 24 horas<br>")
            else:
                formatted_entry.append(f"{day_es}: {hours}<br>")

    formatted_open_time = '\n'.join(formatted_entry)
    return formatted_open_time

def append_data(input_json_path, output_json_path):
    output_json_data = load_or_create_json_data(output_json_path)

    for place_data in load_or_create_json_data(input_json_path):
        place_id = place_data['place_id']
        if place_id not in (place['place_id'] for place in output_json_data):
            weekday_text = place_data.get('opening_hours', {}).get('weekday_text', [])
            formatted_open_time = get_formatted_open_time(weekday_text)
            additional_info = {
                'place_id': place_id,
                'formatted_open_time': formatted_open_time
            }
            output_json_data.append(additional_info)
            print(f"Added place with place_id: {place_id}")
        else:
            print(f"Place with place_id: {place_id} already exists in the JSON data.")

    with open(output_json_path, 'w') as file:
        json.dump(output_json_data, file, indent=4)

current_directory = os.path.dirname(os.path.abspath(__file__))
input_json_filename = 'json_from_googleplaces.json'
output_json_filename = 'formatted_open_time.json'
input_json_path = os.path.join(current_directory, input_json_filename)
output_json_path = os.path.join(current_directory, output_json_filename)

append_data(input_json_path, output_json_path)
