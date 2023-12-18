import nextcord
from nextcord.ext import commands
import paramiko
import os
import json
import re
from config import ENABLE_LOGPLAYERS, FTP_HOST, FTP_PASS, FTP_PORT, FTP_USER

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

    def connect_sftp(self):
        try:
            transport = paramiko.Transport((self.ftp_host, self.ftp_port))
            transport.connect(username=self.ftp_username, password=self.ftp_password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            return sftp
        except Exception as e:
            print(f"Error connecting to SFTP: {e}")
            return None

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


    @commands.command()
    @commands.is_owner()
    async def updateplayers(self, ctx):
        sftp = self.connect_sftp()
        if sftp:
            with sftp.file(self.filepath, "r") as file:
                file_content = file.read().decode()
            sftp.close()
            
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
                    message += f"Name: {player['Name']}, EOS_Id: {player['EOS_Id']}, Steam_Id: {player['Steam_Id']}\n"

                await ctx.send(message)

        except FileNotFoundError:
            await ctx.send("Players database not found.")

def setup(bot):
    if ENABLE_LOGPLAYERS:
        bot.add_cog(LogPlayers(bot))
    else:
        print("LogPlayers cog is disabled.")