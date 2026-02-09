import asyncio
from datetime import datetime
from config import HOST, PORT, PING_MIN_INTERVAL, PING_MAX_INTERVAL, RUN_DURATION
from utils import sleep_random
from clients.logger import log_client_event

PING_TIMEOUT = 5.0


class AsyncClient:
    
    def __init__(self, client_id: int):
        self.client_id = client_id
        self.request_counter = 0
        self.running = True
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.pending_requests: dict[int, tuple[datetime, asyncio.Event, str]] = {}

    async def connect(self):
        
        self.reader, self.writer = await asyncio.open_connection(HOST, PORT)
        print(f"Client {self.client_id} connected to server")

    async def send_ping(self):
        
        if not self.writer:
            return

        request_id = self.request_counter
        message = f"[{request_id}] PING"
        request_time = datetime.now()

        response_event = asyncio.Event()
        self.pending_requests[request_id] = (request_time, response_event, "")

        self.writer.write((message + "\n").encode("ascii"))
        await self.writer.drain()

        try:
            await asyncio.wait_for(response_event.wait(), timeout=PING_TIMEOUT)
        except asyncio.TimeoutError:
            response_time = datetime.now()
            log_client_event(
                client_id=self.client_id,
                request_text=message,
                response_text="",
                request_time=request_time,
                response_time=response_time,
                timeout=True
            )
            
            self.pending_requests.pop(request_id, None)

        self.request_counter += 1

    async def handle_server_messages(self):
        
        if not self.reader:
            return

        try:
            while self.running:
                data = await self.reader.readline()
                if not data:
                    break
                
                message = data.decode("ascii").rstrip("\n")
                response_time = datetime.now()

                if "keepalive" in message:
                    log_client_event(
                        client_id=self.client_id,
                        keepalive=True,
                        response_text=message,
                        response_time=response_time
                    )
                
                elif "PONG" in message:
                    try:
                        bracket_content = message.split("]")[0][1:]  # "0/3"
                        request_id = int(bracket_content.split("/")[1])  # 3
                        
                        if request_id in self.pending_requests:
                            request_time, event, _ = self.pending_requests[request_id]
                            
                            log_client_event(
                                client_id=self.client_id,
                                request_text=f"[{request_id}] PING",
                                response_text=message,
                                request_time=request_time,
                                response_time=response_time
                            )
                            
                            event.set()
                            
                            del self.pending_requests[request_id]
                    
                    except (ValueError, IndexError):
                        pass

        except asyncio.CancelledError:
            pass

    async def run(self):
        
        await self.connect()

        reader_task = asyncio.create_task(self.handle_server_messages())

        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < RUN_DURATION:
            await self.send_ping()
            await sleep_random(PING_MIN_INTERVAL, PING_MAX_INTERVAL)

        self.running = False
        reader_task.cancel()
        try:
            await reader_task
        except asyncio.CancelledError:
            pass

        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        
        print(f"Client {self.client_id} stopped")