import discord


def find_role(role_id, guild):
    return discord.utils.find(lambda r: r.id == role_id, guild.roles)
