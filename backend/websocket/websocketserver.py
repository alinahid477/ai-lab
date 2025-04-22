import asyncio
import websockets

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
    server = await websockets.serve(handle_client, 'localhost', 8765)
    print("server started on port localhost:8765")
    await server.wait_closed()

# Run the server
if __name__ == "__main__":
    asyncio.run(main())