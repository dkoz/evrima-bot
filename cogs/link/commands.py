import nextcord
from nextcord.ext import commands
import random
import util.database as db

class LinkSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="Generate a link code.")
    async def link(self, interaction: nextcord.Interaction):
        code = "{:06d}".format(random.randint(0, 999999))
        await db.add_link(code, str(interaction.user.id))
        await interaction.response.send_message(f"Your link code is: `{code}`", ephemeral=True)

    @nextcord.slash_command(description="Get your linked profile.")
    async def profile(self, interaction: nextcord.Interaction):
        profile_data = await db.user_profile(str(interaction.user.id))
        if not profile_data:
            await interaction.response.send_message("You are not linked.", ephemeral=True)
            return

        steam_id = profile_data["steam_id"]
        status = profile_data["status"]
        eos_id = profile_data["eos_id"]
        discord_name = interaction.user.name
        avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url

        embed = nextcord.Embed(
            title=f"{discord_name}'s Profile",
            description="Welcome to your profile!",
            color=nextcord.Color.blurple()
        )
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Steam ID", value=steam_id, inline=False)
        embed.add_field(name="EOS ID", value=eos_id, inline=False)
        embed.add_field(name="Status", value=status, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name="link")
    @commands.is_owner()
    async def link_command(self, ctx, code: str, steam_id: str):
            link_record = await db.get_link(code, str(ctx.author.id))
            if not link_record:
                await ctx.send("Invalid code or you did not generate one.")
                return
            if link_record["status"] != "pending":
                await ctx.send("This code has already been used.")
                return
            await db.update_link(code, str(ctx.author.id), steam_id)
            await ctx.send("Your account has been successfully linked.")

def setup(bot):
    cog = LinkSystem(bot)
    bot.add_cog(cog)
    if not hasattr(bot, "all_slash_commands"):
        bot.all_slash_commands = []
    bot.all_slash_commands.extend(
        [
            cog.link,
            cog.profile,
        ]
    )
