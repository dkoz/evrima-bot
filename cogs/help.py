import nextcord
from nextcord.ext import commands
from config import BOT_PREFIX

class EvrimaHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="Shows a list of available commands.")
    async def help(self, interaction: nextcord.Interaction):
        bot_avatar_url = self.bot.user.avatar.url
        prefix = BOT_PREFIX

        embed = nextcord.Embed(title="Help Menu", description=f"List of all available commands.", color=nextcord.Color.blue())
        embed.set_footer(text="Created by Koz", icon_url=bot_avatar_url)

        for command in self.bot.commands:
            if not command.hidden and command.enabled:
                embed.add_field(name=f"`{prefix}{command.name}`", value=command.description or "No description", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.slash_command(description="Information about the Evrima Rcon bot.")
    async def about(self, interaction: nextcord.Interaction):
        bot_avatar_url = self.bot.user.avatar.url

        embed = nextcord.Embed(title="Evrima Rcon Bot", color=nextcord.Color.blue())
        embed.set_footer(text="Created by Koz", icon_url=bot_avatar_url)
        embed.add_field(name="About", value="The bot is an open-source project available [here](https://github.com/dkoz/evrima-bot). You can find more info on our readme. I'm always looking for code contributions and support! If there is something wrong with the bot itself, please let me know!", inline=False)
        embed.add_field(name="Creator", value="This bot was created by [Kozejin](https://kozejin.dev). Feel free to add `koz#1337` on discord if you have any questions.", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(EvrimaHelp(bot))