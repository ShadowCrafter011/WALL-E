from discord.ext import commands
from discord import app_commands
from constants import constant


class CommandsHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(constant.admin_role_id)
    async def sync(self, ctx):
        cmds = await self.bot.tree.sync()
        await ctx.send(f"{len(cmds)} Befehle synchronisiert")

    @sync.error
    async def sync_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("Sorry, aber du darfst diesen Befehl nicht benutzen")
        
    @app_commands.command(name="ping", description="Teste den WALL-E Bot")
    async def ping(self, interaction):
        await interaction.response.send_message("Pong!")
        


async def setup(client):
    await client.add_cog(CommandsHandler(client))

    