import discord
from discord import ui

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

#add buttons next to each pokemon to take to the card view. Add a button for delete option too
#we can code the delete feature later, just add the button
class EmbedViewForPokedex(ui.LayoutView):
    def __init__(self, names: list, sprite_urls: list) -> None:
        super().__init__()

        for name, sprite_url in zip(names, sprite_urls):
            title = ui.TextDisplay(f"{name}")
            thumbnail = ui.Thumbnail(media=sprite_url)
            section = ui.Section(title, accessory=thumbnail)
            separator = ui.Separator()
            self.add_item(ui.Container(section, separator))
