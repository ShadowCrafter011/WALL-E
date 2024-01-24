# Unused atm but I can use this for reference with components

from typing import Optional
from discord.ext import commands
from discord import app_commands
from util import find_role, find_user
import discord
from discord.ui import Select
from discord import SelectOption
from types import MethodType
from print import print
from discord.utils import get


class CategorizationHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="categorize-members", description="Add unique categorizer to members")
    async def categorize_members(self, interaction):
        if interaction.user.id != interaction.guild.owner_id:
            return await interaction.response.send_message("Only the owner of the server may use this command")

        await interaction.response.send_message(view=CategorizationView(self.bot, interaction.guild))

    @app_commands.command(name="categorize-images", description="Link image to member ID")
    async def categorize_images(self, interaction):
        if interaction.user.id != interaction.guild.owner_id:
            return await interaction.response.send_message("Only the owner of the server may use this command")

        await interaction.response.send_message("WOW")


async def setup(client):
    await client.add_cog(CategorizationHandler(client))


class CategorizationView(discord.ui.View):
    def __init__(self, bot, guild, timeout=180):
        super().__init__(timeout=timeout)
        self.guild = guild
        self.bot = bot

        options = []
        for member in guild.members:
            if member.bot:
                continue

            options.append(
                SelectOption(label=member.display_name, value=member.id)
            )

        select = Select(placeholder="Select a user", options=options)
        self.add_item(select)

        select.callback = MethodType(self.handle_select, select)

    async def handle_select(self, select, interaction):
        member = await self.bot.fetch_user(select.values[0])
        await interaction.response.send_modal(NamingModal(member))


class NamingModal(discord.ui.Modal):
    def __init__(self, member):
        super().__init__(title=f"Type ID for {member.display_name}")
        self.member = member

        self.add_item(discord.ui.TextInput(
            label=f"ID for {member.display_name}"))

    async def callback(self, interaction):
        interaction.response.edit_message(self.children[0].value)
