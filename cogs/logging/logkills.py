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
        self.last_stat = None
        self.check_kill_feed.start()

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

    def parse_kill_feed(self, file_content):
        pattern = (
            r'^\[(?P<timestamp>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2})\]'
            r'\[LogTheIsleKillData\]:\s+'
            r'(?P<killer>.*?)\s+\[(?P<killer_id>\d+)\]\s+Dino:\s+(?P<killer_dino>.*?),\s+'
            r'(?P<killer_gender>Male|Female),\s+(?P<killer_value>[\d\.]+)\s+-\s+'
            r'(?:(?P<natural>Died from Natural cause)'
            r'|Killed\s+the\s+following\s+player:\s+(?P<victim>.*?),\s+\[(?P<victim_id>\d+)\],\s+'
            r'Dino:\s+(?P<victim_dino>.*?),\s+Gender:\s+(?P<victim_gender>Male|Female),\s+'
            r'Growth:\s+(?P<victim_growth>[\d\.]+)(?:,.*)?)$'
        )
        matches = re.findall(pattern, file_content)
        kill_feed = []
        if not matches:
            #logging.error("Kill feed pattern did not match the response format.")
            return kill_feed
        for match in matches:
            timestamp = match[0]
            killer = match[1]
            killer_id = match[2]
            killer_dino = match[3]
            killer_gender = match[4]
            killer_value = match[5]
            natural = match[6]
            victim = match[7]
            victim_id = match[8]
            victim_dino = match[9]
            victim_gender = match[10]
            victim_growth = match[11]
            if natural:
                message = nextcord.Embed(
                    title="Kill Feed",
                    description=f"[{timestamp}] {killer} [{killer_id}] {killer_dino} died from natural causes."
                )
            else:
                message = nextcord.Embed(
                    title="Kill Feed",
                    description=f"[{timestamp}] {killer} [{killer_id}] {killer_dino} killed {victim} [{victim_id}] {victim_dino}"
                )
            kill_feed.append(message)
        return kill_feed

    @tasks.loop(seconds=30)
    async def check_kill_feed(self):
        try:
            result = await self.async_sftp_operation(self.read_file, self.filepath, self.last_position)
            if result is None:
                return
            file_content, new_position = result
            self.last_position = new_position
            all_kills = file_content.strip().splitlines()
            for kill_line in all_kills:
                kill_feed = self.parse_kill_feed(kill_line + '\n')
                if kill_feed:
                    await self.send_kill_feed(kill_feed)
        except Exception as e:
            logging.error(f"Error in check_kill_feed loop: {e}")

    async def send_kill_feed(self, kill_feed):
        channel = self.bot.get_channel(self.kill_feed_channel_id)
        if channel:
            for message in kill_feed:
                try:
                    await channel.send(embed=message)
                    await asyncio.sleep(1)
                except Exception as e:
                    logging.error(f"Error sending kill feed message: {e}")
        else:
            logging.error("Kill feed channel not found or bot does not have permission to access it.")

def setup(bot):
    if ENABLE_LOGGING:
        bot.add_cog(KillFeed(bot))
    else:
        logging.info("KillFeed cog is disabled.")
