# The Isle: Evrima Discord RCON Bot
![GitHub License](https://img.shields.io/github/license/dkoz/ascension-bot?style=flat-square) ![Discord](https://img.shields.io/discord/802778278200475658?style=flat-square&label=community) ![Discord](https://img.shields.io/discord/1009881575187566632?style=flat-square&label=support)

 This is a discord RCON bot for The Isle: Evrima. (This is not an injection bot!)

## Requirements
>Requires Python 3.10+

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
