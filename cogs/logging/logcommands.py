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

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Log Commands cog is ready.")
        self.check_admin_commands.start()

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

    def read_file(self, sftp, filepath, last_position):
        with sftp.file(filepath, "r") as file:
            if last_position is None:
                file.seek(0, os.SEEK_END)
                last_position = file.tell()
            else:
                file.seek(last_position)
            file_content = file.read().decode()
            new_position = file.tell()
        return file_content, new_position

    def parse_admin_commands(self, file_content):
        pattern = r"\[LogTheIsleCommandData\]: (.*?) \[(\d+)\] used command: (.*?)(?: at: (.*?), \[(\d+)\], Class: (.*?), Gender: (.*?), Previous value: (.*?), New value: (.*?)%)?$"
        matches = re.findall(pattern, file_content)

        admin_commands = []
        for match in matches:
            admin_name, steam_id, command = match[:3]
            target = match[3] if len(match) > 3 else None
            target_id = match[4] if len(match) > 4 else None
            target_class = match[5] if len(match) > 5 else None
            target_gender = match[6] if len(match) > 6 else None
            prev_value = match[7] if len(match) > 7 else None
            new_value = match[8] if len(match) > 8 else None

            embed = nextcord.Embed(
                title="Admin Log",
                description=f"{admin_name} [{steam_id}] used command: {command}",
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
        file_content, new_position = await self.async_sftp_operation(
            self.read_file, self.filepath, self.last_position
        )
        if self.last_position is not None and new_position > self.last_position:
            self.last_position = new_position
            all_commands = file_content.strip().splitlines()
            for command_line in all_commands:
                admin_commands = self.parse_admin_commands(command_line + '\n')
                await self.send_admin_commands(admin_commands)
        elif self.last_position is None:
            self.last_position = new_position

    async def send_admin_commands(self, admin_commands):
        channel = self.bot.get_channel(self.admin_log)
        if channel:
            for message in admin_commands:
                if len(message) > 2000:
                    message = message[:2000]
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