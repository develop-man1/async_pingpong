import asyncio
from typing import Dict
from datetime import datetime

from config import (SERVER_IGNORE_PROBABILITY, SERVER_RESPONSE_MIN_DELAY,SERVER_RESPONSE_MAX_DELAY)
from utils import sleep_random, should_ignore, build_pong, build_keepalive
from server.logger import log_request


class ServerHandler:

    def __init__(self):
        self.response_counter = 0 
        self.clients: Dict[int, asyncio.StreamWriter] = {}
        self.next_client_id = 1
        self.lock = asyncio.Lock()

    def register_client(self, writer: asyncio.StreamWriter) -> int:
        
        client_id = self.next_client_id
        self.clients[client_id] = writer
        self.next_client_id += 1
        return client_id

    def unregister_client(self, client_id: int):

        self.clients.pop(client_id, None)

    async def handle_ping(
        self, 
        message: str, 
        client_id: int, 
        writer: asyncio.StreamWriter, 
        request_time: datetime
    ):
        
        if should_ignore(SERVER_IGNORE_PROBABILITY):
            log_request(request_text=message, ignored=True, request_time=request_time)
            return

        try:
            request_id = int(message.strip()[1:].split("]")[0])
        except Exception:
            log_request(request_text=message, ignored=True, request_time=request_time)
            return

        await sleep_random(SERVER_RESPONSE_MIN_DELAY, SERVER_RESPONSE_MAX_DELAY)

        async with self.lock:
            response_id = self.response_counter
            self.response_counter += 1

        response_text = build_pong(response_id, request_id, client_id)
        response_time = datetime.now()

        try:
            writer.write((response_text + "\n").encode("ascii"))
            await writer.drain()
        except Exception:
            return

        log_request(
            request_text=message,
            response_text=response_text,
            ignored=False,
            request_time=request_time,
            response_time=response_time,
        )

    async def send_keepalive(self):

        for client_id, writer in list(self.clients.items()):
            try:
                async with self.lock:
                    response_id = self.response_counter
                    self.response_counter += 1
                
                msg = build_keepalive(response_id)
                writer.write((msg + "\n").encode("ascii"))
                await writer.drain()
            except Exception:
                pass