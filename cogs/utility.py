import nextcord
from nextcord.ext import commands
import util.constants as c
import util.database as db

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initialize())

    async def initialize(self):
        await db.init_db()

    @nextcord.slash_command(description="Get the bot's latency.", default_member_permissions=nextcord.Permissions(administrator=True))
    async def ping(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms")

    @nextcord.slash_command(description="Shows list of guilds the bot is in.", default_member_permissions=nextcord.Permissions(administrator=True))
    async def guilds(self, interaction: nextcord.Interaction):
        guilds = self.bot.guilds

        embed = nextcord.Embed(title="Guilds", description="List of Guilds", color=nextcord.Color.blue())
        for guild in guilds:
            embed.add_field(name=guild.name, value=f"ID: {guild.id}", inline=False)
        
        embed.set_footer(text="Created by KoZ")

        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(description="Get detailed statistics of the server.", default_member_permissions=nextcord.Permissions(administrator=True))
    async def serverstats(self, interaction: nextcord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("This command can only be used in a server.")
            return

        online_members = sum(1 for member in guild.members if member.status != nextcord.Status.offline)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)

        embed = nextcord.Embed(title=f"{guild.name} Statistics", color=0x00ff00)
        embed.add_field(name="Total Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Online Members", value=str(online_members), inline=True)
        embed.add_field(name="Total Text Channels", value=str(text_channels), inline=True)
        embed.add_field(name="Total Voice Channels", value=str(voice_channels), inline=True)
        embed.add_field(name="Total Categories", value=str(categories), inline=True)
        embed.add_field(name="Number of Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Server Creation Date", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(description="Get information about a user.", default_member_permissions=nextcord.Permissions(administrator=True))
    async def userinfo(self, interaction: nextcord.Interaction, member: nextcord.Member = None):
        member = member or interaction.user
        roles = [role.name for role in member.roles[1:]]

        embed = nextcord.Embed(title=f"User Information - {member}", color=0x00ff00)
        embed.add_field(name="Username", value=member.display_name, inline=True)
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.add_field(name="Status", value=str(member.status).title(), inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Joined Discord", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Activity", value=member.activity.name if member.activity else "None", inline=True)
        embed.add_field(name="Roles", value=", ".join(roles) if roles else "No Roles", inline=False)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)

        await interaction.response.send_message(embed=embed)
        
    @nextcord.slash_command(description="Show map of the server.")
    async def map(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        map_embed = nextcord.Embed(
            title="Server Map",
            description="This is the map of the server.",
            url="https://vulnona.com/game/the_isle/",
            color=nextcord.Color.blurple()
        )
        map_embed.set_image(url="https://raw.githubusercontent.com/dkoz/evrima-bot/refs/heads/main/assets/worldmap.png")
        map_embed.set_footer(
            text=f"{c.BOT_TEXT} {c.BOT_VERSION}",
            icon_url=c.BOT_ICON
        )
        await interaction.followup.send(embed=map_embed)

def setup(bot):
    cog = Utility(bot)
    bot.add_cog(cog)
    if not hasattr(bot, 'all_slash_commands'):
        bot.all_slash_commands = []
    bot.all_slash_commands.extend([
        cog.ping,
        cog.guilds,
        cog.serverstats,
        cog.userinfo
    ])