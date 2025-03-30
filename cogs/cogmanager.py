import nextcord
from nextcord.ext import commands
import util.coghandler as c

class CogManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="load", description="Loads a cog.")
    @commands.is_owner()
    async def load(self, ctx, cog_name: str):
        result = await c.load_cog(self.bot, cog_name)
        await ctx.send(result)

    @commands.command(name="unload", description="Unloads a cog.")
    @commands.is_owner()
    async def unload(self, ctx, cog_name: str):
        result = await c.unload_cog(self.bot, cog_name)
        await ctx.send(result)

    @commands.command(name="reload", description="Reloads a cog.")
    @commands.is_owner()
    async def reload(self, ctx, cog_name: str):
        result = await c.reload_cog(self.bot, cog_name)
        await ctx.send(result)

def setup(bot):
    bot.add_cog(CogManager(bot))
