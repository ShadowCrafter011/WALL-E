from discord.ext import commands
from discord import app_commands
import discord


class VoiceHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="join", description="Lass WALL-E deinem Sprachchat beitreten")
    async def join(self, interaction):
        if channel := interaction.user.voice.channel:

            try:
                vc = await channel.connect()
            except discord.ClientException:
                return await interaction.response.send_message("WALL-E ist schon in einem Sprachchat")
            
            vc.play(discord.FFmpegPCMAudio(source="data/sounds/rick.mp3"))

            await interaction.response.send_message("WALL-E ist deinem Sprachchat beigetreten")
        else:
            await interaction.response.send_message("Du bist in keinem Sprachchat drinnen")

    @app_commands.command(name="leave", description="Lass WALL-E den Sprachchat verlassen")
    async def leave(self, interaction):
        for voice in self.bot.voice_clients:
            await voice.disconnect()
        await interaction.response.send_message("WALL-E hat alle Sprachchats verlassen")


async def setup(client):
    await client.add_cog(VoiceHandler(client))