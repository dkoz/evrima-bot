import os
import json
        
def saveserverinfo(guild_id, channel_id, message_id):
    directory = 'data'
    filepath = os.path.join(directory, 'monitor.json')
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    guild_data = data.get(str(guild_id), [])
    guild_data.append({'channel_id': channel_id, 'message_id': message_id})
    data[str(guild_id)] = guild_data
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def loadserverinfo(guild_id):
    directory = 'data'
    filepath = os.path.join(directory, 'monitor.json')
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data.get(str(guild_id))
    except FileNotFoundError:
        return None