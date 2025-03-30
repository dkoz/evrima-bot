import aiohttp

class PterodactylAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}

    async def get_server_info(self, server_id):
        url = f"{self.base_url}/api/client/servers/{server_id}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                return await response.json() if response.status == 200 else None

    async def get_server_usage(self, server_id):
        url = f"{self.base_url}/api/client/servers/{server_id}/resources"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                return await response.json() if response.status == 200 else None

    async def send_power_action(self, server_id, action):
        url = f"{self.base_url}/api/client/servers/{server_id}/power"
        data = {"signal": action}
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=data) as response:
                return response.status == 204
