import os
import random

import aiohttp
import discord
from discord import ui
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

# commands.Bot is a subclass of discord.Client with
# more features and ease of use

bot = commands.Bot(
    command_prefix=">",
    intents=intents
)

async def get_random_dog_image() -> str:
    async with aiohttp.ClientSession().get('https://random.dog/woof.json') as resp:
        js = await resp.json()
        return js['url']
    
bot.get_random_dog_image = get_random_dog_image

token = os.getenv('TOKEN')

@bot.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(bot))

@bot.event
async def on_message(message: discord.Message):
    print(f'Message {message.content} by {message.author.global_name} on {message.channel.name}')

    if message.author == bot.user:
        return

    if message.channel.name == "poke-tcg":
        if message.content.lower() == ">embed":
            url = await bot.get_random_dog_image()
            # Note that when sending LayoutViews, you cannot send any content, embeds, stickers, or polls.
            await message.channel.send(view=EmbedLikeView(url=url))
            return
        
        if message.content.lower() == "hello" or message.content.lower() == "hi":
            await message.channel.send(f'Hello {message.author.global_name}')
            return
        
        elif message.content.lower() == "bye":
            await message.channel.send(f'Bye {message.author.global_name}')
            return

        elif message.content.lower() == "What are you doing":
            await message.channel.send(f'Doing backchodi')
            return

        elif message.content.lower() == "tell me a joke":
            jokes = [
                "Can someone please shed more light on how my lamp got stolen?",
                "Why is she called llene? She stands on equal legs.",
                "What do you call a gazelle in a lions territory? Denzel."
            ]
            await message.channel.send(random.choice(jokes))
            return

# This is a row of buttons that will be used in our larger LayoutView later.
# An ActionRow is similar to a View but it can only contain up to 5 buttons or 1 select menu.
# Similar to a View it can be inherited to make it easier to manage.
class EmbedChangeButtons(ui.ActionRow):
    def __init__(self, view: 'EmbedLikeView') -> None:
        self.__view = view
        super().__init__()

    @ui.button(label='New Image', style=discord.ButtonStyle.gray)
    async def new_image(self, interaction: discord.Interaction[commands.Bot], button: discord.ui.Button) -> None:
        url = await interaction.client.get_random_dog_image()
        self.__view.thumbnail.media.url = url
        await interaction.response.edit_message(view=self.__view)

    @ui.button(label='Change Text', style=discord.ButtonStyle.primary)
    async def change_text(self, interaction: discord.Interaction[commands.Bot], button: discord.ui.Button) -> None:
        await interaction.response.send_modal(ChangeTextModal(self.__view))


# This is a simple modal to allow the content of the text portion of the "embed" to be changed by the user.
class ChangeTextModal(ui.Modal, title='Change Text'):
    new_text = ui.TextInput(label='The new text', style=discord.TextStyle.long)

    def __init__(self, view: 'EmbedLikeView') -> None:
        self.__view = view
        self.new_text.default = view.random_text.content
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        self.__view.random_text.content = str(self.new_text.value)
        await interaction.response.edit_message(view=self.__view)
        self.stop()


# This defines a simple LayoutView that uses a Container to wrap its contents
# A Container is similar to an Embed, in that it has an accent colour and darkened background.
# It differs from an Embed in that it can contain other items, such as buttons, galleries, or sections, etc.
class EmbedLikeView(ui.LayoutView):
    def __init__(self, *, url: str) -> None:
        super().__init__()

        # When we want to use text somewhere, we can wrap it in a TextDisplay object so it becomes an Item.
        self.random_text = ui.TextDisplay('This is a random dog image! Press the button to change it and this text!')
        # A thumbnail is an Item that can be used to display an image as a thumbnail.
        # It needs to be wrapped inside a Section object to be used.
        # A Section is a container that can hold 3 TextDisplay and an accessory.
        # The accessory can either be a Thumbnail or a Button.
        # Since we're emulating an Embed, we will use a Thumbnail.
        self.thumbnail = ui.Thumbnail(media=url)
        self.section = ui.Section(self.random_text, accessory=self.thumbnail)
        self.buttons = EmbedChangeButtons(self)

        # Wrap all of this inside a Container
        # To visualize how this looks, you can think of it similar to this ASCII diagram:
        # +----------------------Container--------------------+
        # | +--------------------Section--------------------+ |
        # | | +----------------------------+  +-Thumbnail-+ | |
        # | | |  TextDisplay               |  | Accessory | | |
        # | | |                            |  |           | | |
        # | | |                            |  |           | | |
        # | | |                            |  |           | | |
        # | | +----------------------------+  +-----------+ | |
        # | +-----------------------------------------------+ |
        # | +------------------ActionRow--------------------+ |
        # | |+-------------+ +-------------+                | |
        # | || Button A    | | Button B    |                | |
        # | |+-------------+ +-------------+                | |
        # | +-----------------------------------------------+ |
        # +---------------------------------------------------+

        # If you want the "embed" to have multiple images you can add a MediaGallery item
        # to the container as well, which lets you have up to 10 images in a grid-like gallery.

        container = ui.Container(self.section, self.buttons)
        self.add_item(container)

bot.run(token)