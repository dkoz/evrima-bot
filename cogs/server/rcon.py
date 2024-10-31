import nextcord
from nextcord.ext import commands
from gamercon_async import EvrimaRCON
from config import RCON_HOST, RCON_PORT, RCON_PASS

class EvrimaRcon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rcon_host = RCON_HOST
        self.rcon_password = RCON_PASS
        self.rcon_port = RCON_PORT

    @nextcord.slash_command(description="Evrima RCON Commands", default_member_permissions=nextcord.Permissions(administrator=True))
    async def rcon(self, _interaction: nextcord.Interaction):
        pass

    @rcon.subcommand(description="Save the current state of the server.")
    async def saveserver(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("Saving server...", ephemeral=True)
        command = bytes('\x02', 'utf-8') + bytes('\x50', 'utf-8') + bytes('\x00', 'utf-8')
        response = await self.run_rcon(command)
        await interaction.followup.send(f"RCON response: {response}", ephemeral=True)

    @rcon.subcommand(description="Make an announcement on the server.")
    async def announce(self, interaction: nextcord.Interaction, message: str):
        command = bytes('\x02', 'utf-8') + bytes('\x10', 'utf-8') + message.encode() + bytes('\x00', 'utf-8')
        response = await self.run_rcon(command)
        await interaction.response.send_message(f"RCON response: {response}", ephemeral=True)

    @rcon.subcommand(description="Ban a player from the server.")
    async def banplayer(self, interaction: nextcord.Interaction, eos_id: str, ban_length: int):
        await interaction.response.send_message(f"Banning player with EOS ID {eos_id} for {ban_length} minutes.", ephemeral=True)
        userinput = f"{eos_id}, You have been banned!, {ban_length}"
        command = bytes('\x02', 'utf-8') + bytes('\x20', 'utf-8') + userinput.encode() + bytes('\x00', 'utf-8')
        response = await self.run_rcon(command)
        await interaction.followup.send(f"RCON response: {response}", ephemeral=True)

    @rcon.subcommand(description="Kick a player from the server.")
    async def kickplayer(self, interaction: nextcord.Interaction, eos_id: str, reason: str):
        await interaction.response.send_message(f"Kicking player steamid {eos_id}\nReason: {reason}", ephemeral=True)
        formatted_command = f"{eos_id},{reason}"
        command = bytes('\x02', 'utf-8') + bytes('\x30', 'utf-8') + formatted_command.encode() + bytes('\x00', 'utf-8')
        response = await self.run_rcon(command)
        await interaction.followup.send(f"RCON response: {response}", ephemeral=True)
    
    @rcon.subcommand(description="Display a list of players on the server.")
    async def playerlist(self, interaction: nextcord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            command = bytes('\x02', 'utf-8') + bytes('\x40', 'utf-8') + bytes('\x00', 'utf-8')
            response = await self.run_rcon(command)
            await interaction.followup.send(f"RCON response: {response}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

    @rcon.subcommand(description="Update list of allowed playables.")
    async def updateplayables(self, interaction: nextcord.Interaction, message: str):
        command = bytes('\x02', 'utf-8') + bytes('\x15', 'utf-8') + message.encode() + bytes('\x00', 'utf-8')
        response = await self.run_rcon(command)
        await interaction.response.send_message(f"RCON response: {response}", ephemeral=True)
        
    @rcon.subcommand(description="Get details about the server.")
    async def serverinfo(self, interaction: nextcord.Interaction):
        command = bytes('\x02', 'utf-8') + bytes('\x12', 'utf-8') + bytes('\x00', 'utf-8')
        response = await self.run_rcon(command)
        await interaction.response.send_message(f"RCON response: {response}", ephemeral=True)
        
    @rcon.subcommand(description="Get details about a player.")
    async def playerinfo(self, interaction: nextcord.Interaction, eos_id: str):
        await interaction.response.defer(ephemeral=True)
        command = bytes('\x02', 'utf-8') + bytes('\x77', 'utf-8') + eos_id.encode() + bytes('\x00', 'utf-8')
        response = await self.run_rcon(command)
        await interaction.followup.send(f"RCON response: {response}", ephemeral=True)

    async def run_rcon(self, command):
        rcon = EvrimaRCON(self.rcon_host, self.rcon_port, self.rcon_password)
        await rcon.connect()
        return await rcon.send_command(command)

def setup(bot):
    cog = EvrimaRcon(bot)
    bot.add_cog(cog)
    if not hasattr(bot, 'all_slash_commands'):
        bot.all_slash_commands = []
    bot.all_slash_commands.extend([
        cog.rcon,
        cog.saveserver,
        cog.announce,
        cog.banplayer,
        cog.kickplayer,
        cog.playerlist,
        cog.updateplayables,
        cog.serverinfo,
        cog.playerinfo
    ])
