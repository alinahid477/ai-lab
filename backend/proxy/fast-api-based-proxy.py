import os
import asyncio
import threading
import websockets
from fastapi import FastAPI, Request, Response
import httpx
from fastapi.middleware.cors import CORSMiddleware
# FastAPI app\ napp = FastAPI()

app = FastAPI()
# === CORS Middleware: restrict to specific domains via environment variable ===
# Set ALLOWED_ORIGINS as a comma-separated list, e.g.
#   export ALLOWED_ORIGINS="https://abc.com,https://cdf.com"
allowed_origins = os.getenv("PROXY_ALLOWED_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Health check route
@app.get("/")
async def healthz():
    return "HTTP+WebSocket proxy is running"

# === HTTP Proxy Logic ===
BACKEND_HTTP_URL = os.getenv(
    "PROXY_APP_BACKEND_HTTP_URL",
    "http://backend-aiapp.intellilogs.svc.cluster.local:8000"
)

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_http(path: str, request: Request):
    # Build full backend URL including query string
    target_url = f"{BACKEND_HTTP_URL}/{path}"
    if request.url.query:
        target_url += f"?{request.url.query}"

    print(f"PROXY HTTP → {target_url}")

    # Prepare headers (exclude host)
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}

    # Forward the HTTP request using httpx AsyncClient
    async with httpx.AsyncClient(follow_redirects=False) as client:
        resp = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
            cookies=request.cookies,
        )

    print(f"PROXY HTTP ← {resp.status_code}")
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
    )

# === WebSocket Proxy Logic ===
BACKEND_WS_URL = os.getenv(
    "PROXY_APP_BACKEND_WS_URL",
    "ws://backend-wsserver.intellilogs.svc.cluster.local:8765"
)

async def ws_handler(client_ws, path):
    async with websockets.connect(BACKEND_WS_URL) as backend_ws:
        async def client_to_backend():
            try:
                async for message in client_ws:
                    print(f"WS_PROXY: client→backend: {message}")
                    await backend_ws.send(message)
            except websockets.exceptions.ConnectionClosed:
                pass

        async def backend_to_client():
            try:
                async for message in backend_ws:
                    print(f"WS_PROXY: backend→client: {message}")
                    await client_ws.send(message)
            except websockets.exceptions.ConnectionClosed:
                pass

        await asyncio.gather(client_to_backend(), backend_to_client())


def run_ws_proxy():
    async def start_ws():
        wsport=int(os.getenv("PROXY_WS_PORT", "8765"))
        wshost=(os.getenv("PROXY_WW_HOST", "0.0.0.0"))
        print(f"Starting WS proxy on port {wshost}:{wsport}...")
        async with websockets.serve(ws_handler, wshost, wsport):
            await asyncio.Future()  # run forever

    asyncio.run(start_ws())

# === Entry point ===
if __name__ == "__main__":
    # Launch WebSocket proxy in background thread
    threading.Thread(target=run_ws_proxy, daemon=True).start()
    print(f"WebSocket proxy thread started...")

    # Launch FastAPI HTTP + WS server
    import uvicorn
    webport=int(os.getenv("PROXY_WEB_PORT", "8000"))
    webhost=(os.getenv("PROXY_WEB_HOST", "0.0.0.0"))
    print(f"Starting FastAPI HTTP proxy on port {webhost}:{webport}...")
    uvicorn.run(app, host=webhost, port=webport)