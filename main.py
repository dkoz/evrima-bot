import nextcord
from nextcord.ext import commands
import util.config as config
import util.errorhandling as e
import util.coghandler as c
import asyncio

e.setup_logging()
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=config.BOT_PREFIX, intents=intents, help_command=None, default_guild_ids=config.DEFAULT_GUILDS)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}, created by KoZ")
    print(f"Servers: {len(bot.guilds)} | Users: {len(bot.users)}")
    print(f"Invite: {nextcord.utils.oauth_url(bot.user.id)}")

@bot.event
async def on_guild_join(guild):
    print(f"Joined guild: {guild.name} (ID: {guild.id})")

@bot.event
async def on_guild_remove(guild):
    print(f"Left guild: {guild.name} (ID: {guild.id})")

@bot.event
async def on_application_command_error(interaction, error):
    await e.handle_errors(interaction, error)

async def main():
    await c.load_cogs(bot)
    await bot.start(config.BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
