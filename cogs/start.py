from discord.ext import commands
from print import print


class StartHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name}")


async def setup(client):
    await client.add_cog(StartHandler(client))