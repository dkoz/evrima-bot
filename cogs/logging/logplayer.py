import nextcord
from nextcord.ext import commands, tasks
import paramiko
import os
import re
import asyncio
import logging
from util.config import FTP_HOST, FTP_PASS, FTP_PORT, FTP_USER, ENABLE_LOGGING, FILE_PATH
from util.database import add_player, get_players

class LogPlayers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ftp_host = FTP_HOST
        self.ftp_port = FTP_PORT
        self.ftp_username = FTP_USER
        self.ftp_password = FTP_PASS
        self.filepath = FILE_PATH
        self.last_position = None
        self.last_stat = None
        self.update_task = self.update_players_background.start()

    def cog_unload(self):
        self.update_task.cancel()

    @tasks.loop(minutes=3)
    async def update_players_background(self):
        try:
            result = await self.async_sftp_operation(self.read_file, self.filepath, self.last_position)
            if result is None:
                logging.error("Failed to read file from SFTP.")
                return
            file_content, new_position = result
            self.last_position = new_position
            if file_content:
                player_data = self.parse_log_file(file_content)
                for player in player_data:
                    await add_player(player["Name"], player["EOS_Id"], player["Steam_Id"])
                logging.info("Player data updated automatically.")
        except Exception as e:
            logging.error(f"Error in update_players_background loop: {e}")

    @update_players_background.before_loop
    async def before_update_players(self):
        await self.bot.wait_until_ready()

    async def async_sftp_operation(self, operation, *args, **kwargs):
        loop = asyncio.get_event_loop()
        try:
            with paramiko.Transport((self.ftp_host, self.ftp_port)) as transport:
                transport.connect(username=self.ftp_username, password=self.ftp_password)
                sftp = paramiko.SFTPClient.from_transport(transport)
                try:
                    result = await loop.run_in_executor(None, operation, sftp, *args, **kwargs)
                    return result
                finally:
                    sftp.close()
        except Exception as e:
            logging.error(f"SFTP operation error: {e}")
            return None

    def read_file(self, sftp, filepath, last_position):
        current_stat = sftp.stat(filepath)
        if last_position is None or (self.last_stat is not None and current_stat.st_size < last_position):
            last_position = 0
        self.last_stat = current_stat
        with sftp.file(filepath, "r") as file:
            file.seek(last_position)
            content = file.read().decode()
            new_position = file.tell()
        return content, new_position

    def parse_log_file(self, file_content):
        pattern_connection = r"\[LogTheIsleServer\]: \[Player Connecting .. Steam_Id: (\d+)\s*,\s*EOS_Id: (\w+)\]"
        pattern_join = r"\[LogTheIsleJoinData\]: (\w+) \[(\d+)\]"
        connections = re.findall(pattern_connection, file_content)
        joins = re.findall(pattern_join, file_content)
        conn_dict = {}
        for steam_id, eos_id in connections:
            conn_dict[steam_id] = eos_id
        join_dict = {}
        for name, steam_id in joins:
            join_dict[steam_id] = name
        players = []
        seen = set()
        for steam_id in join_dict:
            if steam_id in conn_dict:
                eos_id = conn_dict[steam_id]
                name = join_dict[steam_id]
                if steam_id not in seen:
                    seen.add(steam_id)
                    players.append({
                        "Name": name,
                        "EOS_Id": eos_id,
                        "Steam_Id": steam_id
                    })
                    logging.info(f"Recorded player: Name={name}, EOS_Id={eos_id}, Steam_Id={steam_id}")
        return players

    @commands.command(description="Manually update the player database.")
    @commands.is_owner()
    async def updateplayers(self, ctx):
        result = await self.async_sftp_operation(self.read_file, self.filepath, self.last_position)
        if result is None:
            await ctx.send("Failed to connect to SFTP server.")
            return
        file_content, new_position = result
        self.last_position = new_position
        player_data = self.parse_log_file(file_content)
        for player in player_data:
            await add_player(player["Name"], player["EOS_Id"], player["Steam_Id"])
        logging.info(f"Manually parsed player data: {player_data}")
        await ctx.send("Player data updated.")

    @commands.command(description="Manually list all players in the database.")
    @commands.is_owner()
    async def listplayers(self, ctx):
        players = await get_players()
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

def setup(bot):
    if ENABLE_LOGGING:
        bot.add_cog(LogPlayers(bot))
    else:
        logging.info("LogPlayers cog is disabled.")
