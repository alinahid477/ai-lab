from flask import Flask, request, Response
import requests
import asyncio
import websockets
import threading
from urllib.parse import urlencode
import os
app = Flask(__name__)


# Optional health check route
@app.route("/")
def healthz():
    return "HTTP+WebSocket proxy is running"


# === HTTP Proxy Logic ===
BACKEND_HTTP_URL = os.getenv("PROXY_APP_BACKEND_HTTP_URL", "http://backend-aiapp.intellilogs.svc.cluster.local:8000")

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_http(path):

    # Build full backend URL including query string
    target_url = f"{BACKEND_HTTP_URL}/{path}"
    if request.query_string:
        target_url += f"?{request.query_string.decode()}"

    print(f"PROXY: to target: {target_url}")
    # Forward the HTTP request
    
    resp = requests.request(
        method=request.method,
        url=target_url,
        headers={key: value for key, value in request.headers if key.lower() != 'host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    print(f"PROXY: from target: {resp}")
    return Response(resp.content, resp.status_code, resp.headers.items())

# === WebSocket Proxy Logic ===
BACKEND_WS_URL = os.getenv("PROXY_APP_BACKEND_WS_URL", "ws://backend-wsserver.intellilogs.svc.cluster.local:8765")


# WebSocket proxy logic
def run_ws_proxy():
    async def handler(client_ws, path):
        async with websockets.connect(BACKEND_WS_URL) as backend_ws:
            async def client_to_backend():
                try:
                    async for message in client_ws:
                        print(f"WS_PROXY: client_to_backend: {message}")
                        await backend_ws.send(message)
                except websockets.exceptions.ConnectionClosed:
                    pass

            async def backend_to_client():
                try:
                    async for message in backend_ws:
                        print(f"WS_PROXY: backend_to_client: {message}")
                        await client_ws.send(message)
                except websockets.exceptions.ConnectionClosed:
                    pass

            await asyncio.gather(client_to_backend(), backend_to_client())

    async def start_ws_proxy():
        print("start_ws_proxy...\n")
        wsport=int(os.getenv("PROXY_WS_PORT", "8765"))
        wshost=(os.getenv("PROXY_WW_HOST", "0.0.0.0"))
        async with websockets.serve(handler, wshost, wsport):
            await asyncio.Future()  # Run forever

    asyncio.run(start_ws_proxy())


# === Entry point ===
if __name__ == "__main__":
    print("starting WS proxy...\n")
    # Start WebSocket proxy in a background thread
    threading.Thread(target=run_ws_proxy, daemon=True).start()
    print("starting HTTP proxy...\n")
    webport=int(os.getenv("PROXY_WEB_PORT", "8000"))
    webhost=(os.getenv("PROXY_WEB_HOST", "0.0.0.0"))
    # Start Flask HTTP server
    app.run(host=webhost, port=webport)
