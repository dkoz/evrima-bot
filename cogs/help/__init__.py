import nextcord
from nextcord.ext import commands

class EvrimaHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def helpevrima(self, ctx):
        embed = nextcord.Embed(
            title="Evrima RCON Commands",
            description="List of available commands for the Evrima RCON.",
            color=nextcord.Color.blue()
        )

        embed.add_field(name="announce", value="Make an announcement on the server.", inline=False)
        embed.add_field(name="banplayer", value="Ban a player from the server.", inline=False)
        embed.add_field(name="kickplayer", value="Kick a player from the server.", inline=False)
        embed.add_field(name="playerlist", value="Display a list of players on the server.", inline=False)
        embed.add_field(name="saveserver", value="Save the current state of the server.", inline=False)
        embed.add_field(name="update_playables", value="Update list of allowed playables. (Experimental).", inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(EvrimaHelp(bot))