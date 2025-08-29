import discord
import os
import random
from dotenv import load_dotenv
import json

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
token = os.getenv('TOKEN')

class Pokemon():
    def __init__(self, id, name, types, level):
        self.id = id
        self.name = name
        self.type = types
        self.level = level

@client.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(client))

# Function to open a pack and return a random Pokemon
def open_pack():
    with open('pokemon.json', 'r') as p:
        data = json.load(p)
        random_pokemon = random.choice(data)
        id = random_pokemon.get('id')
        name = random_pokemon.get('name')
        types = random_pokemon.get('types')
        level = random_pokemon.get('level')
        pokemon = Pokemon(id, name, types, level)
    return pokemon

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
        elif user_message.lower() == "what are you doing":
            await message.channel.send(f'Doing backchodi')
        elif user_message.lower() == "bye":
            await message.channel.send(f'Bye {username}')
        elif user_message.lower() == "open a pack":
            pokemon = open_pack()
            await message.channel.send(f'You got!! {pokemon.name}, Types: {pokemon.type}, Levle: {pokemon.level}')
        elif user_message.lower() == "tell me a joke":
            jokes = [" Can someone please shed more\
            light on how my lamp got stolen?",
                     "Why is she called llene? She\
                     stands on equal legs.",
                     "What do you call a gazelle in a \
                     lions territory? Denzel."]
            await message.channel.send(random.choice(jokes))


client.run(token)