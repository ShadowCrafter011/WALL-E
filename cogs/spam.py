from discord.ext import commands
from discord import app_commands


class SpamHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="spam", description="Send a message multiple times")
    @app_commands.describe(message="Message to be sent", n="Number of times message gets sent capped to 10")
    async def spam(self, interaction, message:str, n: int):
        n = min(n, 10)
        await interaction.response.send_message(f"Sending \"{message}\" {n} times")
        for _ in range(n):
            await interaction.channel.send(message)


async def setup(client):
    await client.add_cog(SpamHandler(client))