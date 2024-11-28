> [!IMPORTANT]  
> This bot has been updated to the latest game version, `v0.17.65`. However, there are known issues with RCON that result in the `Game.ini` being deleted. Please note that these issues are due to the latest game update and not related to evrima-bot.

# The Isle: Evrima Discord RCON Bot
![GitHub License](https://img.shields.io/github/license/dkoz/ascension-bot?style=flat-square) ![Discord](https://img.shields.io/discord/802778278200475658?style=flat-square&label=community) ![Discord](https://img.shields.io/discord/1009881575187566632?style=flat-square&label=support)

 This is a discord RCON bot for The Isle: Evrima. (This is not an injection bot!)

## Important
 Most of the functionality of this bot is designed for the Pterodactyl game panel, or secure FTP connections. This bot will not work properly without it. The only function that will run without the panel is RCON.

## Optional Environmental Variables
Variable | Description
--- | ---
CHATLOG_CHANNEL | Channel where you want chat logs to be posted.
KILLFEED_CHANNEL | Channel where you want kill feed to be posted.
ADMINLOG_CHANNEL | Channel where in-game admin commands are logged.
ENABLE_LOGGING | Enables the logging on your server. (You must configure FTP Information when enabling this feature!)
FTP_HOST | Host information for the FTP connection.
FTP_PORT | Port number for the FTP connection.
FTP_USER | Username for FTP access.
FTP_PASS | Password for your FTP account.
FILE_PATH | File path to `TheIsle-Shipping.log` file.
ADMIN_FILE_PATH | File path to your `Game.ini` file.
ENABLE_INJECTIONS | Enable admin injections for your bot.
PTERO_ENABLE | Enable Pterodactyl Panel support
PTERO_URL | Url to your pterodactyl panel.
PTERO_API | API key generated under your pterodactyl panel account.
PTERO_WHITELIST | Specified discord user ids that can control game servers.
ENABLE_RESTART | Enables the restart cog.
RESTART_SERVERID | UUID for your pterodactyl server.
RESTART_CHANNEL | Channel that restarts will be reported to.

## Installation
For detailed installation instructions, please refer to our [git wiki](https://github.com/dkoz/evrima-bot/wiki). Specific instructions for [Linux](https://github.com/dkoz/evrima-bot/wiki/Linux-Installation) and [Windows](https://github.com/dkoz/evrima-bot/wiki/Windows-Installation) can be found at their respective links.
