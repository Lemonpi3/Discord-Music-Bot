import music
import discord
from discord.ext import commands

KEY = "KEY"

cogs = [music]

client = commands.Bot(command_prefix="!",
 intents = discord.Intents.all())

for cog in cogs:
    cog.setup(client)


client.run(KEY)

