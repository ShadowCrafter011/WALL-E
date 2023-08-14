from discord.ext import commands
from constants import constant
from print import print
import asyncio
import discord
import json
from discord.utils import get


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
            asyncio.create_task(self.delete_channel(old_channel))

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

            embed = discord.Embed(
                color=0x0ac400
            )
            embed.set_author(
                name=member.display_name,
                icon_url=member.display_avatar
            )
            embed.add_field(
                name="Room creation notification",
                value=f"{member.mention} created {new_state.channel.mention}"
            )
            
            rooms_channel = self.bot.get_channel(constant.rooms_chat)
            await rooms_channel.send(f"<@&{constant.voice_notification_role}>", embed=embed)

    async def delete_channel(self, channel, sleep=5):
        await asyncio.sleep(sleep)
        if len(channel.members) > 0:
            return
        await channel.delete()

        owner_id = remove_room(channel.id)

        channel_owner = await self.bot.fetch_user(owner_id)

        embed = discord.Embed(
            color=0xd6000b
        )
        embed.set_author(
            name=channel_owner.display_name,
            icon_url=channel_owner.display_avatar
        )
        embed.add_field(
            name="Room deletion notification",
            value=f"{channel_owner.mention}'s room was automatically removed"
        )

        rooms_channel = self.bot.get_channel(constant.rooms_chat)
        await rooms_channel.send(embed=embed)


async def setup(client):
    await client.add_cog(RoomHandler(client))


# Util methods
def room_ids():
    with open("data/rooms.json") as rooms:
        return json.loads(rooms.read())

def write_data(data):
    with open("data/rooms.json", "w") as rooms:
        rooms.write(json.dumps(data))

def remove_room(room_id):
    data = room_ids()
    owner_id = data[str(room_id)]
    del data[str(room_id)]
    write_data(data)
    return owner_id


def add_room(room_id, member_id):
    data = room_ids()
    data[room_id] = member_id
    write_data(data)
    
