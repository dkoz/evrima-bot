import nextcord
from nextcord.ext import commands
from util.config import PTERO_API, PTERO_URL, PTERO_WHITELIST, PTERO_ENABLE, PTERO_SERVER
import logging
from util.pteroutil import PterodactylAPI

ptero = PterodactylAPI(PTERO_URL, PTERO_API)
SERVER_ID = PTERO_SERVER

class PterodactylControls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def authcheck(self, interaction: nextcord.Interaction):
        if interaction.user.id not in PTERO_WHITELIST:
            await interaction.response.send_message('You cannot use this command!', ephemeral=True)
            return False
        return True

    async def poweraction(self, interaction: nextcord.Interaction, action: str):
        if not await self.authcheck(interaction):
            return
        try:
            success = await ptero.send_power_action(SERVER_ID, action)
            if success:
                await interaction.response.send_message(f'{action.capitalize()}ing server.')
            else:
                logging.error(f'Failed to send {action} command.')
                await interaction.response.send_message(f'Failed to send {action} command.', ephemeral=True)
        except Exception as e:
            logging.error(f'Error: {e}')
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

    @nextcord.slash_command(
        description="Pterodactyl Controls",
        default_member_permissions=nextcord.Permissions(administrator=True)
    )
    async def ptero(self, interaction: nextcord.Interaction):
        pass

    @ptero.subcommand(description="Pterodactyl help menu.")
    async def panelhelp(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Pterodactyl Server Controls", description="List of available commands:", color=0x00ff00)
        embed.add_field(name="/ptero startserver", value="Start the game server.", inline=False)
        embed.add_field(name="/ptero stopserver", value="Stop the game server.", inline=False)
        embed.add_field(name="/ptero restartserver", value="Restart the game server.", inline=False)
        embed.add_field(name="/ptero killserver", value="Kill the game server.", inline=False)
        embed.add_field(name="/ptero info", value="Displays information about the game server.", inline=False)
        embed.set_footer(text="Use /ptero <command> to execute a command.")

        await interaction.response.send_message(embed=embed)

    @ptero.subcommand(description="Start the game server.")
    async def startserver(self, interaction: nextcord.Interaction):
        await self.poweraction(interaction, 'start')

    @ptero.subcommand(description="Stop the game server.")
    async def stopserver(self, interaction: nextcord.Interaction):
        await self.poweraction(interaction, 'stop')

    @ptero.subcommand(description="Restart the game server.")
    async def restartserver(self, interaction: nextcord.Interaction):
        await self.poweraction(interaction, 'restart')

    @ptero.subcommand(description="Kill the game server.")
    async def killserver(self, interaction: nextcord.Interaction):
        await self.poweraction(interaction, 'kill')

    @ptero.subcommand(description="Displays information about the game server.")
    async def info(self, interaction: nextcord.Interaction):
        if not await self.authcheck(interaction):
            return
        try:
            server_info = await ptero.get_server_info(SERVER_ID)
            usage_info = await ptero.get_server_usage(SERVER_ID)

            if not server_info or "attributes" not in server_info:
                await interaction.response.send_message("Failed to fetch server info.", ephemeral=True)
                return

            details = server_info["attributes"]
            resources = usage_info["attributes"]["resources"] if usage_info else {}

            uptime_ms = resources.get('uptime', 0)
            uptime_minutes = int(uptime_ms / 1000 / 60) if uptime_ms else 0

            embed = nextcord.Embed(title="Server Details", color=0x00ff00)
            embed.add_field(name="Name", value=details.get("name", "N/A") or "N/A", inline=True)
            embed.add_field(name="Status", value=details.get("status", "Unknown") or "Unknown", inline=True)
            embed.add_field(name="Node", value=details.get("node", "N/A") or "N/A", inline=True)
            embed.add_field(name="Memory Usage", value=f"{resources.get('memory_bytes', 0) / 1048576:.2f} MB", inline=True)
            embed.add_field(name="CPU Usage", value=f"{resources.get('cpu_absolute', 0):.2f}%" if resources.get("cpu_absolute") is not None else "0.00%", inline=True)
            embed.add_field(name="Disk Usage", value=f"{resources.get('disk_bytes', 0) / 1073741824:.2f} GB", inline=True)
            embed.add_field(name="Uptime", value=f"{uptime_minutes} minutes", inline=True)
            embed.set_footer(text=f"Server ID: {SERVER_ID}")

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logging.error(f'Error: {e}')
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

def setup(bot):
    if PTERO_ENABLE:
        cog = PterodactylControls(bot)
        bot.add_cog(cog)
        if not hasattr(bot, 'all_slash_commands'):
            bot.all_slash_commands = []
        bot.all_slash_commands.extend([
            cog.panelhelp,
            cog.startserver,
            cog.stopserver,
            cog.restartserver,
            cog.killserver,
            cog.info
        ])
    else:
        logging.info("Pterodactyl Controls are disabled.")