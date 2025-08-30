import discord
import os
import random
from dotenv import load_dotenv
import json
import requests

base_url = 'https://pokeapi.co/api/v2/'

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
token = os.getenv('TOKEN')

class Pokemon():
    def __init__(self, id, name, types):
        self.id = id
        self.name = name
        self.type = types


def get_pokemon(name):
    url = f"{base_url}/pokemon/{name}"
    responce = requests.get(url)
    if responce.status_code == 200:
        pokemon_data = responce.json()
        return pokemon_data
    else:
        print(f"Error: Could not find Pokemon '{name}'. Status code: {responce.status_code}")
        return None

def create_pokemon_object(data):
    id = data['id']
    name = data['name'].capitalize()
    type_names = [t['type']['name'].capitalize() for t in data['types']]
    type_str = ', '.join(type_names)
    pokemon_object = Pokemon(id, name, type_str)
    return pokemon_object

@client.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(client))

# Function to open a pack and return a random Pokemon
def pick_random_kanto_pokemon():
    with open('kanto_pokemon.json', 'r') as p:
        data = json.load(p)
        random_pokemon = random.choice(data)
        name = random_pokemon.get('name')
    return name

@client.event
async def on_message(message):
    username = str(message.author).split("#")[0]
    channel = str(message.channel.name)
    user_message = str(message.content)

    print(f'Message {user_message} by {username} on {channel}')

    if message.author == client.user:
        return

    if channel == "poke-tcg":
        if user_message.lower() == "hello" or user_message.lower() == "hi":
            await message.channel.send(f'Hello {username}')
            return
        elif user_message.lower() == "bye":
            await message.channel.send(f'Bye {username}')
        elif user_message.lower() == "open a pack":
            pokemon_name = pick_random_kanto_pokemon()
            pokemon_data = get_pokemon(pokemon_name)
            pokemon = create_pokemon_object(pokemon_data)
            await message.channel.send(f'You got!! {pokemon.name}, Types: {pokemon.type}')


client.run(token)