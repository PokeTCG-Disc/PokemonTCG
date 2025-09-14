import os
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from pokemon import starter_selection, number_of_pokemon_cards
from pokemon import open_a_pack, display_starter_pokemon, createCard
from view import EmbedView

load_dotenv()

intents = discord.Intents.default()
intents.members = True #to access member info
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
client = MongoClient(os.getenv('uri'), server_api=ServerApi('1'))

@bot.event
async def on_ready():
    print(f"Logged in as a bot {bot.user}")
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    username = message.author.name
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
            user_collection2 = user_database["poke_cards"]
            user_collection1 = user_database["user_info"]

            name, types, hp, sprite_url, image_url = createCard(choice)

            await message.channel.send(view=EmbedView(name, hp, types, sprite_url, image_url))

            insert_pokeInfo = {
                "name": name,
                "types": types,
                "hp": hp,
                "sprite_url": sprite_url,
                "image_url": image_url
            }

            user_collection2.insert_one(insert_pokeInfo)

            query_filter = {"number_of_poke_cards": number_of_pokemon_cards}
            update_operation = {"$set":
                {"number_of_poke_cards": number_of_pokemon_cards + 1}                    
            }

            user_collection1.update_one(query_filter, update_operation)
            
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
                    user_collection1 = user_database["user_info"]
                    
                    #add collection for trainers, items, etc

                    insert_info = {
                        "username": username,
                        "user_id": message.author.id,
                        "number_of_poke_cards": number_of_pokemon_cards
                    }
                    user_collection1.insert_one(insert_info)

                    #pick a starter pokemon
                    await display_starter_pokemon(message)

                except Exception as e:
                    print(e)

@bot.tree.command()
async def open(interaction: discord.Interaction):
    """Open a Pokémon card pack"""
    await open_a_pack(interaction, interaction.user.name)

bot.run(os.getenv('TOKEN'))
