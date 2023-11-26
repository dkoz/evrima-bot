import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
bot_prefix = os.getenv("BOT_PREFIX")

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=bot_prefix, intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}, created by koz')
    activity = nextcord.Game(name="Playing The Isle: Evrima")
    await bot.change_presence(activity=activity)

# Just an example command for now.
@bot.command()
@commands.is_owner()
async def guilds(ctx):
    guilds = bot.guilds

    response = "Guilds:\n"
    for guild in guilds:
        response += f"- {guild.name} (ID: {guild.id})\n"

    await ctx.send(response)

@guilds.error
async def guilds_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("This command is restricted to the bot owner.")

bot.run(bot_token)