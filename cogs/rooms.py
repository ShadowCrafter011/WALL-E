from discord.ext import commands
from constants import constant
from print import print
import asyncio
import discord
import json


class RoomHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Delete empty rooms on startup
        for room_id in room_ids().keys():

            try:
                room = self.bot.get_channel(int(room_id))
            except discord.errors.NotFound:
                remove_room(room_id)
            
            if isinstance(room, discord.VoiceChannel) and len(room.members) == 0:
                remove_room(room_id)
                await room.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, old_state, new_state):
        guild = member.guild
        old_channel = old_state.channel
        new_channel = new_state.channel

        # Handle room deletion
        if old_channel and len(old_channel.members) == 0 and str(old_channel.id) in room_ids():
            asyncio.create_task(delete_channel(old_channel))

        # Handle room creation
        if new_channel and new_channel.id == constant.create_room_channel:
            category = discord.utils.get(guild.categories, id=constant.voice_category)

            # Move member to his room if he already has one
            rooms = room_ids()
            if member.id in rooms.values():
                channel_id = list(rooms.keys())[list(rooms.values()).index(member.id)]
                room = self.bot.get_channel(int(channel_id))
                await member.move_to(room)
                return

            created_room = await guild.create_voice_channel(
                f"☕│{member.display_name}'s Raum",
                category=category,
                position=0
            )

            add_room(created_room.id, member.id)
            await member.move_to(created_room)


async def setup(client):
    await client.add_cog(RoomHandler(client))


# Util methods
async def delete_channel(channel, sleep=5):
    await asyncio.sleep(sleep)
    if len(channel.members) > 0:
        return
    await channel.delete()
    remove_room(channel.id)

def room_ids():
    with open("data/rooms.json") as rooms:
        return json.loads(rooms.read())

def write_data(data):
    with open("data/rooms.json", "w") as rooms:
        rooms.write(json.dumps(data))

def remove_room(room_id):
    data = room_ids()
    del data[str(room_id)]
    write_data(data)


def add_room(room_id, member_id):
    data = room_ids()
    data[room_id] = member_id
    write_data(data)
    
