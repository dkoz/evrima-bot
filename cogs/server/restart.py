import asyncio
import nextcord
from nextcord.ext import commands, tasks
from util.functions import evrima_rcon
from pydactyl import PterodactylClient
from datetime import datetime
import pytz
from config import RCON_HOST, RCON_PORT, RCON_PASS
from config import PTERO_API, PTERO_URL
from config import ENABLE_RESTART, RESTART_SERVERID, RESTART_CHANNEL

class RestartServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rcon_host = RCON_HOST
        self.rcon_port = RCON_PORT
        self.rcon_password = RCON_PASS
        self.timeout = 30
        self.ptero_client = PterodactylClient(PTERO_URL, PTERO_API)
        self.report_channel = RESTART_CHANNEL
        self.server_id = RESTART_SERVERID
        self.restart_task.start()

    async def perform_restart(self, server_id, wait_time):
        announce_command = bytes('\x02', 'utf-8') + bytes('\x10', 'utf-8') + "Server restarting in 5 minutes.".encode() + bytes('\x00', 'utf-8')
        await evrima_rcon(self.rcon_host, self.rcon_port, self.rcon_password, announce_command)

        await asyncio.sleep(wait_time)

        try:
            response = self.ptero_client.client.servers.send_power_action(server_id, 'restart')
            print(f'Restart command sent to server with ID "{server_id}". Response: {response.status_code}')

            await asyncio.sleep(5)

            kill_response = self.ptero_client.client.servers.send_power_action(server_id, 'kill')
            if kill_response.status_code == 204:
                print(f'Successfully sent kill command to server with ID "{server_id}".')
            else:
                print(f'Failed to send kill command: {kill_response.status_code} {kill_response.text}')
        except Exception as e:
            print(f'Error during restart: {e}')

    @commands.command(description="Automatically restart the game server with announcements.")
    @commands.is_owner()
    async def forcerestart(self, server_id: str, wait_time: int = 300):
        channel = self.bot.get_channel(self.report_channel)
        if channel:
            await channel.send("Server restart initiated. Restarting in 5 minutes.")
        else:
            print("Announcement channel not found.")

        await self.perform_restart(server_id, wait_time)

    @tasks.loop(minutes=1)
    async def restart_task(self):
        now = datetime.now(pytz.timezone('US/Eastern'))
        if now.hour in [0, 6, 12, 18] and now.minute == 30:
            channel = self.bot.get_channel(self.report_channel)
            if channel:
                await channel.send("Scheduled server restart initiated. Restarting in 5 minutes.")
            else:
                print("Announcement channel not found.")

            await self.perform_restart(self.server_id, 300)

    @restart_task.before_loop
    async def before_restart_task(self):
        await self.bot.wait_until_ready()

def setup(bot):
    if ENABLE_RESTART:
        bot.add_cog(RestartServer(bot))
    else:
        print("Restart cog is disabled.")
