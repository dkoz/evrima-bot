import nextcord
from nextcord.ext import commands
import paramiko
import asyncio
import io
from collections import defaultdict
from config import FTP_HOST, FTP_PASS, FTP_PORT, FTP_USER

class MultiKeyConfigParser:
    def __init__(self):
        self._sections = defaultdict(list)

    def read_string(self, string):
        current_section = None
        for line in string.splitlines():
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1]
            elif "=" in line and current_section is not None:
                key, value = line.split("=", 1)
                self._sections[current_section].append((key.strip(), value.strip()))

    def get(self, section, key):
        return [item[1] for item in self._sections[section] if item[0] == key]

    def set(self, section, key, values):
        self._sections[section] = [(k, v) for k, v in self._sections[section] if k != key]
        for value in values:
            self._sections[section].append((key, value))

    def to_string(self):
        lines = []
        for section, items in self._sections.items():
            lines.append(f"[{section}]")
            for key, value in items:
                lines.append(f"{key}={value}")
        return "\n".join(lines)

class GameIniAdminManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ftp_host = FTP_HOST
        self.ftp_port = FTP_PORT
        self.ftp_username = FTP_USER
        self.ftp_password = FTP_PASS
        self.ini_file_path = "/TheIsle/Saved/Config/LinuxServer/Game.ini"

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addadmin(self, ctx, steam_id: str):
        if await self.modify_admins(steam_id, add=True):
            await ctx.send(f"Admin {steam_id} added successfully.")
        else:
            await ctx.send("Failed to add admin.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removeadmin(self, ctx, steam_id: str):
        if await self.modify_admins(steam_id, add=False):
            await ctx.send(f"Admin {steam_id} removed successfully.")
        else:
            await ctx.send("Failed to remove admin.")

    async def modify_admins(self, steam_id, add=True):
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(None, self._modify_admins_sync, steam_id, add)
        except Exception as e:
            print(f"Error: {e}")
            return False

    def _modify_admins_sync(self, steam_id, add):
        transport = paramiko.Transport((self.ftp_host, self.ftp_port))
        transport.connect(username=self.ftp_username, password=self.ftp_password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        try:
            with sftp.open(self.ini_file_path, "r") as file:
                file_content = file.read().decode()

            config = MultiKeyConfigParser()
            config.read_string(file_content)

            admin_section = '/Script/TheIsle.TIGameStateBase'
            admin_key = 'AdminsSteamIDs'
            admins = config.get(admin_section, admin_key)

            if add:
                if steam_id not in admins:
                    admins.append(steam_id)
            else:
                if steam_id in admins:
                    admins.remove(steam_id)

            config.set(admin_section, admin_key, admins)

            new_file_content = config.to_string()

            with sftp.open(self.ini_file_path, "w") as file:
                file.write(new_file_content)
            return True
        finally:
            sftp.close()
            transport.close()

def setup(bot):
    bot.add_cog(GameIniAdminManager(bot))
