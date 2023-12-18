from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_PREFIX = os.getenv("BOT_PREFIX")
RCON_HOST = os.getenv("RCON_HOST")
RCON_PORT = int(os.getenv("RCON_PORT", 0))
RCON_PASS = os.getenv("RCON_PASS")
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID", 0))

ENABLE_LOGPLAYERS = os.getenv('ENABLE_LOGPLAYERS', 'false').lower() in ['true', '1', 'yes']
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT"), 0)
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
HOSTNAME = os.getenv("HOSTNAME", "The Isle")
MAXPLAYERS = int(os.getenv("MAXPLAYERS", 100))
CURRENTMAP = os.getenv("CURRENTMAP", "Gateway")