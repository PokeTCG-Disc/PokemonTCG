import requests

base_url = 'https://pokeapi.co/api/v2/'

def get_pokemon(name):
    url = f"{base_url}/pokemon/{name}"
    responce = requests.get(url)
    if responce.status_code == 200:
        pokemon_data = responce.json()
        return pokemon_data
    else:
        print(f"Error: Could not find Pokemon '{name}'. Status code: {responce.status_code}")
        return None

def print_pokemon(data):
    name = data['name'].capitalize()
    type_names = [t['type']['name'].capitalize() for t in data['types']]
    type_str = ', '.join(type_names)
    pokemon_info = f"Name: {name}, Type: {type_str}"
    return pokemon_info


poke_name = input("Type a pokemon name: ")
poke_data = get_pokemon(poke_name)
if poke_data:
    info = print_pokemon(poke_data)
    print(info)
