import os
import json
import random
from typing import Any

import discord
from discord import ui
from discord.ext import commands
from dotenv import load_dotenv
import mysql.connector
import requests

#MySQL server stuff. DO NOT SHARE THIS PLEASE

config: dict[str, Any] = {
    'user': 'srivatsav',
    'password': 'sriSQL$2025',
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'pokemontcg', 
    'raise_on_warnings': True
}

base_url: str = 'https://pokeapi.co/api/v2/'
cursor = None

load_dotenv()

intents = discord.Intents.default()
intents.members = True #to access member info
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

#---------------------------------------------------------------------------------------------------------------------

class Pokemon():
    def __init__(self, name, types) -> None:
        self.id = id
        self.name = name
        self.type = types

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

@bot.event
async def on_message(message):
    username = str(message.author).split("#")[0]
    channel = str(message.channel.name)
    user_message = str(message.content)

    print(f'Message {user_message} by {username} on {channel}')

    if message.author == bot.user:
        return

    if channel == "poke-tcg":
        # When someone types start, we add the user to the users table. 
        # If someone is already in the game, it won't store
        if user_message.lower() == "start":
            cursor = None

            #get info from SQL:
            try:
                cnx = mysql.connector.connect(**config)
                cursor = cnx.cursor()

                get_user = "SELECT user_id FROM users"
                cursor.execute(get_user)
                all_ids = cursor.fetchall() #creates a tuple list will all the user ids
                ids =[]

                for id_tuple in all_ids:
                    ids.append(id_tuple[0])

            except mysql.connector.Error:
                print("Error getting user info")
            
            finally:
                if cursor is not None:
                    cursor.close()
                if 'cnx' in locals() and cnx is not None:
                    cnx.close()

            #add info to SQL:
            if message.author.id in ids:
                await message.channel.send("You are already in the game!!")
            else:
                try:
                    cnx = mysql.connector.connect(**config)
                    cursor = cnx.cursor()

                    add_user = """INSERT INTO users (user_id, user_name) VALUES (%s, %s) AS new ON DUPLICATE KEY UPDATE user_name=new.user_name"""
                    user_data = (message.author.id, username)
                    cursor.execute(add_user, user_data)
                    cnx.commit()

                    #await message.channel.send(f"Data inserted {username}, {message.author.id}")
                    await message.channel.send(f"Welcome to the game {username}!!")

                    return message.author.id
            
                except mysql.connector.Error:
                    print("Error adding user")
            
                finally:
                    if cursor is not None:
                        cursor.close()
                    
                    if 'cnx' in locals() and cnx is not None:
                        cnx.close()

        elif user_message.lower() == "open a pack":
            pokemon_name, image_url = pick_random_kanto_pokemon()
            pokemon_data = get_pokemon(pokemon_name)
            pokemon = create_pokemon_object(pokemon_data)

            name: str = pokemon.name
            types: list[str] = [pkmn_type["type"]["name"] for pkmn_type in pokemon_data["types"]]
            hp: int = pokemon_data["stats"][0]["base_stat"]
            sprite_url: str = pokemon_data["sprites"]["front_default"]
            image_url: str = pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]

            await message.channel.send(view=EmbedView(name, hp, types, sprite_url, image_url))
            

bot.run(os.getenv('TOKEN'))