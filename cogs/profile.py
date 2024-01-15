import nextcord
from nextcord.ext import commands
import json
import os

class PlayerProfileLinker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = "data"
        self.players_file = os.path.join(self.data_folder, "players.json")
        self.linked_accounts_file = os.path.join(self.data_folder, "linked_accounts.json")
        os.makedirs(self.data_folder, exist_ok=True)

    @nextcord.slash_command(name="linkaccount", description="Link your Discord account with your in-game SteamID64")
    async def linkaccount(self, interaction: nextcord.Interaction, steam_id: str):
        discord_id = str(interaction.user.id)

        if not os.path.exists(self.players_file):
            await interaction.response.send_message("The players database is not available.")
            return

        with open(self.players_file, "r", encoding="utf-8") as file:
            players_data = json.load(file)
            player_profile = next((player for player in players_data if player["Steam_Id"] == steam_id), None)

        if not player_profile:
            await interaction.response.send_message("No player found with the provided SteamID64.")
            return

        if not os.path.exists(self.linked_accounts_file):
            with open(self.linked_accounts_file, "w", encoding="utf-8") as file:
                json.dump({}, file, indent=4)

        with open(self.linked_accounts_file, "r+", encoding="utf-8") as file:
            linked_accounts = json.load(file)
            if discord_id in linked_accounts:
                await interaction.response.send_message("Your Discord account is already linked.")
                return

            linked_accounts[discord_id] = player_profile
            file.seek(0)
            file.truncate()
            json.dump(linked_accounts, file, indent=4)

        await interaction.response.send_message("Account linked successfully.")

    @nextcord.slash_command(name="me", description="Display your linked in-game profile information")
    async def me(self, interaction: nextcord.Interaction):
        discord_id = str(interaction.user.id)

        if not os.path.exists(self.linked_accounts_file):
            await interaction.response.send_message("No profile linked with your Discord account.")
            return

        with open(self.linked_accounts_file, "r", encoding="utf-8") as file:
            linked_accounts = json.load(file)
            profile = linked_accounts.get(discord_id)

        if profile:
            embed = nextcord.Embed(title=profile['Name'], color=nextcord.Color.blue())
            embed.add_field(name="Steam ID", value=profile['Steam_Id'], inline=False)
            embed.add_field(name="EOS ID", value=profile['EOS_Id'], inline=False)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No profile linked with your Discord account.")

    @nextcord.slash_command(name="find", description="Find a player by name, EOS ID, or SteamID64")
    async def findplayer(self, interaction: nextcord.Interaction, search_term: str):
        data_folder = "data"
        json_file = os.path.join(data_folder, "players.json")

        try:
            with open(json_file, "r", encoding="utf-8") as file:
                players = json.load(file)
                found_players = []

                for player in players:
                    if search_term.lower() in player['Name'].lower() or \
                    search_term in player['EOS_Id'] or \
                    search_term in player['Steam_Id']:
                        found_players.append(player)

                if found_players:
                    message = "Found Players:\n"
                    for player in found_players:
                        new_line = f"Name: {player['Name']}, EOSID: {player['EOS_Id']}, SteamID64: {player['Steam_Id']}\n"
                        if len(message) + len(new_line) > 2000:
                            await interaction.response.send_message(message)
                            message = "Player List Continued:\n"

                        message += new_line

                    await interaction.response.send_message(message, ephemeral=True)
                else:
                    await interaction.response.send_message("No players found with that search term.", ephemeral=True)

        except FileNotFoundError:
            await interaction.response.send_message("Players database not found.", ephemeral=True)

def setup(bot):
    cog = PlayerProfileLinker(bot)
    bot.add_cog(cog)
    if not hasattr(bot, 'all_slash_commands'):
        bot.all_slash_commands = []
    bot.all_slash_commands.extend([
        cog.linkaccount,
        cog.me,
        cog.findplayer
    ])