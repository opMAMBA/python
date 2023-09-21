import wavelink
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self,node):
        print(f"Node {node.id}is ready") 

    @commands.command()
    async def play(self,ctx:commands.Context,*args):
        query="".join(args)
        player:wavelink.Player 
        player=ctx.guild.voice_client or await ctx.author.voice.channel.connect(cls=wavelink.Player)

        tracks=await wavelink.YouTubeTrack.search(query) 
        if isinstance(tracks,(list)):
            if not player.is_playing():
                await player.play(tracks[0])

async def setup(bot):
    await bot.add_cog (Music(bot))
