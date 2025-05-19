import asyncio
import websockets
import os
# Set of connected clients
connected_clients = set()

# Function to handle each client connection
async def handle_client(websocket):
    # Add the new client to the set of connected clients
    connected_clients.add(websocket)
    print(f"here: {connected_clients}")
    try:
        # Listen for messages from the client
        async for message in websocket:
            # Broadcast the message to all other connected clients
            count=0
            for client in connected_clients:
                if client != websocket:
                    await client.send(message)
                    print(f"Sending message to client: {message}")
                else:
                    print(f"client not websocket")
    except websockets.exceptions.ConnectionClosed as e:
        pass
        print(f"websocket passed {e}")
    finally:
        # Remove the client from the set of connected clients
        connected_clients.remove(websocket)
        print(f"websocket removed")

# Main function to start the WebSocket server
async def main():
    print(f"starting webserver socket....")
    host = os.getenv("WEBSOCKET_HOST")
    print(f"HOST: {host}")
    port = int(os.getenv("WEBSOCKET_PORT", "8765"))
    print(f"PORT: {port}")
    if host:
        server = await websockets.serve(handle_client, host=host, port=port)
        print(f"server started on {host}:{port}")
    else:
        server = await websockets.serve(handle_client, port=port)
        print(f"server started on port: {port}")
    await server.wait_closed()

# Run the server
if __name__ == "__main__":
    asyncio.run(main())