# The Isle: Evrima Discord RCON Bot
![GitHub License](https://img.shields.io/github/license/dkoz/ascension-bot?style=flat-square) ![Discord](https://img.shields.io/discord/802778278200475658?style=flat-square&label=community) ![Discord](https://img.shields.io/discord/1009881575187566632?style=flat-square&label=support)

 This is a discord RCON bot for The Isle: Evrima. (This is not an injection bot!)

## Optional Environmental Variables
Variable | Description
--- | ---
CHATLOG_CHANNEL | Channel where you want chat logs to be posted.
KILLFEED_CHANNEL | Channel where you want kill feed to be posted.
ENABLE_LOGPLAYERS | Enables the logging of players on your server.
FTP_HOST | Host information for the FTP connection.
FTP_PORT | Port number for the FTP connection.
FTP_USER | Username for FTP access.
FTP_PASS | Password for your FTP account.
SERVERNAME | The name of the server.
MAXPLAYERS | Maximum number of players allowed on the server.
CURRENTMAP | The current map for your server
PTERO_URL | Url to your pterodactyl panel.
PTERO_API | API key generated under your pterodactyl panel account.
PTERO_WHITELIST | Specified discord user ids that can control game servers.

## Requirements
>Requires [Python 3.10+](https://www.python.org/downloads/)

## Installation (Linux)
1. Create a new user and switch to it.
```
sudo adduser evrimarcon
su - evrimarcon
```
2. Clone the Arkon bot repository with the following commands
```
git clone https://github.com/dkoz/evrima-bot
cd evrima-bot
```
3. Now you need to create a virtual env and install the requirements.
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
4. Configure the environment variables.
```
cp .env.example .env
nano .env
```
5. Now run the bot.
```
python main.py
```
