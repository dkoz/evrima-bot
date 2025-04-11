import nextcord
from nextcord.ext import commands, tasks
import paramiko
import os
import re
import asyncio
import logging
import aiosqlite
from util.config import FTP_HOST, FTP_PASS, FTP_PORT, FTP_USER, ENABLE_LOGGING, FILE_PATH, LINK_CHANNEL
from util.database import DB_PATH

class LinkListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.filepath = FILE_PATH
        self.ftp_host = FTP_HOST
        self.ftp_port = FTP_PORT
        self.ftp_username = FTP_USER
        self.ftp_password = FTP_PASS
        self.last_position = None
        self.last_stat = None
        self.check_link_commands.start()

    def cog_unload(self):
        self.check_link_commands.cancel()

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

    def parse_link_message(self, message):
        pattern = r'^!link\s+(\d{6})'
        match = re.match(pattern, message.strip())
        if match:
            return match.group(1)
        return None

    async def process_link_message(self, steam_id, code):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT id, discord_id FROM links WHERE code = ? AND status = ?", (code, "pending")) as cursor:
                row = await cursor.fetchone()
            if not row:
                return False, None
            link_id, discord_id = row
            await db.execute("UPDATE links SET steam_id = ?, status = ? WHERE id = ?", (steam_id, "linked", link_id))
            await db.commit()
        return True, discord_id

    async def notify_link_success(self, discord_id, steam_id, code):
        try:
            user = self.bot.get_user(int(discord_id))
            if user is None:
                user = await self.bot.fetch_user(int(discord_id))
            await user.send(f"Your account has been successfully linked. Steam ID: {steam_id}, Code: {code}")
        except Exception as e:
            logging.error(f"Error sending DM: {e}")
        try:
            channel = self.bot.get_channel(int(LINK_CHANNEL))
            if channel:
                await channel.send(f"Link successful: Discord ID {discord_id} linked with Steam ID {steam_id} using code {code}.")
        except Exception as e:
            logging.error(f"Error sending channel message: {e}")

    @tasks.loop(seconds=30)
    async def check_link_commands(self):
        try:
            result = await self.async_sftp_operation(self.read_file, self.filepath, self.last_position)
            if result is None:
                return
            content, new_position = result
            self.last_position = new_position
            lines = content.splitlines()
            for line in lines:
                pattern = r'^\[\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}\]\[LogTheIsleChatData\]: .*?\[(?P<steam_id>\d+)\]: (?P<message>.*)$'
                match = re.match(pattern, line)
                if match:
                    steam_id = match.group("steam_id")
                    message = match.group("message")
                    code = self.parse_link_message(message)
                    if code:
                        success, discord_id = await self.process_link_message(steam_id, code)
                        if success:
                            await self.notify_link_success(discord_id, steam_id, code)
        except Exception as e:
            logging.error(f"Error in check_link_commands loop: {e}")

def setup(bot):
    if not ENABLE_LOGGING:
        return
    bot.add_cog(LinkListener(bot))
