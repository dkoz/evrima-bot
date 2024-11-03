import nextcord
from nextcord.ext import commands
from gamercon_async import EvrimaRCON
from util.config import RCON_HOST, RCON_PORT, RCON_PASS

class ToggleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rcon_host = RCON_HOST
        self.rcon_password = RCON_PASS
        self.rcon_port = RCON_PORT

    @nextcord.slash_command(
        description="Evrima Toggle Commands",
        default_member_permissions=nextcord.Permissions(administrator=True),
        dm_permission=False
    )
    async def toggle(self, _interaction: nextcord.Interaction):
        pass
    
    @toggle.subcommand(description="Toggle AI.")
    async def ai(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("Toggling AI on/off. Please wait for a response.", ephemeral=True)
        command = b'\x02' + b'\x90' + b'\x00'
        response = await self.run_rcon(command)
        await interaction.followup.send(f"RCON response: {response}", ephemeral=True)
    
    @toggle.subcommand(description="Toggle humans.")
    async def humans(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("Toggling humans on/off. Please wait for a response.", ephemeral=True)
        command = b'\x02' + b'\x86' + b'\x00'
        response = await self.run_rcon(command)
        await interaction.followup.send(f"RCON response: {response}", ephemeral=True)

    @toggle.subcommand(description="Toggle global chat.")
    async def globalchat(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("Toggling global chat on/off. Please wait for a response.", ephemeral=True)
        command = b'\x02' + b'\x84' + b'\x00'
        response = await self.run_rcon(command)
        await interaction.followup.send(f"RCON response: {response}", ephemeral=True)

    async def run_rcon(self, command):
        rcon = EvrimaRCON(self.rcon_host, self.rcon_port, self.rcon_password)
        await rcon.connect()
        return await rcon.send_command(command)

def setup(bot):
    bot.add_cog(ToggleCog(bot))
