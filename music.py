import discord
from discord.ext import commands
import requests
import youtube_dl
import asyncio

class music(commands.Cog):

    def __init__(self,client):
        self.client = client
        self.queue = Queue()
        self.player = Player(client)

    @commands.command()
    async def join(self,ctx):
        
        if ctx.author.voice is None:
            await ctx.send("You are not in voice channel")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def disconect(self,ctx):
        await ctx.voice_client.disconnect()

    @commands.command()
    async def play(self,ctx,url):

        if ctx.author.voice is None:
            await ctx.send("You are not in voice channel")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            ctx.voice_client.move_to(voice_channel)

        vc = ctx.voice_client
        if not url:
            await ctx.send("Input error please see !bhelp")
            return

        await ctx.send(f"Added song to queue: {url}")
        
        self.queue.add_to_que(url)

        await self.player.set_player(ctx,self.queue)   
        
    @commands.command()
    async def skip(self,ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not in voice channel")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            ctx.voice_client.move_to(voice_channel)
        ctx.send("Skipping Song...")
        ctx.voice_client.stop()

        self.player.skip_song()
        
    @commands.command()
    async def clearqueue(self,ctx):
        await self.queue.clear_queue()
        await ctx.send("Queue cleared")

    @commands.command()
    async def clearlast(self,ctx):
        await self.queue.remove_last_added()

    @commands.command()
    async def showqueue(self,ctx):
        await ctx.send(f"{self.queue.get_queue()}")

    @commands.command()
    async def bhelp(self,ctx):
        await ctx.send("""
        Commands:
        !join / !disconnect
        * bot joins/disconect the voice channel

        !play <link/song name>
        * plays desired song, if is already playing a song it adds it to queue.
        * bot automaticaly joins the voice channel if not in.

        !skip
        * skips current song

        !clearqueue
        * clears the queue

        !clear last
        * removes last added song in the queue

        !showqueue
        * shows current queue

        """)


class Player():

    def __init__(self,client):
        self.current_song = None
        self.playing = False
        self.ctx = None
        self.queue = None
        self.client = client

    async def set_player(self,ctx,queue):
        if not self.ctx:
            self.ctx = ctx
        if not self.queue:
            self.queue = queue
        if not self.playing:
            await self.play_song()

    async def skip_song(self):
        self.play_song()

    async def play_song(self):
        try:
            song = self.queue.get_next_song()
            vc = self.ctx.voice_client
            vc.stop()

            FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn"
            }
            YDL_OPTIONS = {"format":"bestaudio"}

            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                self.playing = True

                if not song:
                    self.playing = False
                    return
                try:
                    requests.get(song)
                except:

                    info = ydl.extract_info(f"ytsearch:{song}",download = False)["entries"][0]
                    url2 = info["formats"][0]["url"]
                    source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS,executable ="../ffmpeg-2021-12-09-git-b9f4c1231f-essentials_build/bin/ffmpeg.exe")
                    await self.ctx.send(f"Playing {song}. Requested by {self.ctx.author}")
                    vc.play(source, after=self.my_after)
                    
                else:

                    info = ydl.extract_info(song,download = False)
                    url2 = info["formats"][0]["url"]
                    source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS,executable ="../ffmpeg-2021-12-09-git-b9f4c1231f-essentials_build/bin/ffmpeg.exe")
                    await self.ctx.send(f"Playing {song}. Requested by {self.ctx.author}")
                    vc.play(source, after =self.my_after)
        except Exception as e:
            print(e)
    
    def my_after(self,error):
        fut = asyncio.run_coroutine_threadsafe(self.play_song(), self.client.loop)
        try:
            fut.result()
        except:
            # an error happened sending the message
            pass


class Queue():
    def __init__(self):
        self.queue = []

    def add_to_que(self,url):
        self.queue.append(url)

    def get_next_song(self):
        if self.queue:
            return self.queue.pop(0)
        else:
            return None
    
    def clear_queue(self):
        self.queue = []

    def remove_last_added(self):
        del self.queue[-1]

    def get_queue(self):
        return self.queue

    def check_que(self):
        return

def setup(client):
    client.add_cog(music(client))
    

