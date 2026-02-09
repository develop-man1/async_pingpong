import asyncio
import random
from datetime import datetime


def current_date() -> str:
    
    return datetime.now().strftime("%Y-%m-%d")


def current_time() -> str:
    
    now = datetime.now()
    
    return now.strftime("%H:%M:%S.") + f"{now.microsecond // 1000:03d}"


async def sleep_random(min_seconds: float, max_seconds: float) -> None:
    
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)
    
    
def should_ignore(probability: float) -> bool:
    
    return random.random() < probability


def parse_ping(message: str) -> int:
    
    message = message.strip()
    
    if not message.startswith("[") or "]" not in message:
        raise ValueError("Invalid PING format")
    
    number_part, command = message.split("]", 1)
    number = int(number_part[1:])
    
    if command.strip() != "PING":
        raise ValueError("Invalid command")
    
    return number


def build_pong(response_id: int, request_id: int, client_id: int) -> str:
    
    return f"[{response_id}.{request_id}] PONG ({client_id})"


def build_keepalive(response_id: int) -> str:
    
    return f"[{response_id}] keepalive"