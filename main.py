import nextcord
from nextcord.ext import commands
import os
import config

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=config.BOT_PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}, created by KoZ')
    activity = nextcord.Game(name="Playing The Isle: Evrima")
    await bot.change_presence(activity=activity)

for folder in os.listdir("cogs"):
    bot.load_extension(f"cogs.{folder}")

# Just an example command for now.
@bot.command(description="Shows list of guilds the bot is in.", hidden=True)
@commands.is_owner()
async def guilds(ctx):
    guilds = bot.guilds

    embed = nextcord.Embed(title="Guilds", description="List of Guilds", color=nextcord.Color.blue())
    for guild in guilds:
        embed.add_field(name=guild.name, value=f"ID: {guild.id}", inline=False)
    
    embed.set_footer(text="Created by KoZ")

    await ctx.send(embed=embed)

@guilds.error
async def guilds_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("This command is restricted to the bot owner.")

if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)