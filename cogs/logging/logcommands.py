import nextcord
from nextcord.ext import commands, tasks
import paramiko
import os
import re
import asyncio
from config import FTP_HOST, FTP_PASS, FTP_PORT, FTP_USER
from config import ENABLE_LOGGING, ADMINLOG_CHANNEL, FILE_PATH

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
        print("Log Commands cog is ready.")
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
        pattern = r"LogTheIsleCommandData: Verbose: \[(.*?)\] (.*?) \[(\d+)\] used command: (.*?) at: (.*?), \[(\d+)\], Class: (.*?), Gender: (.*?), Previous value: (.*?), New value: (.*?)%"
        matches = re.findall(pattern, file_content)

        admin_commands = []
        for match in matches:
            timestamp, admin_name, steam_id, command, target, target_id, target_class, target_gender, prev_value, new_value = match
            # format in embed
            # message = f"[{timestamp}] {admin_name} [{steam_id}] used command: {command} on {target} [{target_id}], Class: {target_class}, Gender: {target_gender}, Previous value: {prev_value}, New value: {new_value}%"
            message = nextcord.Embed(
                title="Admin Log",
                description=f"[{timestamp}] {admin_name} [{steam_id}] used command: {command}",
            )
            message.add_field(name="Target", value=f"{target} ({target_id})", inline=False)
            message.add_field(name="Class", value=f"{target_class}", inline=True)
            message.add_field(name="Gender", value=f"{target_gender}", inline=True)
            message.add_field(name="Previous Value", value=f"{prev_value}", inline=True)
            message.add_field(name="New Value", value=f"{new_value}", inline=True)
            admin_commands.append(message)
        return admin_commands

    @tasks.loop(seconds=10)
    async def check_admin_commands(self):
        file_content, new_position = await self.async_sftp_operation(
            self.read_file, self.filepath, self.last_position
        )
        if self.last_position is None or new_position != self.last_position:
            self.last_position = new_position
            admin_commands = self.parse_admin_commands(file_content)
            await self.send_admin_commands(admin_commands)

    async def send_admin_commands(self, admin_commands):
        channel = self.bot.get_channel(self.admin_log)
        if channel:
            for message in admin_commands:
                if len(message) > 2000:
                    message = message[:2000]

                try:
                    await channel.send(embed=message)
                except Exception as e:
                    print(f"Error sending message: {e}")
        else:
            print("Channel not found or bot does not have permission to access it.")

def setup(bot):
    if ENABLE_LOGGING:
        bot.add_cog(CommandFeed(bot))
    else:
        print("LogCommands cog is disabled.")