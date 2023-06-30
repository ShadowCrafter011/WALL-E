from discord.ext import tasks, commands
from constants import constant
from print import print
import pickle
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
        with open("data/icon.p", "rb") as pickle_index:
            icon_index = pickle.loads(pickle_index.read())

        icons = list(os.listdir("data/icons"))
        guild = await self.bot.fetch_guild(constant.guild_id)

        if icon_index >= len(icons) - 1:
            icon_index = 0

        with open(os.path.join("data/icons", icons[icon_index]), "rb") as icon:
            await guild.edit(icon=icon.read())

        icon_index += 1
        
        with open("data/icon.p", "wb") as pickle_index:
            pickle_index.write(pickle.dumps(icon_index))

    
async def setup(client):
    await client.add_cog(IconHandler(client))