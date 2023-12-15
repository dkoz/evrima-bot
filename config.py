from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_PREFIX = os.getenv("BOT_PREFIX")
RCON_HOST = os.getenv("RCON_HOST")
RCON_PORT = int(os.getenv("RCON_PORT", 0))
RCON_PASS = os.getenv("RCON_PASS")
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID", 0))
