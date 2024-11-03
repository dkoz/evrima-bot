import nextcord
from nextcord.ext import commands
from gamercon_async import EvrimaRCON
from util.config import RCON_HOST, RCON_PORT, RCON_PASS

class EvrimaWhitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rcon_host = RCON_HOST
        self.rcon_password = RCON_PASS
        self.rcon_port = RCON_PORT

    @nextcord.slash_command(description="Evrima whitelist commands.", default_member_permissions=nextcord.Permissions(administrator=True))
    async def whitelist(self, _interaction: nextcord.Interaction):
        pass

    @whitelist.subcommand(name="add", description="Add a player to the whitelist.")
    async def addwhitelist(self, interaction: nextcord.Interaction, eos_id: str):
        command = b'\x02' + b'\x82' + eos_id.encode() + b'\x00'
        response = await self.run_rcon(command)
        await interaction.response.send_message(f"RCON response: {response}", ephemeral=True)

    @whitelist.subcommand(name="remove", description="Remove a player from the whitelist.")
    async def removewhitelist(self, interaction: nextcord.Interaction, eos_id: str):
        command = b'\x02' + b'\x83' + eos_id.encode() + b'\x00'
        response = await self.run_rcon(command)
        await interaction.response.send_message(f"RCON response: {response}", ephemeral=True)

    @whitelist.subcommand(name="enable", description="Enable the whitelist.")
    async def enablewhitelist(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("Enabling the whitelist for your server.", ephemeral=True)
        command = b'\x02' + b'\x81' + b'\x00'
        response = await self.run_rcon(command)
        await interaction.followup.send(f"RCON response: {response}", ephemeral=True)
            
    async def run_rcon(self, command):
        rcon = EvrimaRCON(self.rcon_host, self.rcon_port, self.rcon_password)
        await rcon.connect()
        return await rcon.send_command(command)
    
def setup(bot):
    cog = EvrimaWhitelist(bot)
    bot.add_cog(cog)
    if not hasattr(bot, 'all_slash_commands'):
        bot.all_slash_commands = []
    bot.all_slash_commands.append([
        cog.whitelist,
        cog.addwhitelist,
        cog.removewhitelist,
        cog.enablewhitelist
    ])