import nextcord
from nextcord.ext import commands, tasks
from util.config import RCON_HOST, RCON_PORT, RCON_PASS
import util.constants as c
from gamercon_async import EvrimaRCON
from util.functions import saveserverinfo, loadserverinfo
import pytz
import datetime
import re
import logging

class EvrimaMonitorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rcon_host = RCON_HOST
        self.rcon_port = RCON_PORT
        self.rcon_password = RCON_PASS
        self.update_server_info.start()
        self.update_bot_activity.start()

    def create_embed(self, server_info):
        embed_timestamp = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone('US/Central')).strftime('%m/%d/%Y %H:%M %Z')
        embed = nextcord.Embed(title=server_info.get("ServerDetailsServerName", "N/A"), color=nextcord.Color.blurple())
        embed.add_field(name="Players", value=f"{server_info.get('ServerCurrentPlayers', 0)}/{server_info.get('ServerMaxPlayers', 0)}", inline=False)
        embed.add_field(name="Map", value=server_info.get("ServerMap", "N/A"), inline=False)
        embed.add_field(name="Day Length", value=f"{server_info.get('ServerDayLengthMinutes', 0)} minutes", inline=False)
        embed.add_field(name="Night Length", value=f"{server_info.get('ServerNightLengthMinutes', 0)} minutes", inline=False)
        embed.set_thumbnail(url=c.BOT_ICON)
        embed.set_footer(text=f"{c.BOT_TEXT} {c.BOT_VERSION} • Updated: {embed_timestamp}", icon_url=c.BOT_ICON)
        
        return embed

    async def get_server_info(self):
        try:
            rcon = EvrimaRCON(self.rcon_host, self.rcon_port, self.rcon_password)
            await rcon.connect()
            command = b'\x02' + b'\x12' + b'\x00'
            response = await rcon.send_command(command)

            # This regex pattern is used to extract the rcon response into a dictionary.
            # Not really using all of it but just making sure I extracted it.
            pattern = (
                r"ServerDetailsServerName:\s*(.*?), "
                r"ServerPassword:\s*(.*?), "
                r"ServerMap:\s*(.*?), "
                r"ServerMaxPlayers:\s*(-?\d+), "
                r"ServerCurrentPlayers:\s*(-?\d+), "
                r"bEnableMutations:\s*(true|false), "
                r"bEnableHumans:\s*(true|false), "
                r"bServerPassword:\s*(true|false), "
                r"bQueueEnabled:\s*(true|false), "
                r"bServerWhitelist:\s*(true|false), "
                r"bSpawnAI:\s*(true|false), "
                r"bAllowRecordingReplay:\s*(true|false), "
                r"bUseRegionSpawning:\s*(true|false), "
                r"bUseRegionSpawnCooldown:\s*(true|false), "
                r"RegionSpawnCooldownTimeSeconds:\s*(-?\d+), "
                r"ServerDayLengthMinutes:\s*(-?\d+), "
                r"ServerNightLengthMinutes:\s*(-?\d+), "
                r"bEnableGlobalChat:\s*(true|false)"
            )
            match = re.search(pattern, response)

            if match:
                server_info = {
                    "ServerDetailsServerName": match.group(1),
                    "ServerPassword": match.group(2),
                    "ServerMap": match.group(3),
                    "ServerMaxPlayers": int(match.group(4)),
                    "ServerCurrentPlayers": int(match.group(5)),
                    "bEnableMutations": match.group(6) == "true",
                    "bEnableHumans": match.group(7) == "true",
                    "bServerPassword": match.group(8) == "true",
                    "bQueueEnabled": match.group(9) == "true",
                    "bServerWhitelist": match.group(10) == "true",
                    "bSpawnAI": match.group(11) == "true",
                    "bAllowRecordingReplay": match.group(12) == "true",
                    "bUseRegionSpawning": match.group(13) == "true",
                    "bUseRegionSpawnCooldown": match.group(14) == "true",
                    "RegionSpawnCooldownTimeSeconds": int(match.group(15)),
                    "ServerDayLengthMinutes": int(match.group(16)),
                    "ServerNightLengthMinutes": int(match.group(17)),
                    "bEnableGlobalChat": match.group(18) == "true",
                }
                return server_info
            else:
                logging.error("Pattern did not match the response format.")
                return None
        except Exception as e:
            logging.error(f"Error retrieving server info: {e}")
            return None

    @tasks.loop(seconds=30)
    async def update_bot_activity(self):
        try:
            server_info = await self.get_server_info()
            if server_info:
                player_count = server_info["ServerCurrentPlayers"]
                max_players = server_info["ServerMaxPlayers"]
                activity_text = f"Players {player_count}/{max_players}"
                activity = nextcord.Activity(type=nextcord.ActivityType.watching, name=activity_text)
                await self.bot.change_presence(activity=activity)
        except Exception as e:
            logging.error(f"Error updating bot activity: {e}")

    @update_bot_activity.before_loop
    async def before_update_bot_activity(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=5)
    async def update_server_info(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            guild_info_list = loadserverinfo(guild.id)
            if guild_info_list:
                for guild_info in guild_info_list:
                    channel = self.bot.get_channel(int(guild_info['channel_id']))
                    if channel:
                        try:
                            message = await channel.fetch_message(int(guild_info['message_id']))
                            server_info = await self.get_server_info()
                            if server_info:
                                embed = self.create_embed(server_info)
                                await message.edit(embed=embed)
                        except Exception as e:
                            logging.error(f"Error updating server info for guild {guild.id}: {e}")

    @update_server_info.before_loop
    async def before_update_server_info(self):
        await self.bot.wait_until_ready()

    @nextcord.slash_command(
        description='Post a live tracker of your game server.',
        default_member_permissions=nextcord.Permissions(administrator=True)
    )
    async def postserver(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel):
        await interaction.response.defer(ephemeral=True)
        server_info = await self.get_server_info()
        if server_info:
            embed = self.create_embed(server_info)
            message = await channel.send(embed=embed)
            saveserverinfo(interaction.guild_id, channel.id, message.id)
            await interaction.followup.send(f"Server info message created in {channel.mention}", ephemeral=True)
        else:
            await interaction.followup.send("Error retrieving server info. Check the RCON connection.", ephemeral=True)

    def cog_unload(self):
        self.update_server_info.cancel()
        self.update_bot_activity.cancel()

def setup(bot):
    cog = EvrimaMonitorCog(bot)
    bot.add_cog(cog)
    if not hasattr(bot, 'all_slash_commands'):
        bot.all_slash_commands = []
    bot.all_slash_commands.extend([
        cog.postserver
    ])
