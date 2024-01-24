from discord import app_commands, File
from discord.ext import commands
from random import randint
import json


class ImageSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        with open("data/send_images.json") as f:
            send_images = json.loads(f.read())
            if not send_images["send_images"]:
                return

        if len(message.mentions) == 0:
            return
        
        with open("data/image_data.json") as f:
            image_data = json.loads(f.read())

        for member in message.mentions:
            user_id = str(member.id)
            if not user_id in image_data:
                continue

            images = image_data[user_id]["images"]
            image = images[randint(0, len(images) - 1)]

            with open(image, "rb") as img:
                pic = File(img)
                await message.reply(file=pic)

    @app_commands.command(name="toggle-images", description="Toggle the bot sending images on mention")
    async def toggle_images(self, interaction):
        with open("data/send_images.json") as f:
            send_images = json.loads(f.read())

        send_images["send_images"] = not send_images["send_images"]

        with open("data/send_images.json", "w") as f:
            f.write(json.dumps(send_images))

        if send_images["send_images"]:
            await interaction.response.send_message("The bot will now send images of the person mentioned")
        else:
            await interaction.response.send_message("The bot will no longer send images of mentioned people")        


async def setup(client):
    await client.add_cog(ImageSender(client))
