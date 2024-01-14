import nextcord
from nextcord.ext import commands, tasks
import paramiko
import os
import json
import re
import asyncio
from config import ENABLE_LOGGING, FTP_HOST, FTP_PASS, FTP_PORT, FTP_USER

# This is highly experimental and is not completed yet.
# This has to be enable inside your ENV file.
class LogPlayers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ftp_host = FTP_HOST
        self.ftp_port = FTP_PORT
        self.ftp_username = FTP_USER
        self.ftp_password = FTP_PASS
        self.filepath = "/TheIsle/Saved/Logs/TheIsle.log"
        self.json_file = "players.json"
        self.update_task = self.update_players_background.start()

    def cog_unload(self):
        self.update_task.cancel()

    @tasks.loop(minutes=5)
    async def update_players_background(self):
        file_content = await self.async_sftp_operation(self.read_file, self.filepath)
        if file_content is not None:
            player_data = self.parse_log_file(file_content)
            self.update_json(player_data)
            print("Player data updated automatically.")
        else:
            print("Failed to connect to SFTP server.")

    @update_players_background.before_loop
    async def before_update_players(self):
        await self.bot.wait_until_ready()

    async def async_sftp_operation(self, operation, *args, **kwargs):
        loop = asyncio.get_event_loop()
        with paramiko.Transport((self.ftp_host, self.ftp_port)) as transport:
            transport.connect(username=self.ftp_username, password=self.ftp_password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            try:
                result = await loop.run_in_executor(None, operation, sftp, *args, **kwargs)
                return result
            finally:
                sftp.close()

    def read_file(self, sftp, filepath):
        with sftp.file(filepath, "r") as file:
            file_content = file.read().decode()
        return file_content

    def parse_log_file(self, file_content):
        pattern = r"LogNet: Login request: .*?Name=([^\s]+) userId: RedpointEOS:(\w+) platform: RedpointEOS.*?LogTemp: Warning: Player Connecting \.\. Steam_Id: (\d+)"
        matches = re.findall(pattern, file_content, re.DOTALL)

        player_data = []
        seen = set()
        for match in matches:
            player_tuple = (match[0], match[1], match[2])
            if player_tuple not in seen:
                seen.add(player_tuple)
                player_data.append({
                    "Name": match[0],
                    "EOS_Id": match[1],
                    "Steam_Id": match[2]
                })
        return player_data

    def update_json(self, player_data):
        data_folder = "data"
        json_file = os.path.join(data_folder, "players.json")

        os.makedirs(data_folder, exist_ok=True)

        try:
            with open(json_file, "r+", encoding="utf-8") as file:
                existing_data = json.load(file)
                updated_data = existing_data.copy()

                for new_entry in player_data:
                    if not any(player['EOS_Id'] == new_entry['EOS_Id'] and player['Steam_Id'] == new_entry['Steam_Id'] for player in existing_data):
                        updated_data.append(new_entry)

                file.seek(0)
                file.truncate()
                json.dump(updated_data, file, indent=4)

        except FileNotFoundError:
            with open(json_file, "w", encoding="utf-8") as file:
                json.dump(player_data, file, indent=4)

    @commands.command(description="Update the players database.")
    @commands.is_owner()
    async def updateplayers(self, ctx):
        file_content = await self.async_sftp_operation(self.read_file, self.filepath)
        if file_content is not None:
            player_data = self.parse_log_file(file_content)
            self.update_json(player_data)
            await ctx.send("Player data updated.")
        else:
            await ctx.send("Failed to connect to SFTP server.")

    @commands.command()
    @commands.is_owner()
    async def listplayers(self, ctx):
        data_folder = "data"
        json_file = os.path.join(data_folder, "players.json")

        try:
            with open(json_file, "r", encoding="utf-8") as file:
                players = json.load(file)
                if not players:
                    await ctx.send("No players found in the database.")
                    return

                message = "Player List:\n"
                for player in players:
                    new_line = f"Name: {player['Name']}, EOSID: {player['EOS_Id']}, SteamID64: {player['Steam_Id']}\n"
                    if len(message) + len(new_line) > 2000:
                        await ctx.send(message)
                        message = "Player List Continued:\n"

                    message += new_line

                if message:
                    await ctx.send(message)

        except FileNotFoundError:
            await ctx.send("Players database not found.")

def setup(bot):
    if ENABLE_LOGGING:
        bot.add_cog(LogPlayers(bot))
    else:
        print("LogPlayers cog is disabled.")
