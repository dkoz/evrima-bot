import socket

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
