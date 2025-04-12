import nextcord
from nextcord.ext import commands
import paramiko
import os
import asyncio
import logging
import aiosqlite
from util.config import FTP_HOST, FTP_PASS, FTP_PORT, FTP_USER, ENABLE_LOGGING, FILE_PATH, LINK_CHANNEL
from util.database import DB_PATH

# Systerm still being developed, don't complain.
class DinoStorage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ftp_host = FTP_HOST
        self.ftp_port = FTP_PORT
        self.ftp_username = FTP_USER
        self.ftp_password = FTP_PASS

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

    def copy_remote_file(self, sftp, src, dest):
        try:
            try:
                sftp.stat(os.path.dirname(dest))
            except IOError:
                sftp.mkdir(os.path.dirname(dest))
            with sftp.open(src, "rb") as fsrc:
                data = fsrc.read()
            with sftp.open(dest, "wb") as fdest:
                fdest.write(data)
            return True
        except Exception as e:
            logging.error(f"Error copying remote file: {e}")
            return False

    def delete_remote_file(self, sftp, path):
        try:
            sftp.remove(path)
            return True
        except Exception as e:
            try:
                sftp.stat(path)
                logging.error(f"Error deleting remote file: {e}")
                return False
            except Exception:
                return True

    async def get_linked_steam_id(self, discord_id: str):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT steam_id FROM links WHERE discord_id = ? AND status = ?", (discord_id, "linked")) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
                return None

    @nextcord.slash_command(description="Store your dino.")
    async def store(self, interaction: nextcord.Interaction):
        discord_id = str(interaction.user.id)
        steam_id = await self.get_linked_steam_id(discord_id)
        if not steam_id:
            embed = nextcord.Embed(title="Dino Storage", description="You are not linked. Please link your account first.", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        src_sav = f"TheIsle/Saved/PlayerData/{steam_id}.sav"
        dest_sav = f"TheIsle/Saved/Garage/{discord_id}/{steam_id}.sav"

        result_sav = await self.async_sftp_operation(self.copy_remote_file, src_sav, dest_sav)

        if result_sav:
            try:
                dm_embed = nextcord.Embed(title="Dino Storage", description="Your dino has been successfully stored.", color=0x00FF00)
                await interaction.user.send(embed=dm_embed)
            except Exception as e:
                logging.error(f"DM error: {e}")

            channel = self.bot.get_channel(int(LINK_CHANNEL))
            if channel:
                channel_embed = nextcord.Embed(title="Dino Storage", description=f"User {interaction.user.id} stored their dino (Steam ID: {steam_id}).", color=0x00FF00)
                await channel.send(embed=channel_embed)

            success_embed = nextcord.Embed(title="Dino Storage", description="Dino stored successfully.", color=0x00FF00)
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        else:
            failure_embed = nextcord.Embed(title="Dino Storage", description="Failed to store dino.", color=0xFF0000)
            await interaction.response.send_message(embed=failure_embed, ephemeral=True)

    @nextcord.slash_command(description="Load your stored dino.")
    async def load(self, interaction: nextcord.Interaction):
        discord_id = str(interaction.user.id)
        steam_id = await self.get_linked_steam_id(discord_id)
        if not steam_id:
            embed = nextcord.Embed(title="Dino Storage", description="You are not linked. Please link your account first.", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        dest_sav = f"TheIsle/Saved/PlayerData/{steam_id}.sav"
        deletion_sav = await self.async_sftp_operation(self.delete_remote_file, dest_sav)

        if deletion_sav is False:
            delete_embed = nextcord.Embed(title="Dino Storage", description="Failed to delete previous save files.", color=0xFF0000)
            await interaction.response.send_message(embed=delete_embed, ephemeral=True)
            return

        src_sav = f"TheIsle/Saved/Garage/{discord_id}/{steam_id}.sav"
        result_sav = await self.async_sftp_operation(self.copy_remote_file, src_sav, dest_sav)

        if result_sav:
            try:
                dm_embed = nextcord.Embed(title="Dino Storage", description="Your dino has been successfully loaded.", color=0x00FF00)
                await interaction.user.send(embed=dm_embed)
            except Exception as e:
                logging.error(f"DM error: {e}")

            channel = self.bot.get_channel(int(LINK_CHANNEL))
            if channel:
                channel_embed = nextcord.Embed(title="Dino Storage", description=f"User {interaction.user.id} loaded their dino (Steam ID: {steam_id}).", color=0x00FF00)
                await channel.send(embed=channel_embed)

            success_embed = nextcord.Embed(title="Dino Storage", description="Dino loaded successfully.", color=0x00FF00)
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        else:
            failure_embed = nextcord.Embed(title="Dino Storage", description="Failed to load dino.", color=0xFF0000)
            await interaction.response.send_message(embed=failure_embed, ephemeral=True)

def setup(bot):
    if not ENABLE_LOGGING:
        return
    cog = DinoStorage(bot)
    bot.add_cog(cog)
    if not hasattr(bot, "all_slash_commands"):
        bot.all_slash_commands = []
    bot.all_slash_commands.extend(
        [
            cog.store,
            cog.load,
        ]
    )
