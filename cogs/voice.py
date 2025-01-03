from discord.ext import commands
from discord import app_commands
import discord
import os
import time
import yt_dlp
import re
import json
from constants.consts import Constant



async def get_file_path(url, interaction):
    match = re.match(r"^https:\/\/www.youtube.com\/watch\?v=([\w-]+)$", url)
    video_id = match.group(1)

    if base_path := os.getenv("BASE_PATH"):
        audio_path = os.path.join(base_path, "data/audio")
    else:
        audio_path = "/home/lukas/WALL-E/data/audio"

    def return_existing_file():
        existing_file = list(filter(lambda path: path.startswith(video_id), os.listdir(audio_path)))

        if len(existing_file) > 0:
            return os.path.join(audio_path, existing_file[0])
        
    if path := return_existing_file():
        return path
    
    original_response = await interaction.original_response()
    await original_response.edit(content="Downloading audio file")

    ydl_opts = {
        "format": "bestaudio/best",  # Select the best audio format
        "postprocessors": [{
            "key": "FFmpegExtractAudio",  # Use ffmpeg to extract audio
            "preferredcodec": "mp3",  # Change to "aac", "wav", etc., for different formats
            "preferredquality": "192",  # Set the audio quality (e.g., 192kbps)
        }],
        "outtmpl": os.path.join(audio_path, f"{video_id}.%(title)s.%(ext)s"),  # Output file template
        "noplaylist": True,  # Avoid downloading playlists
    }

    with yt_dlp.YoutubeDL(ydl_opts) as dlp:
        dlp.download([video_id])

    return return_existing_file()

def play_next_queue(self):
    if base_path := os.getenv("BASE_PATH"):
        queue_path = os.path.join(base_path, "data/audio_queue.json")
    else:
        queue_path = "/home/lukas/WALL-E/data/audio_queue.json"

    with open(queue_path) as queue_file:
        queue: list = json.load(queue_file)

    if len(queue) == 0:
        return
    
    path = queue.pop(0)
    self.vc.play(discord.FFmpegPCMAudio(source=path), after=lambda _: play_next_queue(self))

    with open(queue_path, "w") as queue_file:
        json.dump(queue, queue_file)


class VoiceHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="Play the audio of a Youtube video")
    @app_commands.describe(url="Play the audio of the given URL")
    async def play(self, interaction, url: str):
        await interaction.response.send_message("Checking whether audio was already downloaded")
        path = await get_file_path(url, interaction)
        if self.vc.is_playing():
            if base_path := os.getenv("BASE_PATH"):
                queue_path = os.path.join(base_path, "data/audio_queue.json")
            else:
                queue_path = "/home/lukas/WALL-E/data/audio_queue.json"
            if not os.path.isfile(queue_path):
                with open(queue_path, "w") as queue_file:
                    json.dump([], queue_file)
            with open(queue_path) as queue_file:
                queue = json.load(queue_file)
            queue.append(path)
            with open(queue_path, "w") as queue_file:
                json.dump(queue, queue_file)
            await (await interaction.original_response()).edit(content=f"{path.split(".")[1]} wurde zur Warteschlange hinzugefügt")
        else:
            self.vc.play(discord.FFmpegPCMAudio(source=path), after=lambda _: play_next_queue(self))
            await (await interaction.original_response()).edit(content=f"Playing {path.split(".")[1]}")

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
        if base_path := os.getenv("BASE_PATH"):
            queue_path = os.path.join(base_path, "data/audio_queue.json")
        else:
            queue_path = "/home/lukas/WALL-E/data/audio_queue.json"

        with open(queue_path, "w") as queue_file:
            json.dump([], queue_file)

        await self.vc.disconnect()
        await interaction.response.send_message("WALL-E den Sprachchat verlassen")


async def setup(client):
    await client.add_cog(VoiceHandler(client))