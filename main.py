import os
import json
import random
from typing import Any

import discord
from discord import ui
from discord.ext import commands
from dotenv import load_dotenv
import requests

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

#MySQL server stuff. DO NOT SHARE THIS PLEASE

base_url: str = 'https://pokeapi.co/api/v2/'

load_dotenv()

intents = discord.Intents.default()
intents.members = True #to access member info
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
client = MongoClient(os.getenv('uri'), server_api=ServerApi('1'))

#---------------------------------------------------------------------------------------------------------------------

class Pokemon():
    def __init__(self, name, types) -> None:
        self.id = id
        self.name = name
        self.type = types

class EmbedView(ui.LayoutView):
    def __init__(self, name: str, hp: int, types: list[str], sprite_url: str, image_url: str) -> None:
        super().__init__()

        self.title = ui.TextDisplay(f"# You got a {name}!")
        self.hp = ui.TextDisplay(f"-# **{hp} HP**")

        types_string: str = ",".join([f"`{pkmn_type.capitalize()}`" for pkmn_type in types])
        self.types = ui.TextDisplay(f"-# Types: {types_string}")

        self.thumbnail = ui.Thumbnail(media=sprite_url)
        self.section1 = ui.Section(self.title, self.hp, self.types, accessory=self.thumbnail)

        self.separator = ui.Separator()

        self.image = ui.MediaGallery(discord.MediaGalleryItem(media=image_url))

        self.add_item(ui.Container(self.section1, self.separator, self.image))
        
class EmbedViewForSelection(ui.LayoutView):
    def __init__(self, name: str, hp: int, types: list[str], sprite_url: str) -> None:
        super().__init__()

        self.title = ui.TextDisplay(f"# You got a {name}!")
        self.hp = ui.TextDisplay(f"-# **{hp} HP**")

        types_string: str = ",".join([f"`{pkmn_type.capitalize()}`" for pkmn_type in types])
        self.types = ui.TextDisplay(f"-# Types: {types_string}")

        self.thumbnail = ui.Thumbnail(media=sprite_url)
        self.section1 = ui.Section(self.title, self.hp, self.types, accessory=self.thumbnail)

        self.separator = ui.Separator()

        self.add_item(ui.Container(self.section1, self.separator))
#----------------------------------------------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"Logged in as a bot {bot.user}")

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

async def open_a_pack(message, username):
        pokemon_name, image_url = pick_random_kanto_pokemon()
        pokemon_data = get_pokemon(pokemon_name)
        pokemon = create_pokemon_object(pokemon_data)

        name: str = pokemon.name
        types: list[str] = [pkmn_type["type"]["name"] for pkmn_type in pokemon_data["types"]]
        hp: int = pokemon_data["stats"][0]["base_stat"]
        sprite_url: str = pokemon_data["sprites"]["front_default"]
        image_url: str = pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]

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
        user_collection2.insert_one(insert_pokeInfo)


@bot.event
async def on_message(message):
    username = str(message.author).split("#")[0]
    channel = str(message.channel.name)
    user_message = str(message.content)

    print(f'Message {user_message} by {username} on {channel}')

    if message.author == bot.user:
        return


    # Handle starter selection state
    if message.author.id in starter_selection:
        choice = user_message.lower().strip()
        valid_choices = ["bulbasaur", "charmander", "squirtle"]
        if choice in valid_choices:
            # Save the user's starter choice to their collection
            user_database = client[username]
            user_collection2 = user_database["pokeCards"]
            pokemon_data = get_pokemon(choice)
            pokemon = create_pokemon_object(pokemon_data)

            name: str = pokemon.name
            types: list[str] = [pkmn_type["type"]["name"] for pkmn_type in pokemon_data["types"]]
            hp: int = pokemon_data["stats"][0]["base_stat"]
            sprite_url: str = pokemon_data["sprites"]["front_default"]
            image_url: str = pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]

            await message.channel.send(view=EmbedView(name, hp, types, sprite_url, image_url))

            insert_pokeInfo = {
                "name": name,
                "types": types,
                "hp": hp,
                "sprite_url": sprite_url,
                "image_url": image_url
            }
            user_collection2.insert_one(insert_pokeInfo)
            await message.channel.send(f"Congratulations {username}, you chose {choice.capitalize()} as your starter!")
            del starter_selection[message.author.id]
        else:
            await message.channel.send("Please type the name of your starter exactly as shown (bulbasaur, charmander, or squirtle).")
        return

    if channel == "poke-tcg":
        # When someone types start, we add the user to the users table. 
        # If someone is already in the game, it won't store
        if user_message.lower() == "start":

            user_info_databases = client["all_users"] #all_users databases already created manually 
            user_info_collection = user_info_databases["user_info"]

            result = user_info_collection.find_one({"user_id": message.author.id})

            if result:
                await message.channel.send("You are already in the game!!")
            else:
                try:
                    client.admin.command('ping')
                    print("Pinged your deployment. You successfully connected to MongoDB!")
                    #add user_name and user_id to the database
                    insert_query = {
                        "username": username,
                        "user_id": message.author.id
                    }
                    user_info_collection.insert_one(insert_query)
                    await message.channel.send(f"Welcome to Pokemon TCG {username}")

                    #create a new table for each user to store the cards they own and user stats
                    user_database = client[username]
                    #info stores name, id, number of cards owned, player level, battle #, # wins, etc
                    user_collection1 = user_database[f"{username}Info"]
                    user_collection2 = user_database["pokeCards"]
                    #add collection for trainers, items, etc

                    insert_info = {
                        "username": username,
                        "user_id": message.author.id
                    }
                    user_collection1.insert_one(insert_info)

                    #pick a starter pokemon
                    await display_starter_pokemon(message)

                except Exception as e:
                    print(e)

        elif user_message.lower() == "open a pack":
            await open_a_pack(message, username)
            

bot.run(os.getenv('TOKEN'))
