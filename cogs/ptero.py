import nextcord
from nextcord.ext import commands
from pydactyl import PterodactylClient
from util.config import PTERO_API, PTERO_URL, PTERO_WHITELIST, PTERO_ENABLE
import logging

api = PterodactylClient(PTERO_URL, PTERO_API)

class PterodactylControls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def authcheck(self, interaction: nextcord.Interaction):
        if interaction.user.id not in PTERO_WHITELIST:
            await interaction.response.send_message('You can not use this command!', ephemeral=True)
            return False
        return True

    async def poweraction(self, interaction: nextcord.Interaction, server_id: str, action: str):
        if not await self.authcheck(interaction):
            return
        try:
            response = api.client.servers.send_power_action(server_id, action)
            if response.status_code == 204:
                await interaction.response.send_message(f'{action.capitalize()}ing server with ID "{server_id}".')
            else:
                logging.error(f'Unexpected response: {response.status_code} {response.text}')
                await interaction.response.send_message(f'Unexpected response: {response.status_code} {response.text}', ephemeral=True)
        except Exception as e:
            logging.error(f'You have an error: {e}')
            await interaction.response.send_message(f'You have an error: {e}', ephemeral=True)

    @nextcord.slash_command(
        description="Pterodactyl Controls",
        default_member_permissions=nextcord.Permissions(administrator=True),
        dm_permission=False
    )
    async def ptero(self, interaction: nextcord.Interaction):
        pass

    @ptero.subcommand(description="Pterodactyl help menu.")
    async def panelhelp(self, interaction: nextcord.Interaction):
        await self.show_help_menu(interaction)

    async def show_help_menu(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Pterodactyl Server Controls", description="List of available commands:", color=0x00ff00)
        embed.add_field(name="/ptero startserver", value="Start the specified game server.", inline=False)
        embed.add_field(name="/ptero stopserver", value="Stop the specified game server.", inline=False)
        embed.add_field(name="/ptero restartserver", value="Restart the specified game server.", inline=False)
        embed.add_field(name="/ptero killserver", value="Kill the specified game server.", inline=False)
        embed.add_field(name="/ptero info", value="Displays information about a specified game server.", inline=False)
        embed.set_footer(text="Use /ptero <command> to execute a command.")

        await interaction.response.send_message(embed=embed)

    @ptero.subcommand(description="Start the specified game server.")
    async def startserver(self, interaction: nextcord.Interaction, server_id: str):
        await self.poweraction(interaction, server_id, 'start')

    @ptero.subcommand(description="Stop the specified game server.")
    async def stopserver(self, interaction: nextcord.Interaction, server_id: str):
        await self.poweraction(interaction, server_id, 'stop')

    @ptero.subcommand(description="Restart the specified game server.")
    async def restartserver(self, interaction: nextcord.Interaction, server_id: str):
        await self.poweraction(interaction, server_id, 'restart')

    @ptero.subcommand(description="Kill the specified game server.")
    async def killserver(self, interaction: nextcord.Interaction, server_id: str):
        await self.poweraction(interaction, server_id, 'kill')
    
    @ptero.subcommand(description="Displays information about a specified game server.")
    async def info(self, interaction: nextcord.Interaction, server_id: str):
        """ Shows detailed information about a server """
        if not await self.authcheck(interaction):
            return
        try:
            server_info = api.client.servers.get_server(server_id)
            if not isinstance(server_info, dict):
                logging.error(f'Invalid response format: {server_info}')
                await interaction.response.send_message('Error: Invalid response format from the API.', ephemeral=True)
                return

            server_details = {
                "Name": server_info.get('name', 'N/A'),
                "Status": server_info.get('status', 'Unknown'),
                "Owner": 'Yes' if server_info.get('server_owner', False) else 'No',
                "Node": server_info.get('node', 'N/A'),
                "Memory Limit": f"{server_info['limits'].get('memory', 'N/A')} MB",
                "Disk Limit": f"{server_info['limits'].get('disk', 'N/A')} MB",
                "CPU Limit": f"{server_info['limits'].get('cpu', 'N/A')}%"
            }

            embed = nextcord.Embed(title="Server Details", color=0x00ff00)
            for key, value in server_details.items():
                embed.add_field(name=key, value=value, inline=True)
            embed.set_footer(text=f"Server ID: {server_id}")

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