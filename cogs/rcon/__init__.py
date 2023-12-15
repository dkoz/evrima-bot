import nextcord
from nextcord.ext import commands
from lib.util import evrima_rcon
from config import RCON_HOST, RCON_PORT, RCON_PASS, ADMIN_ROLE_ID

ADMIN_ROLE = ADMIN_ROLE_ID

class EvrimaRcon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rcon_host = RCON_HOST
        self.rcon_port = RCON_PORT
        self.rcon_password = RCON_PASS
        self.timeout = 30

    @commands.command(name="saveserver", description="Save the current state of the server.")
    @commands.has_role(ADMIN_ROLE)
    async def save_server(self, ctx):
        command = bytes('\x02', 'utf-8') + bytes('\x50', 'utf-8') + bytes('\x00', 'utf-8')
        response = await evrima_rcon(self.rcon_host, self.rcon_port, self.rcon_password, command)
        await ctx.send(f"RCON response: {response}")

    @commands.command(name="announce", description="Make an announcement on the server.")
    @commands.has_role(ADMIN_ROLE)
    async def make_announcement(self, ctx, *, message: str):
        command = bytes('\x02', 'utf-8') + bytes('\x10', 'utf-8') + message.encode() + bytes('\x00', 'utf-8')
        response = await evrima_rcon(self.rcon_host, self.rcon_port, self.rcon_password, command)
        await ctx.send(f"RCON response: {response}")

    @commands.command(name="banplayer", description="Ban a player from the server.")
    @commands.has_role(ADMIN_ROLE)
    async def ban_player(self, ctx, steam_id: str, description: str, ban_length: int):
        userinput = f"{steam_id}, {description}, {ban_length}"
        command = bytes('\x02', 'utf-8') + bytes('\x20', 'utf-8') + userinput.encode() + bytes('\x00', 'utf-8')
        response = await evrima_rcon(self.rcon_host, self.rcon_port, self.rcon_password, command)
        await ctx.send(f"RCON response: {response}")

    @commands.command(name="kickplayer", description="Kick a player from the server.")
    @commands.has_role(ADMIN_ROLE)
    async def kick_player(self, ctx, steam_id: str):
        command = bytes('\x02', 'utf-8') + bytes('\x30', 'utf-8') + steam_id.encode() + bytes('\x00', 'utf-8')
        response = await evrima_rcon(self.rcon_host, self.rcon_port, self.rcon_password, command)
        await ctx.send(f"RCON response: {response}")

    @commands.command(name="playerlist", description="Display a list of players on the server.")
    @commands.has_role(ADMIN_ROLE)
    async def player_list(self, ctx):
        command = bytes('\x02', 'utf-8') + bytes('\x40', 'utf-8') + bytes('\x00', 'utf-8')
        response = await evrima_rcon(self.rcon_host, self.rcon_port, self.rcon_password, command)
        await ctx.send(f"RCON response: {response}")

    @commands.command(name="update_playables", description="Update list of allowed playables. (Experimental).")
    @commands.has_role(ADMIN_ROLE)
    async def update_playables(self, ctx):
        command = bytes('\x02', 'utf-8') + bytes('\x15', 'utf-8') + bytes('\x00', 'utf-8')
        response = await evrima_rcon(self.rcon_host, self.rcon_port, self.rcon_password, command)
        await ctx.send(f"RCON response: {response}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send(f"You must have the required role to use this command.")
        else:
            pass

def setup(bot):
    bot.add_cog(EvrimaRcon(bot))
