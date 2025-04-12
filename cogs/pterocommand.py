import nextcord
from nextcord.ext import commands
import logging
from util.config import PTERO_API, PTERO_URL, PTERO_WHITELIST, PTERO_ENABLE, PTERO_SERVER
from util.pteroutil import PterodactylAPI
import util.constants as constants

ptero = PterodactylAPI(PTERO_URL, PTERO_API)
SERVER_ID = PTERO_SERVER

class ConfirmActionView(nextcord.ui.View):
    def __init__(self, action):
        super().__init__(timeout=30)
        self.action = action

    @nextcord.ui.button(label="Yes", style=nextcord.ButtonStyle.success)
    async def yes_button(self, button, interaction):
        try:
            s = await ptero.send_power_action(SERVER_ID, self.action)
            if s:
                await interaction.response.edit_message(content=f"{self.action.capitalize()}ing...", view=None)
            else:
                await interaction.response.edit_message(content=f"Failed to {self.action}.", view=None)
        except Exception as e:
            logging.error(str(e))
            await interaction.response.edit_message(content=str(e), view=None)

    @nextcord.ui.button(label="No", style=nextcord.ButtonStyle.danger)
    async def no_button(self, button, interaction):
        await interaction.response.edit_message(content="Action canceled.", view=None)

class PterodactylControlView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def authcheck(self, interaction: nextcord.Interaction):
        if interaction.user.id not in PTERO_WHITELIST:
            await interaction.response.send_message("You cannot use this command.", ephemeral=True)
            return False
        return True

    @nextcord.ui.button(label="Start", style=nextcord.ButtonStyle.green, custom_id="ptero_start")
    async def start_button(self, button, interaction):
        if not await self.authcheck(interaction):
            return
        view = ConfirmActionView("start")
        await interaction.response.send_message("Are you sure you want to start?", view=view, ephemeral=True)

    @nextcord.ui.button(label="Stop", style=nextcord.ButtonStyle.danger, custom_id="ptero_stop")
    async def stop_button(self, button, interaction):
        if not await self.authcheck(interaction):
            return
        view = ConfirmActionView("stop")
        await interaction.response.send_message("Are you sure you want to stop?", view=view, ephemeral=True)

    @nextcord.ui.button(label="Kill", style=nextcord.ButtonStyle.danger, custom_id="ptero_kill")
    async def kill_button(self, button, interaction):
        if not await self.authcheck(interaction):
            return
        view = ConfirmActionView("kill")
        await interaction.response.send_message("Are you sure you want to kill?", view=view, ephemeral=True)

    @nextcord.ui.button(label="Restart", style=nextcord.ButtonStyle.primary, custom_id="ptero_restart")
    async def restart_button(self, button, interaction):
        if not await self.authcheck(interaction):
            return
        view = ConfirmActionView("restart")
        await interaction.response.send_message("Are you sure you want to restart?", view=view, ephemeral=True)

    @nextcord.ui.button(label="Info", style=nextcord.ButtonStyle.secondary, custom_id="ptero_info")
    async def info_button(self, button, interaction):
        if not await self.authcheck(interaction):
            return
        try:
            i = await ptero.get_server_info(SERVER_ID)
            u = await ptero.get_server_usage(SERVER_ID)
            if not i or "attributes" not in i:
                await interaction.response.send_message("Failed to get info.", ephemeral=True)
                return
            d = i["attributes"]
            r = u["attributes"]["resources"] if u else {}
            up = r.get("uptime", 0)
            upm = int(up / 1000 / 60) if up else 0
            e = nextcord.Embed(title="Server Info")
            e.add_field(name="Name", value=d.get("name", "N/A") or "N/A", inline=True)
            e.add_field(name="Status", value=d.get("status", "Unknown") or "Unknown", inline=True)
            e.add_field(name="Node", value=d.get("node", "N/A") or "N/A", inline=True)
            e.add_field(name="Memory", value=f"{r.get('memory_bytes', 0)/1048576:.2f} MB", inline=True)
            e.add_field(name="CPU", value=f"{r.get('cpu_absolute', 0):.2f}%" if r.get("cpu_absolute") is not None else "0.00%", inline=True)
            e.add_field(name="Disk", value=f"{r.get('disk_bytes', 0)/1073741824:.2f} GB", inline=True)
            e.add_field(name="Uptime", value=f"{upm}m", inline=True)
            e.set_footer(text=f"ID: {SERVER_ID}")
            await interaction.response.send_message(embed=e, ephemeral=True)
        except Exception as e:
            logging.error(str(e))
            await interaction.response.send_message(str(e), ephemeral=True)

class PterodactylPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.view_added = False

    @commands.command(name="sendpanel")
    @commands.is_owner()
    async def send_panel_cmd(self, ctx, channel_id: int):
        if not PTERO_ENABLE:
            await ctx.send("Pterodactyl controls are disabled.")
            return
        c = self.bot.get_channel(channel_id)
        if not c:
            await ctx.send("Invalid channel.")
            return
        e = nextcord.Embed(title="Pterodactyl Control", description="Manage your server directly from Discord. Use the buttons below to start, stop, or restart your server.")
        e.set_thumbnail(url=constants.BOT_ICON)
        e.set_footer(text=f"{constants.BOT_TEXT} {constants.BOT_VERSION}")
        v = PterodactylControlView()
        await c.send(embed=e, view=v)
        await ctx.send(f"Panel sent to {c.mention}.")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.view_added:
            self.bot.add_view(PterodactylControlView())
            self.view_added = True

def setup(bot):
    if PTERO_ENABLE:
        bot.add_cog(PterodactylPanel(bot))
    else:
        logging.info("Pterodactyl Panel Cog is disabled.")
