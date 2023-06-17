from ast import alias
import discord
import asyncio
from discord.ext import commands
from youtube_dl import YoutubeDL


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Initializing the values
        self.is_playing = False
        self.is_paused = False

        # Array containing the queue
        self.music_queue = []
        # Settings for the YoutubeDL object
        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
        }
        # FFMPEG settings
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = None

    # Function to search for a song on Youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" %
                                        item, download=False)['entries'][0]
            except Exception:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # Get the music url
            m_url = self.music_queue[0][0]['source']

            # Delete the first queue entry
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(
                m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # Loop to prevent infinite loop
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            # Connect to the voice channel if not already connected and if user is connected to a voice channel
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                # If connection failed
                if self.vc == None:
                    await ctx.send("Couldn't connect to the voice channel. Sorry...")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(
                m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p", "playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            # User not connected to a voice channel
            await ctx.send("You must be connected to a voice channel. Sorry...")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("An error occured... Sorry...")
            else:
                await ctx.send("Added to the queue!")
                self.music_queue.append([song, voice_channel])

                if self.is_playing == False:
                    await self.play_music(ctx)

    # Command to stop the music
    @commands.command(name="pause", help="Pauses the music")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    # Command to resume the music
    @commands.command(name="resume", aliases=["r"], help="Resumes the music")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    # Command to skip the music
    @commands.command(name="skip", aliases=["s"], help="Skips the music")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            # Musique suivante
            await self.play_music(ctx)

    # Command to display the queue
    @commands.command(name="queue", aliases=["q"], help="Displays the queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            # Affiche les 20 premiers titres de la queue
            if (i > 20):
                break
            retval += self.music_queue[i][0]['title'] + "\n" + "\n"

        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("The queue is empty! Ask me to play something!")

    # Command to clear the queue
    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("J'ai vidé ta queue, mon chat !")

    # Comand to leave the voice channel
    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kicks the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await ctx.send("In Schwarzenegger's voice : 'I'll be back!'")
        await self.vc.disconnect()
