import asyncio
from multiprocessing import Process, Queue
from src.connection import run_client
# from src.connection import run_client

async def main():
  queue = Queue()
  # Process(target=ai_camera_worker, args=(queue,), daemon=True).start()
  await run_client(queue)

if __name__ == "__main__":
  asyncio.run(main())
