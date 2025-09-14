import os
import json
import random
import requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from view import EmbedView, EmbedViewForSelection

from dotenv import load_dotenv

load_dotenv()

base_url: str = 'https://pokeapi.co/api/v2/'
client = MongoClient(os.getenv('uri'), server_api=ServerApi('1'))

class Pokemon():
    def __init__(self, name, types) -> None:
        self.id = id
        self.name = name
        self.type = types

def pick_random_kanto_pokemon() -> tuple[str, str]:
    """
    Pick a random Pokemon and return its name and image URL
    """
    with open('kanto_pokemon.json', 'r') as p:
        data = json.load(p)
        random_pokemon = random.choice(data)
        name: str = random_pokemon.get('name')
        image_url: str = random_pokemon.get('url')
    return name, image_url

def get_pokemon(name):
    url = f"{base_url}/pokemon/{name}"
    response = requests.get(url)

    if response.status_code == 200:
        pokemon_data = response.json()
        return pokemon_data
    else:
        print(f"Error: Could not find Pokemon '{name}'. Status code: {response.status_code}")
        return None
    
def create_pokemon_object(data) -> Pokemon:
    name: str = data['name'].capitalize()
    type_names: list[str] = [t['type']['name'].capitalize() for t in data['types']]
    type_str: str = ', '.join(type_names)
    pokemon_object: Pokemon = Pokemon(name, type_str)
    return pokemon_object

def createCard(pokemon_name) -> tuple[str, str, int, str, str]:
    pokemon_data = get_pokemon(pokemon_name)
    pokemon = create_pokemon_object(pokemon_data)

    name: str = pokemon.name
    types: list[str] = [pkmn_type["type"]["name"] for pkmn_type in pokemon_data["types"]]
    hp: int = pokemon_data["stats"][0]["base_stat"]
    sprite_url: str = pokemon_data["sprites"]["front_default"]
    image_url: str = pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]

    return name, types, hp, sprite_url, image_url

async def open_a_pack(message, username):
    pokemon_name, image_url = pick_random_kanto_pokemon()

    name, types, hp, sprite_url, image_url = createCard(pokemon_name)

    await message.channel.send(view=EmbedView(name, hp, types, sprite_url, image_url))

    user_database = client[username]
    user_collection2 = user_database["pokeCards"]

    insert_pokeInfo = {
        "name": name,
        "types": types,
        "hp": hp,
        "sprite_url": sprite_url,
        "image_url": image_url
    }
    try:
        result = user_collection2.insert_one(insert_pokeInfo)
        print(f"Inserted card for {username}: {result.inserted_id}")
    except Exception as e:
        print(f"Failed to insert card for {username}: {e}")

# Global dictionary to track users picking a starter
starter_selection = {}

async def display_starter_pokemon(message):
    names = ["bulbasaur", "charmander", "squirtle"]
    for name in names:
        pokemon_name = get_pokemon(name)
        pokemon_object = create_pokemon_object(pokemon_name)

        name_str: str = pokemon_object.name
        types: list[str] = [pkmn_type["type"]["name"] for pkmn_type in pokemon_name["types"]]
        hp: int = pokemon_name["stats"][0]["base_stat"]
        sprite_url: str = pokemon_name["sprites"]["front_default"]

        await message.channel.send(view=EmbedViewForSelection(name_str, hp, types, sprite_url))
    await message.channel.send("Pick your starter Pokemon!!")
    # Add user to starter selection state
    starter_selection[message.author.id] = True
