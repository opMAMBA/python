import wavelink
import discord
from discord.ext import commands
from discord.ext.commands import Context
import asyncio

async def check_author(ctx: Context):
    if ctx.author.voice is None:
        await ctx.reply("Join a voice channel first", mention_author=False)
        return False
    return True

class Music(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self,node):
        print(f"Node {node.id}is ready") 

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload : wavelink.TrackEventPayload):
        player: wavelink.Player=payload.player
        try:
            await self.bot.wait_for("wavelink_track_start", timeout=300)
        except asyncio.TimeoutError:
            await player.disconnect()


    @commands.command(aliases=["p"])
    async def play(self, ctx: Context, *args):
        """Play a song from YouTube"""
        query = " ".join(args)
        if ctx.author.voice is None:
            await ctx.reply("Join Voice chat first", mention_author=False)
            return

        if not query:
            await ctx.reply("Query is empty", mention_author=False)
            return
        player:wavelink.Player
        player = ctx.guild.voice_client or await ctx.author.voice.channel.connect(cls=wavelink.Player)

        if player.channel.id != ctx.author.voice.channel.id:
            await ctx.send("Playing already on other channel", mention_author=False)

        tracks = await wavelink.YouTubeTrack.search(query)
        if isinstance(tracks, (list)):
            if not player.is_playing():
                await player.play(tracks[0])
                embed = discord.Embed(title="Now Playing", description=f"[{tracks[0].title}]({tracks[0].uri})", color=discord.Color.blurple())
                embed.set_image(url=tracks[0].thumb)
                await ctx.reply(embed=embed, mention_author=False)
            else:
                await player.queue.put_wait(tracks[0])
                await ctx.reply(f"Queued {tracks[0].title}", mention_author=False)

        elif isinstance(tracks, wavelink.YouTubePlaylist):
            await player.queue.put_wait(tracks)
            if not player.is_playing():
                track = player.queue.get()
                await player.play(track)
                embed = discord.Embed(title="Now Playing", description=f"[{track.title}]({track.uri})", color=discord.Color.blurple())
                embed.set_image(url=track.thumb)
                await ctx.reply(embed=embed, mention_author=False)
            else:
                await ctx.reply(f"Queued Playlist ", mention_author=False)

        else:
            reply_message = "Query returned no results"
            await ctx.reply(reply_message, mention_author=False)

    @commands.command(aliases=["pa"])
    async def pause(self, ctx:Context):
        """Pause the current song"""
        check = await check_author(ctx)
        if not check:
            return
        player: wavelink.Player = ctx.guild.voice_client
        if not player.is_playing():
            await ctx.reply("Player is empty", mention_author=False)
            return
        await player.pause()
        await ctx.reply("Paused",mention_author=False)


    @commands.command(aliases=["r"])
    async def resume(self, ctx:Context):
        """Resume the current song"""
        check = await check_author(ctx)
        if not check:
            return
        player: wavelink.Player = ctx.guild.voice_client
        if player.is_playing():
            await ctx.reply("Already playing", mention_author=False)
            return
        if player is None:
            await ctx.reply("Player is empty", mention_author=False)
            return
        await player.resume()
        await ctx.reply("Resumed",mention_author=False)

    @commands.command(aliases=["s","dc"])
    async def stop(self, ctx:Context):
        """Stop the current song"""
        check = await check_author(ctx)
        if not check:
            return
        player: wavelink.Player = ctx.guild.voice_client
        if player.queue.is_empty != True:
            player.queue.clear()
        await player.disconnect()   
        await ctx.message.add_reaction("👍")

    @commands.command(aliases=["np"])
    async def now_playing(self, ctx:Context):
        """Show the current song"""
        check = await check_author(ctx)
        if not check:
            return
        player: wavelink.Player = ctx.guild.voice_client
        if not player.is_playing():
            await ctx.reply("Player is empty")
            return
        embed = discord.Embed(title="Now Playing", description=player.current.title, color=0x00ff00)
        embed.set_image(url=player.current.thumbnail)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["q"])
    async def queue(self, ctx:Context):
        """Show the current queue"""
        check = await check_author(ctx)
        if not check:
            return
        player: wavelink.Player = ctx.guild.voice_client
        if player.queue.is_empty:
            await ctx.reply("Empty Queue")
            return
        embed = discord.Embed(title="Queue", description="", color=0x00ff00)
        for i, track in enumerate(player.queue, start=1):
            embed.description += f"{i}) {track.title}\n"
        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog (Music(bot))
