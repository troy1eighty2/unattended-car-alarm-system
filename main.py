#!/usr/bin/env python3
import asyncio
from multiprocessing import Process, Queue
from src.connection import run_client
from src.ai_camera import run_ai_camera

async def main():
  queue = Queue()
  ai_camera = Process(target=run_ai_camera, args=(queue,), daemon=True)

  ai_camera.start()
  await run_client(queue)

if __name__ == "__main__":
  asyncio.run(main())
