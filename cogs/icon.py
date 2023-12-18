from discord.ext import tasks, commands
from discord import app_commands, File
from PIL import UnidentifiedImageError
from constants import constant
from random import randint
from print import print
from PIL import Image
import requests
import discord
import pickle
import uuid
import os


class IconHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.changer.start()

    def cog_unload(self):
        self.changer.cancel()

    @tasks.loop(hours=24.0)
    async def changer(self):
        if os.path.exists("data/icon.p"):
            with open("data/icon.p", "rb") as pickle_index:
                icon_index = pickle.loads(pickle_index.read())
        else:
            icon_index = 0

        icons = list(os.listdir("data/icons"))
        guild = await self.bot.fetch_guild(constant.guild_id)

        if icon_index >= len(icons) - 1:
            icon_index = 0

        with open(os.path.join("data/icons", icons[icon_index]), "rb") as icon:
            await guild.edit(icon=icon.read())

        icon_index += 1
        
        with open("data/icon.p", "wb") as pickle_index:
            pickle_index.write(pickle.dumps(icon_index))

    @app_commands.command(name="image", description="Send a random image also used as server icon")
    async def image(self, interaction):
        images = os.listdir("data/icons")
        image = images[randint(0, len(images) - 1)]
        with open(os.path.join("data/icons", image), "rb") as img:
            pic = File(img)
            await interaction.response.send_message(file=pic)

    @app_commands.command(name="add-image", description="Add an image to the server icon cycle")
    @app_commands.describe(image_url="URL of the image to be added")
    async def add_image(self, interaction, image_url: str):
        role_admin = find_role(constant.admin_role_id, interaction.guild)
        role_imager = find_role(constant.imager_role_id, interaction.guild)
        if role_admin in interaction.user.roles or role_imager in interaction.user.roles:
            img_data = requests.get(image_url).content
            file_name = f"{uuid.uuid4()}.jpg"
            path = os.path.join("data/icons", file_name)
            with open(path, "wb") as image:
                image.write(img_data)
            try:
                with Image.open(path) as im:
                    im.verify()
            except UnidentifiedImageError:
                os.remove(path)
                return await interaction.response.send_message("Image URL seems to be invalid or not an image")

            await interaction.response.send_message("Image downloaded and added to icon cycle")
        else:
            await interaction.response.send_message(f"Sorry, you're not allowed to use this command")


def find_role(role_id, guild):
    return discord.utils.find(lambda r: r.id == role_id, guild.roles)

async def setup(client):
    await client.add_cog(IconHandler(client))