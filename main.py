import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv
import json
import requests
import mysql.connector

#MySQL server stuff. DO NOT SHARE THIS PLEASE
config = {
    'user': 'root',
    'password': 'sriSQL$2025',
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'pokemontcg', 
    'raise_on_warnings': True
}
cursor = None

base_url = 'https://pokeapi.co/api/v2/'
load_dotenv()
intents = discord.Intents.default()
intents.members = True #to access member info
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
#client = discord.Client(intents=intents)
token = os.getenv('TOKEN')


#---------------------------------------------------------------------------------------------------------------------

class Pokemon():
    def __init__(self, name, types):
        self.id = id
        self.name = name
        self.type = types

#----------------------------------------------------------------------------------------------------------------

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
    name = data['name'].capitalize()
    type_names = [t['type']['name'].capitalize() for t in data['types']]
    type_str = ', '.join(type_names)
    pokemon_object = Pokemon(name, type_str)
    return pokemon_object

@bot.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(bot))


# Function to open a pack and return a random Pokemon
def pick_random_kanto_pokemon():
    with open('kanto_pokemon.json', 'r') as p:
        data = json.load(p)
        random_pokemon = random.choice(data)
        name = random_pokemon.get('name')
        image_url = random_pokemon.get('url')
    return name, image_url

@bot.event
async def on_message(message):
    username = str(message.author).split("#")[0]
    channel = str(message.channel.name)
    user_message = str(message.content)

    print(f'Message {user_message} by {username} on {channel}')

    if message.author == bot.user:
        return

    if channel == "poke-tcg":
        #when someone types start, we add the user to the users table
        if user_message.lower() == "start":
            #add smth where if the user types start but they are already stores in the database
            #print you have already entered the game
            try:
                cnx = mysql.connector.connect(**config)
                cursor = cnx.cursor()
                add_user = """INSERT INTO users (user_id, user_name) VALUES (%s, %s) AS new ON DUPLICATE KEY UPDATE user_name=new.user_name"""
                user_data = (message.author.id, username)
                cursor.execute(add_user, user_data)
                cnx.commit()
                await message.channel.send(f"Data inserted {username}, {message.author.id}")

            except mysql.connector.Error as err:
                print("Error: {}".format(err))
            finally:
                if cursor is not None:
                    cursor.close()
                if 'cnx' in locals() and cnx is not None:
                    cnx.close()

            await message.channel.send(f'Welcome to Pokemon TCG {username}!!')
            return
        
        elif user_message.lower() == "open a pack":
            pokemon_name, image_url = pick_random_kanto_pokemon()
            pokemon_data = get_pokemon(pokemon_name)
            pokemon = create_pokemon_object(pokemon_data)
            await message.channel.send(f'You got!! {pokemon.name}, Types: {pokemon.type}')


bot.run(token)