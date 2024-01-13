import nextcord
from nextcord.ext import commands, tasks
from config import RCON_HOST, RCON_PORT, RCON_PASS
from config import SERVERNAME, MAXPLAYERS, CURRENTMAP
from lib.util import evrima_rcon
from lib.util import saveserverinfo, loadserverinfo

class EvrimaMonitorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rcon_host = RCON_HOST
        self.rcon_port = RCON_PORT
        self.rcon_password = RCON_PASS
        self.update_player_count.start()
        self.update_bot_activity.start()

    def create_embed(self, player_count):
        servername = SERVERNAME
        currentmap = CURRENTMAP
        maxplayers = MAXPLAYERS

        embed = nextcord.Embed(title="Server Status", color=nextcord.Color.blue())
        embed.add_field(name=f"{servername}", value="", inline=False)
        embed.add_field(name="Map", value=f"{currentmap}", inline=True)
        embed.add_field(name="Players", value=f"{player_count}/{maxplayers}", inline=True)
        embed.add_field(name="Gamemode", value="Survival Mode", inline=True)

        return embed
    
    @tasks.loop(seconds=30)
    async def update_bot_activity(self):
        player_count = await self.get_player_count()
        activity_text = f"Players {player_count}/{MAXPLAYERS}"
        activity = nextcord.Activity(type=nextcord.ActivityType.watching, name=activity_text)
        await self.bot.change_presence(activity=activity)

    @update_bot_activity.before_loop
    async def before_update_bot_activity(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=5)
    async def update_player_count(self):
        print("Updating player count.")
        for guild in self.bot.guilds:
            guild_info_list = loadserverinfo(guild.id)
            if guild_info_list:
                for guild_info in guild_info_list:
                    channel = self.bot.get_channel(int(guild_info['channel_id']))
                    if channel:
                        try:
                            message = await channel.fetch_message(int(guild_info['message_id']))
                            player_count = await self.get_player_count()
                            embed = self.create_embed(player_count)
                            await message.edit(embed=embed)
                        except Exception as e:
                            print(f"Error updating player count for guild {guild.id}: {e}")

    async def get_player_count(self):
        command = bytes('\x02', 'utf-8') + bytes('\x40', 'utf-8') + bytes('\x00', 'utf-8')
        response = await evrima_rcon(self.rcon_host, self.rcon_port, self.rcon_password, command)
        return self.parse_player_list(response)

    def parse_player_list(self, response):
        lines = response.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        player_count = len(lines) // 2
        return player_count

    @nextcord.slash_command(description='Post a live tracker of your game server.', default_member_permissions=nextcord.Permissions(administrator=True))
    async def postserver(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel):
        try:
            player_count = await self.get_player_count()
            embed = self.create_embed(player_count)
            message = await channel.send(embed=embed)
            saveserverinfo(interaction.guild_id, channel.id, message.id)
            await interaction.response.send_message(f"Player count message created in {channel.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error creating player count message: {e}", ephemeral=True)

    @update_player_count.before_loop
    async def before_update_player_count(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.update_player_count.cancel()
        self.update_bot_activity.cancel()

def setup(bot):
    bot.add_cog(EvrimaMonitorCog(bot))
