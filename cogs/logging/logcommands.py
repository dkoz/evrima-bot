import nextcord
from nextcord.ext import commands, tasks
import paramiko
import os
import re
import asyncio
import logging
from util.config import FTP_HOST, FTP_PASS, FTP_PORT, FTP_USER
from util.config import ENABLE_LOGGING, ADMINLOG_CHANNEL, FILE_PATH

class CommandFeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ftp_host = FTP_HOST
        self.ftp_port = FTP_PORT
        self.ftp_username = FTP_USER
        self.ftp_password = FTP_PASS
        self.filepath = FILE_PATH
        self.admin_log = ADMINLOG_CHANNEL
        self.last_position = None
        self.last_stat = None
        self.check_admin_commands.start()

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
            file_content = file.read().decode()
            new_position = file.tell()
        return file_content, new_position

    def parse_admin_commands(self, file_content):
        pattern = (
            r'^\[(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2})\]'
            r'\[LogTheIsleCommandData\]: (?P<admin>.*?) '
            r'\[(?P<steam_id>\d+)\] used command: (?P<command>.*?)(?: at: (?P<target>.*?), '
            r'\[(?P<target_id>\d+)\], Class: (?P<class>.*?), Gender: (?P<gender>.*?), '
            r'Previous value: (?P<prev_value>.*?%), New value: (?P<new_value>.*?%))?$'
        )
        matches = re.findall(pattern, file_content)
        admin_commands = []
        if not matches:
            #logging.error("Pattern did not match the response format.")
            return admin_commands
        for match in matches:
            admin_name = match[1]
            steam_id = match[2]
            command = match[3]
            target = match[4] if match[4] else None
            target_id = match[5] if match[5] else None
            target_class = match[6] if match[6] else None
            target_gender = match[7] if match[7] else None
            prev_value = match[8] if match[8] else None
            new_value = match[9] if match[9] else None
            embed = nextcord.Embed(
                title="Admin Log",
                description=f"{admin_name} [{steam_id}] used command: {command}"
            )
            if target:
                embed.add_field(name="Target", value=f"{target} ({target_id})", inline=False)
            if target_class:
                embed.add_field(name="Class", value=target_class, inline=True)
            if target_gender:
                embed.add_field(name="Gender", value=target_gender, inline=True)
            if prev_value:
                embed.add_field(name="Previous Value", value=prev_value, inline=True)
            if new_value:
                embed.add_field(name="New Value", value=new_value, inline=True)
            admin_commands.append(embed)
        return admin_commands

    @tasks.loop(seconds=30)
    async def check_admin_commands(self):
        try:
            result = await self.async_sftp_operation(self.read_file, self.filepath, self.last_position)
            if result is None:
                return
            file_content, new_position = result
            self.last_position = new_position
            all_commands = file_content.strip().splitlines()
            for command_line in all_commands:
                admin_commands = self.parse_admin_commands(command_line + '\n')
                if admin_commands:
                    await self.send_admin_commands(admin_commands)
        except Exception as e:
            logging.error(f"Error in check_admin_commands loop: {e}")

    async def send_admin_commands(self, admin_commands):
        channel = self.bot.get_channel(self.admin_log)
        if channel:
            for message in admin_commands:
                try:
                    await channel.send(embed=message)
                    await asyncio.sleep(1)
                except Exception as e:
                    logging.error(f"Error sending message: {e}")
        else:
            logging.error("Channel not found or bot does not have permission to access it.")

def setup(bot):
    if ENABLE_LOGGING:
        bot.add_cog(CommandFeed(bot))
    else:
        logging.info("LogCommands cog is disabled.")
