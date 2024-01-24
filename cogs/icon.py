from discord.ext import tasks, commands
from discord import app_commands, File
from PIL import UnidentifiedImageError
from constants import constant
from random import randint
from print import print
from PIL import Image
import requests
import asyncio
import discord
import pickle
import json
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

    @app_commands.command(name="image", description="Send a random image or a random image of a user")
    @app_commands.describe(user="The user you want to get a random image of")
    async def image(self, interaction, user: discord.User = None):
        await interaction.response.defer()

        images = [os.path.join("data/icons", path) for path in os.listdir("data/icons")]

        if user:
            with open("data/image_data.json") as f:
                image_data = json.loads(f.read())
            user_id = str(user.id)
            if user_id in image_data and image_data[user_id]["images"]:
                images = image_data[user_id]["images"]
            else:
                await interaction.followup.send(
                    "Could not find any images of the user you specified"
                )

        image = images[randint(0, len(images) - 1)]
        with open(image, "rb") as img:
            pic = File(img)
            await interaction.followup.send(file=pic)

    @app_commands.command(name="images", description="Get all the images or all the images for a specific user")
    @app_commands.describe(user="The user you want to get the images of")
    async def images(self, interaction, user: discord.User = None):
        await interaction.response.send_message("Sending images now")

        images = [os.path.join("data/icons", path) for path in os.listdir("data/icons")]

        if user_images := get_user_images(user):
            images = user_images

        for image in images:
            with open(image, "rb") as img:
                pic = File(img)
                await interaction.channel.send(file=pic)
                await asyncio.sleep(1)
        await interaction.channel.send("Done")

    @app_commands.command(name="add-image", description="Add an image to the server icon cycle")
    @app_commands.describe(image_url="URL of the image to be added", user="User in the image")
    async def add_image(self, interaction, image_url: str, user: discord.User = None):
        role_admin = find_role(constant.admin_role_id, interaction.guild)
        role_imager = find_role(constant.imager_role_id, interaction.guild)
        if role_admin in interaction.user.roles or role_imager in interaction.user.roles:
            await interaction.response.defer()

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
                return await interaction.followup.send("Image URL seems to be invalid or not an image")

            # Link image with provided user
            if user:
                data_path = "data/image_data.json"
                if not os.path.isfile(data_path):
                    with open(data_path, "w") as f:
                        f.write(json.dumps({}))

                with open(data_path) as f:
                    image_data = json.loads(f.read())

                user_id = str(user.id)
                if not user_id in image_data:
                    image_data[user_id] = {
                        "display_name": user.display_name,
                        "name": user.name,
                        "images": []
                    }

                image_data[user_id]["images"].append(path)

                with open(data_path, "w") as f:
                    f.write(json.dumps(image_data))

            await interaction.followup.send("Image downloaded and added to icon cycle")
        else:
            await interaction.response.send_message(f"Sorry, you're not allowed to use this command")


def find_role(role_id, guild):
    return discord.utils.find(lambda r: r.id == role_id, guild.roles)


def get_user_images(user):
    if not user:
        return
    
    with open("data/image_data.json") as f:
        image_data = json.loads(f.read())

    user_id = str(user.id)
    if user_id in image_data and len(image_data[user_id]["images"]) > 0:
        return image_data[user_id]["images"]
    
    return None


async def setup(client):
    await client.add_cog(IconHandler(client))
