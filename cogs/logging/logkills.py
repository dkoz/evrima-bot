import nextcord
from nextcord.ext import commands, tasks
import paramiko
import os
import re
import asyncio
import logging
from util.config import FTP_HOST, FTP_PASS, FTP_PORT, FTP_USER
from util.config import ENABLE_LOGGING, KILLFEED_CHANNEL, FILE_PATH

class KillFeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ftp_host = FTP_HOST
        self.ftp_port = FTP_PORT
        self.ftp_username = FTP_USER
        self.ftp_password = FTP_PASS
        self.filepath = FILE_PATH
        self.kill_feed_channel_id = KILLFEED_CHANNEL
        self.last_position = None

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("KillFeed cog is ready.")
        self.check_kill_feed.start()

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

    def parse_kill_feed(self, file_content):
        pattern = r"\[LogTheIsleKillData\]: (.*?) \[(\d+)\] Dino: (.*?), (Male|Female), \d+\.\d+ - (Died from Natural cause|Killed the following player: (.*?), \[(\d+)\], Dino: (.*?),)"
        matches = re.findall(pattern, file_content)

        kill_feed = []
        for match in matches:
            try:
                logging.info(f"Parsing match: {match}")
                time, killer, killer_id, killer_dino, event_type, victim, victim_id, victim_dino = match
                if "Died from Natural cause" in event_type:
                    message = nextcord.Embed(
                        title="Kill Feed",
                        description=f"[{time}] {killer} [{killer_id}] {killer_dino} died from natural causes."
                    )
                elif "Killed the following player" in event_type:
                    message = nextcord.Embed(
                        title="Kill Feed",
                        description=f"[{time}] {killer} [{killer_id}] {killer_dino} killed {victim} [{victim_id}] {victim_dino}."
                    )
                kill_feed.append(message)
            except Exception as e:
                logging.error(f"Error parsing match: {match} - {e}")
        return kill_feed

    @tasks.loop(seconds=30)
    async def check_kill_feed(self):
        file_content, new_position = await self.async_sftp_operation(
            self.read_file, self.filepath, self.last_position
        )
        if self.last_position is not None and new_position > self.last_position:
            self.last_position = new_position
            all_kills = file_content.strip().splitlines()
            for kill_line in all_kills:
                kill_feed = self.parse_kill_feed(kill_line + '\n')
                await self.send_kill_feed(kill_feed)
        elif self.last_position is None:
            self.last_position = new_position

    async def send_kill_feed(self, kill_feed):
        channel = self.bot.get_channel(self.kill_feed_channel_id)
        if channel:
            for message in kill_feed:
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
        bot.add_cog(KillFeed(bot))
    else:
        logging.info("KillFeed cog is disabled.")