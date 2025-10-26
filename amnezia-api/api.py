# amnezia-api/api.py
import asyncio
import logging
import os
from aiohttp import web
from core import create_client_with_options, delete_client_by_name, get_client_vpn_key, list_clients

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_SECRET = os.getenv("AMNEZIA_API_SECRET", "change_me_in_production")

async def auth_middleware(app, handler):
    async def middleware(request):
        if request.path == "/health":
            return await handler(request)
        auth = request.headers.get("X-API-Key")
        if auth != API_SECRET:
            return web.json_response({"error": "Unauthorized"}, status=401)
        return await handler(request)
    return middleware

async def health(request):
    return web.json_response({"status": "ok"})

async def create_client_handler(request):
    try:
        data = await request.json()
        name = data.get("name")
        duration_days = data.get("duration_days")  # int or None
        traffic_limit = data.get("traffic_limit", "Неограниченно")
        if not name or not isinstance(name, str):
            return web.json_response({"error": "name (str) is required"}, status=400)
        result = create_client_with_options(name, duration_days, traffic_limit)
        return web.json_response(result)
    except Exception as e:
        logger.exception("Create client error")
        return web.json_response({"error": str(e)}, status=500)

async def delete_client_handler(request):
    try:
        data = await request.json()
        name = data.get("name")
        if not name:
            return web.json_response({"error": "name is required"}, status=400)
        success = delete_client_by_name(name)

        return web.json_response({"success": success})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def get_vpn_key_handler(request):
    name = request.match_info["name"]
    try:
        key = get_client_vpn_key(name)
        if key:
            return web.json_response({"vpn_key": key})
        else:
            return web.json_response({"error": "Client not found"}, status=404)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def list_clients_handler(request):
    try:
        clients = list_clients()
        return web.json_response(clients)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

app = web.Application(middlewares=[auth_middleware])
app.router.add_get("/health", health)
app.router.add_post("/create", create_client_handler)
app.router.add_post("/delete", delete_client_handler)
app.router.add_get("/key/{name}", get_vpn_key_handler)
app.router.add_get("/list", list_clients_handler)

if __name__ == "__main__":
    port = int(os.getenv("AMNEZIA_API_PORT", 8081))
    host = os.getenv("AMNEZIA_API_HOST", "127.0.0.1")
    web.run_app(app, host=host, port=port)