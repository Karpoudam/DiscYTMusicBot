import discord
import asyncio
from discord.ext import commands
import os

# Import cogs

from help_cog import help_cog
from music_cog import music_cog
from misc_cog import misc_cog

# Choose your prefix, here it's "."

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

# Initializing the bot


@bot.event
async def on_ready():
    await bot.add_cog(music_cog(bot))
    await bot.add_cog(help_cog(bot))
    await bot.add_cog(misc_cog(bot))

# Deactivating the base command help
bot.remove_command("help")

# Linking via token
bot.run("TOKEN")
