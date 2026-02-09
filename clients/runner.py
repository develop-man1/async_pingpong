import asyncio
import multiprocessing
from client import AsyncClient
from config import RUN_DURATION


def run_client(client_id: int):
    
    async def main():
        client = AsyncClient(client_id)
        await client.run()

    asyncio.run(main())


if __name__ == "__main__":
    processes = []

    for cid in range(1, 3):
        p = multiprocessing.Process(target=run_client, args=(cid,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print("Both clients stopped")