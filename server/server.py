import asyncio
from datetime import datetime
from config import HOST, PORT, KEEPALIVE_INTERVAL, RUN_DURATION
from .handlers import ServerHandler
from utils import current_time

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, handler: ServerHandler):

    client_id = handler.register_client(writer)
    addr = writer.get_extra_info('peername')
    print(f"[{current_time()}] Client {client_id} connected: {addr}")

    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            message = data.decode("ascii").rstrip("\n")
            request_time = datetime.now()
            
            await handler.handle_ping(message, client_id, writer, request_time)
    except asyncio.CancelledError:
        pass
    finally:
        print(f"[{current_time()}] Client {client_id} disconnected")
        handler.unregister_client(client_id)
        writer.close()
        await writer.wait_closed()


async def keepalive_loop(handler: ServerHandler):

    try:
        while True:
            await asyncio.sleep(KEEPALIVE_INTERVAL)
            await handler.send_keepalive()
    except asyncio.CancelledError:
        pass


async def main():
    
    handler = ServerHandler()

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, handler),
        HOST,
        PORT
    )

    addr = server.sockets[0].getsockname()
    print(f"[{current_time()}] Serving on {addr}")

    keepalive_task = asyncio.create_task(keepalive_loop(handler))
    server_task = asyncio.create_task(server.serve_forever())
    stop_task = asyncio.create_task(asyncio.sleep(RUN_DURATION))

    async with server:
        done, pending = await asyncio.wait(
            [server_task, stop_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        for task in pending:
            task.cancel()

    keepalive_task.cancel()
    try:
        await keepalive_task
    except asyncio.CancelledError:
        pass

    print(f"[{current_time()}] Server stopped")


if __name__ == "__main__":
    asyncio.run(main())