import nextcord
from nextcord.ext import commands, tasks
import paramiko
import os
import re
import asyncio
from config import FTP_HOST, FTP_PASS, FTP_PORT, FTP_USER
from config import ENABLE_LOGGING, CHATLOG_CHANNEL, FILE_PATH

class LogChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ftp_host = FTP_HOST
        self.ftp_port = FTP_PORT
        self.ftp_username = FTP_USER
        self.ftp_password = FTP_PASS
        self.filepath = FILE_PATH
        self.chat_log_channel_id = CHATLOG_CHANNEL
        self.last_position = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("LogChat cog is ready.")
        self.check_chat_log.start()

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

    def parse_chat_messages(self, file_content):
        pattern = r"LogTheIsleChatData: Verbose: \[.*?\] \[.*?\] \[.*?\] (.*?) \[(\d+)\]: (.*)"
        matches = re.findall(pattern, file_content)

        chat_messages = []
        for match in matches:
            chat_messages.append({
                "Player": match[0],
                "SteamID64": match[1],
                "Message": match[2]
            })
        return chat_messages

    @tasks.loop(seconds=10)
    async def check_chat_log(self):
        file_content, new_position = await self.async_sftp_operation(
            self.read_file, self.filepath, self.last_position
        )
        if self.last_position is None or new_position != self.last_position:
            self.last_position = new_position
            chat_messages = self.parse_chat_messages(file_content)
            await self.send_chat_messages(chat_messages)

    async def send_chat_messages(self, chat_messages):
        channel = self.bot.get_channel(self.chat_log_channel_id)
        if channel:
            for message in chat_messages:
                #content = f"{message['Player']} [{message['SteamID64']}]: {message['Message']}"
                #if len(content) > 2000:
                #    content = content[:2000]

                #try:
                #    await channel.send(content)
                content = nextcord.Embed(
                    title="Chat Log",
                    description=f"{message['Player']} [{message['SteamID64']}]: {message['Message']}",
                )
                try:
                    await channel.send(embed=content)
                except Exception as e:
                    print(f"Error sending message: {e}")
        else:
            print("Channel not found or bot does not have permission to access it.")

def setup(bot):
    if ENABLE_LOGGING:
        bot.add_cog(LogChat(bot))
    else:
        print("LogChat cog is disabled.")