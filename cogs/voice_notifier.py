from print import print
from constants import constant
from discord.ext import commands
import discord
from .rooms import room_ids


class VoiceNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, old_state, new_state):
        if old_state.channel == new_state.channel:
            return

        if not new_state.channel:
            return

        new_channel_id = new_state.channel.id

        # Do not send a notification if the member is trying to create a room
        if new_channel_id == constant.create_room_channel:
            return
        
        current_rooms_ids = room_ids()

        # Do not send a notification if the room belongs to the member
        if str(new_channel_id) in current_rooms_ids and current_rooms_ids[str(new_channel_id)] == member.id:
            return

        rooms_channel = self.bot.get_channel(constant.rooms_chat)

        embed = discord.Embed(
            color=0x0059e8
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar
        )
        embed.add_field(
            name="Voice join notification",
            value=f"{member.mention} join the {new_state.channel.mention} voice channel"
        )

        await rooms_channel.send(f"<@&{constant.voice_notification_role}>", embed=embed)


async def setup(client):
    await client.add_cog(VoiceNotifier(client))