import discord
import asyncio
from discord.ext import commands
from youtube_dl import YoutubeDL


# Creating the misc_cog class


class misc_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Removing the last 100 messages
    @commands.command()
    async def purge(self, ctx, amount=100):
        await ctx.channel.purge(limit=amount)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        # Ignore les changements de channel autre que ceux du bot
        if not member.id == self.bot.user.id:
            return

        # Ignore les changements de channel initiés par un "disconnect"
        elif before.channel is not None:
            return

        # Checks if the bot is playing music
        else:
            voice = after.channel.guild.voice_client
            while True:
                await asyncio.sleep(300)

                # If the bot hasn't played music for 5 minutes, it disconnects
                if voice.is_playing() == False:
                    await voice.disconnect()
                    break
