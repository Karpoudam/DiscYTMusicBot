import discord
import asyncio
from discord.ext import commands


class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.help_message = """
```
These are all my commands:
.help : Displays all available commands
.p : Plays music
.q : Displays the queue
.skip : Skips the music
.clear : Clears the queue
.leave : Disconnects the bot from the voice channel
.pause : Pauses the music
.resume : Resumes the music
.purge : Deletes the last 100 messages
```
"""
        self.text_channel_list = []

    # Initializing function
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_list.append(channel)

        await self.send_to_all(self.help_message)

    @commands.command(name="help", help="Displays all available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_list:
            await text_channel.send(msg)
