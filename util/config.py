from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "default_bot_token")
BOT_PREFIX = os.getenv("BOT_PREFIX", "!")
RCON_HOST = os.getenv("RCON_HOST", "localhost")
RCON_PORT = int(os.getenv("RCON_PORT", 25575))
RCON_PASS = os.getenv("RCON_PASS", "default_rcon_password")
DEFAULT_GUILDS = [int(id.strip()) for id in os.getenv("DEFAULT_GUILDS", "").split(",") if id.strip().isdigit()]

CHATLOG_CHANNEL = int(os.getenv("CHATLOG_CHANNEL", 0))
KILLFEED_CHANNEL = int(os.getenv("KILLFEED_CHANNEL", 0))
ADMINLOG_CHANNEL = int(os.getenv("ADMINLOG_CHANNEL", 0))
LINK_CHANNEL = int(os.getenv("LINK_CHANNEL", 0))

ENABLE_LOGGING = os.getenv('ENABLE_LOGGING', 'false').lower() in ['true', '1', 'yes']
FTP_HOST = os.getenv("FTP_HOST", "localhost")
FTP_PORT = int(os.getenv("FTP_PORT", 21))
FTP_USER = os.getenv("FTP_USER", "user")
FTP_PASS = os.getenv("FTP_PASS", "password")
FILE_PATH = os.getenv("FILE_PATH", "/TheIsle/Saved/Logs/TheIsle-Shipping.log")
ADMIN_FILE_PATH = os.getenv("ADMIN_FILE_PATH", "/TheIsle/Saved/Config/LinuxServer/Game.ini")
ENABLE_INJECTIONS = os.getenv('ENABLE_INJECTIONS', 'false').lower() in ['true', '1', 'yes']

PTERO_ENABLE = os.getenv('PTERO_ENABLE', 'false').lower() in ['true', '1', 'yes']
PTERO_API = os.getenv("PTERO_API", "default_api_key")
PTERO_URL = os.getenv("PTERO_URL", "http://localhost")
PTERO_WHITELIST = [int(id.strip()) for id in os.getenv("PTERO_WHITELIST", "").split(",") if id.strip().isdigit()]
PTERO_SERVER = os.getenv("PTERO_SERVER", 0)

ENABLE_RESTART = os.getenv('ENABLE_RESTART', 'false').lower() in ['true', '1', 'yes']
RESTART_CHANNEL = int(os.getenv("RESTART_CHANNEL", 0))