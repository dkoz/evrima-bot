import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_PREFIX = os.getenv("BOT_PREFIX")
RCON_HOST = os.getenv("RCON_HOST")
RCON_PORT = int(os.getenv("RCON_PORT"))
RCON_PASS = os.getenv("RCON_PASS")
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}, created by koz')
    activity = nextcord.Game(name="Playing The Isle: Evrima")
    await bot.change_presence(activity=activity)

for folder in os.listdir("cogs"):
    bot.load_extension(f"cogs.{folder}")

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

if __name__ == "__main__":
    bot.run(BOT_TOKEN)