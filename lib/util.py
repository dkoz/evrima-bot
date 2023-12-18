import socket
import os
import json

async def evrima_rcon(host, port, password, command_bytes):
    timeout = 30
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(timeout)
            s.connect((host, port))
            # Send login packets
            payload = bytes('\x01', 'utf-8') + password.encode() + bytes('\x00', 'utf-8')
            s.send(payload)
            # Check for login
            response = s.recv(1024)
            if "Accepted" not in str(response):
                return "Login failed"
            # Send the commands
            s.send(command_bytes)
            response = s.recv(1024)
            return response.decode()
        except socket.error as e:
            return f"Socket error: {e}"
        
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