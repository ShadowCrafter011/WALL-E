#!/home/lukas/WALL-E/venv/bin/python3

from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from print import print
import nest_asyncio
import discord
import asyncio
import logging
import sys
import os


async def main():
    nest_asyncio.apply()

    load_dotenv()

    intents = discord.Intents.default()
    intents.voice_states = True
    intents.message_content = True
    client = commands.Bot(intents=intents, command_prefix="!")

    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            await client.load_extension(f"cogs.{file[:-3]}")

    logging.basicConfig(stream=sys.stdout, level=logging.WARN)

    await client.start(os.getenv("DISCORD_TOKEN"))


asyncio.run(main())
