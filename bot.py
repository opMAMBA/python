from discord.ext import commands
import discord
import config
import wavelink 
from cogs import EXTENSIONS

class Bot(commands.Bot):
    def __init__(self, intents: discord.Intents, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=intents, **kwargs)

    async def setup_hook(self):
        node: wavelink.Node = wavelink.Node(uri='http://n1.ll.darrennathanael.com:2269', password='glasshost1984')
        await wavelink.NodePool.connect(client=self,nodes=[node])
        for cog in EXTENSIONS:
            try:
                await self.load_extension(cog)
            except Exception as exc:
                print(f'Could not load extension {cog} due to {exc.__class__.__name__}: {exc}')

    async def on_ready(self):
        print(f'Logged on as {self.user} (ID: {self.user.id})')


intents = discord.Intents.default()
intents.message_content = True
bot = Bot(intents=intents)

# write general commands here

bot.run(config.token)
