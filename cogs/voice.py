from discord.ext import commands
from discord import app_commands
import discord
from pytube import YouTube
import os
import time


class YT(YouTube):
    def __init__(self, *args, **kwargs):
        super(YT, self).__init__(*args, **kwargs)

    async def get_file_path(self, interaction):
        existing_file = list(filter(lambda path: path.startswith(self.video_id), os.listdir("/home/lukas/WALL-E/data/audio")))

        if len(existing_file) > 0:
            return os.path.join("/home/lukas/WALL-E/data/audio", existing_file[0])
        
        original_response = await interaction.original_response()
        
        await original_response.edit(content="Downloading audio file")

        stream = sorted(self.streams.filter(only_audio=True), key=lambda stream: int(stream.abr.replace("kbps", "")), reverse=True)[0]
        filename = f"{self.video_id}-{time.time()}.webm"
        stream.download(output_path="/home/lukas/WALL-E/data/audio", filename=filename)
        return os.path.join("/home/lukas/WALL-E/data/audio", filename)


class VoiceHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="Play the audio of a Youtube video")
    @app_commands.describe(url="Play the audio of the given URL")
    async def play(self, interaction, url: str):
        yt = YT(url)
        await interaction.response.send_message("Checking whether audio was already downloaded")
        path = await yt.get_file_path(interaction)
        self.vc.play(discord.FFmpegPCMAudio(source=path))
        await (await interaction.original_response()).edit(content=f"Playing {yt.title}, at {path}")

    @app_commands.command(name="join", description="Lass WALL-E deinem Sprachchat beitreten")
    async def join(self, interaction):
        if channel := interaction.user.voice.channel:

            try:
                self.vc = await channel.connect(self_deaf=True)
            except discord.ClientException:
                return await interaction.response.send_message("WALL-E ist schon in einem Sprachchat")

            await interaction.response.send_message("WALL-E ist deinem Sprachchat beigetreten")
        else:
            await interaction.response.send_message("Du bist mit keinem Sprachchat verbunden")

    @app_commands.command(name="leave", description="Lass WALL-E den Sprachchat verlassen")
    async def leave(self, interaction):
        await self.vc.disconnect()
        await interaction.response.send_message("WALL-E den Sprachchat verlassen")


async def setup(client):
    await client.add_cog(VoiceHandler(client))