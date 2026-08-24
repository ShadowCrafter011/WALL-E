from discord.ext import commands
from discord import app_commands
from constants import constant
from random import randint
import string
import math
import json


class GeoguessrHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="geoguessr", description="Create a new geoguessr challenge")
    async def geoguessr(self, interaction, latitude: float, longitude: float):
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return await interaction.response.send_message("The latitude or longitude provided have the wrong format. Please use a decimal number", ephemeral=True)

        geoguessr_db = GeoguessrDB()
        id = geoguessr_db.create_geoguessr_challenge(latitude, longitude)

        await interaction.channel.send(f"<@&{constant.geoguessr_role}> {interaction.user.mention} just created a new Geoguessr challenge.\n\nThe code to submit guesses is **{id}**")

        await interaction.response.send_message(f"Geoguessr challenge created with code {id}", ephemeral=True)

    @app_commands.command(name="guess", description="Guess the location of a geoguessr challenge")
    async def guess(self, interaction, code: str, latitude: float, longitude: float):
        geoguessr_db = GeoguessrDB()

        if geoguessr_db.id_unique(code):
            return await interaction.response.send_message("The code you used is invalid please check it is correct", ephemeral=True)

        distance = round(geoguessr_db.distance_to(code, latitude, longitude))
        score = round(5000 * math.exp(-10 * distance / 20_037))

        await interaction.response.send_message(f"You are {distance}km away from the correct location and get {score} points", ephemeral=True)

        if score < 5000:
            message = f"{interaction.user.mention} got a score of {score} on challenge {code}"
        else:
            message = f"**5K**!!!! {interaction.user.mention} guessed the **exact** location of challenge {code}!"
        await interaction.channel.send(message)

async def setup(client):
    await client.add_cog(GeoguessrHandler(client))


class GeoguessrDB:
    def __init__(self):
        self.db = self.read_db()

    def read_db(self):
        with open("data/geoguessr.json") as db_file:
            return json.load(db_file)

    def write_db(self):
        with open("data/geoguessr.json", "w") as db_file:
            json.dump(self.db, db_file)

    def ids(self):
        return self.db.keys()

    def id_unique(self, id):
        return id not in self.ids()

    def add_geoguessr_challenge(self, id, latitude, longitude):
        if not self.id_unique(id):
            raise ValueError("Geoguessr ID is not unique")

        self.db[id] = {
            "lat": latitude,
            "lon": longitude
        }

        self.write_db()

    def create_geoguessr_challenge(self, *coords):
        id = self.generate_unique_id()
        self.add_geoguessr_challenge(
            id,
            *coords
        )
        return id

    def generate_unique_id(self, length=4):
        characters = list(string.ascii_uppercase) + list(string.digits)
        id = ""
        while id == "" or not self.id_unique(id):
            for _ in range(length):
                id += characters[randint(0, len(characters) - 1)]
        return id

    def distance_to(self, id, latitude, longitude):
        challenge_lat = self.db[id]["lat"] * math.pi / 180
        challenge_lon = self.db[id]["lon"] * math.pi / 180
        latitude *= math.pi / 180
        longitude *= math.pi / 180

        d_lat = challenge_lat - latitude
        d_lon = challenge_lon - longitude
        sin_lat = math.sin(d_lat / 2) ** 2
        sin_lon = math.sin(d_lon / 2) ** 2
        sq = math.sqrt(sin_lat + math.cos(latitude) * math.cos(challenge_lat) * sin_lon)
        return 2 * 6371 * math.asin(sq)
