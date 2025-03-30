import nextcord
from nextcord.ext import commands, tasks
import paramiko
import os
import re
import asyncio
import logging
from util.config import FTP_HOST, FTP_PASS, FTP_PORT, FTP_USER
from util.config import ENABLE_LOGGING, CHATLOG_CHANNEL, FILE_PATH

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
        self.last_stat = None
        self.check_chat_log.start()

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

    def parse_chat_messages(self, file_content):
        pattern = (
            r'^\[(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2})\]'
            r'\[LogTheIsleChatData\]: \[(?P<channel>.*?)\] \[(?P<group>.*?)\] (?P<player>.*?) '
            r'\[(?P<steam_id>\d+)\]: (?P<message>.*)$'
        )
        matches = re.findall(pattern, file_content)
        chat_messages = []
        if not matches:
            #logging.error("Chat log pattern did not match the response format.")
            return chat_messages
        for match in matches:
            chat_messages.append({
                "Timestamp": match[0],
                "Channel": match[1],
                "Group": match[2],
                "Player": match[3],
                "SteamID64": match[4],
                "Message": match[5]
            })
        return chat_messages

    @tasks.loop(seconds=30)
    async def check_chat_log(self):
        try:
            result = await self.async_sftp_operation(self.read_file, self.filepath, self.last_position)
            if result is None:
                return
            file_content, new_position = result
            self.last_position = new_position
            all_messages = file_content.strip().splitlines()
            for message_line in all_messages:
                chat_messages = self.parse_chat_messages(message_line + '\n')
                if chat_messages:
                    await self.send_chat_messages(chat_messages)
        except Exception as e:
            logging.error(f"Error in check_chat_log loop: {e}")

    async def send_chat_messages(self, chat_messages):
        channel = self.bot.get_channel(self.chat_log_channel_id)
        if channel:
            for message in chat_messages:
                embed = nextcord.Embed(
                    title=f"{message['Channel']} - {message['Group']}",
                    description=f"{message['Player']} [{message['SteamID64']}]: {message['Message']}"
                )
                try:
                    await channel.send(embed=embed)
                    await asyncio.sleep(1)
                except Exception as e:
                    logging.error(f"Error sending chat message: {e}")
        else:
            logging.error("Chat log channel not found or bot does not have permission to access it.")

def setup(bot):
    if ENABLE_LOGGING:
        bot.add_cog(LogChat(bot))
    else:
        logging.info("LogChat cog is disabled.")
