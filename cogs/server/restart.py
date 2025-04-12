import asyncio
import nextcord
from nextcord.ext import commands, tasks
from gamercon_async import EvrimaRCON
from datetime import datetime
import logging
import pytz
from util.config import RCON_HOST, RCON_PORT, RCON_PASS
from util.config import PTERO_ENABLE, PTERO_SERVER, PTERO_API, PTERO_URL
from util.pteroutil import PterodactylAPI
from util.config import ENABLE_RESTART, RESTART_CHANNEL

class RestartServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rcon_host = RCON_HOST
        self.rcon_port = RCON_PORT
        self.rcon_password = RCON_PASS
        self.timeout = 30
        self.ptero = PterodactylAPI(PTERO_URL, PTERO_API)
        self.report_channel = RESTART_CHANNEL
        self.server_id = PTERO_SERVER
        self.restart_task.start()

    async def perform_restart(self, wait_time):
        announce_command = bytes('\x02', 'utf-8') + bytes('\x10', 'utf-8') + "Server restarting in 5 minutes.".encode() + bytes('\x00', 'utf-8')
        evrima_client = EvrimaRCON(self.rcon_host, self.rcon_port, self.rcon_password)
        await evrima_client.connect()
        await evrima_client.send_command(announce_command)
        asyncio.create_task(self.delayed_restart(wait_time))

    async def delayed_restart(self, wait_time):
        await asyncio.sleep(120)
        evrima_client2 = EvrimaRCON(self.rcon_host, self.rcon_port, self.rcon_password)
        await evrima_client2.connect()
        announce_command_3 = bytes('\x02', 'utf-8') + bytes('\x10', 'utf-8') + "Server restarting in 3 minutes.".encode() + bytes('\x00', 'utf-8')
        await evrima_client2.send_command(announce_command_3)
        await asyncio.sleep(120)
        evrima_client3 = EvrimaRCON(self.rcon_host, self.rcon_port, self.rcon_password)
        await evrima_client3.connect()
        announce_command_1 = bytes('\x02', 'utf-8') + bytes('\x10', 'utf-8') + "Server restarting in 1 minute.".encode() + bytes('\x00', 'utf-8')
        await evrima_client3.send_command(announce_command_1)
        await asyncio.sleep(60)
        try:
            success = await self.ptero.send_power_action(self.server_id, 'restart')
            if success:
                logging.info(f'Successfully restarted server with ID "{self.server_id}".')
            else:
                logging.error(f'Failed to restart server with ID "{self.server_id}".')
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f'Error during restart: {e}')

    @nextcord.slash_command(
        description="Restart the game server.",
        default_member_permissions=nextcord.Permissions(administrator=True)
    )
    async def restart(self, interaction: nextcord.Interaction, wait_time: int = 300):
        await interaction.response.send_message("Server restart initiated. Restarting in 5 minutes.", ephemeral=True)
        asyncio.create_task(self.perform_restart(wait_time))

    @tasks.loop(minutes=1)
    async def restart_task(self):
        now = datetime.now(pytz.timezone('US/Eastern'))
        if now.hour in [0, 6, 12, 18] and now.minute == 30:
            channel = self.bot.get_channel(self.report_channel)
            if channel:
                embed = nextcord.Embed(title="Scheduled Restart", description="Server restarting in 5 minutes.", color=nextcord.Color.blurple())
                await channel.send(embed=embed)
            else:
                logging.error("Announcement channel not found.")
            asyncio.create_task(self.perform_restart(300))

    @restart_task.before_loop
    async def before_restart_task(self):
        await self.bot.wait_until_ready()

def setup(bot):
    if ENABLE_RESTART and PTERO_ENABLE:
        cog = RestartServer(bot)
        bot.add_cog(cog)
        if not hasattr(bot, 'all_slash_commands'):
            bot.all_slash_commands = []
        bot.all_slash_commands.extend([cog.restart])
    else:
        logging.info("RestartServer cog disabled.")
