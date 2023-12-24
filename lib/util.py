import os
import json
import asyncio

async def evrima_rcon(host, port, password, command_bytes):
    timeout = 30
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)

        payload = bytes('\x01', 'utf-8') + password.encode() + bytes('\x00', 'utf-8')
        writer.write(payload)
        await writer.drain()

        response = await asyncio.wait_for(reader.read(1024), timeout=timeout)
        if "Accepted" not in str(response):
            writer.close()
            await writer.wait_closed()
            return "Login failed"

        writer.write(command_bytes)
        await writer.drain()

        response = await asyncio.wait_for(reader.read(1024), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return response.decode()

    except asyncio.TimeoutError:
        return "Connection timed out"
    except asyncio.CancelledError:
        return "Connection cancelled"
    except Exception as e:
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