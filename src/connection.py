#!/usr/bin/env python3
import socketio
from dotenv import load_dotenv
import os
import time
import asyncio
import cv2
from pathlib import Path


async def run_client(queue):

  env_path = Path(__file__).resolve().parent.parent/ ".env"
  load_dotenv(env_path)
  sio = socketio.AsyncClient()

  async def send_frames():
    while True:
      if queue.qsize() > 0:
        await sio.emit("frame", "test")
        await asyncio.sleep(.001)


  SERVER_URL=f"ws://{os.getenv('INDEX_ADDRESS')}:{os.getenv('PORT')}"

# define event handlers for events from server
  async def connect():
    print("Connected to websocket server")
    await sio.emit("message", "I connected")
    asyncio.create_task(send_frames())

  async def disconnect():
    print("Disconnecting from websocket server")

  async def message(data):
    print(f"Message from Server: {data}")

  sio.on("connect", connect)
  sio.on("disconnect", disconnect)
  sio.on("message", message)


  try:
    await sio.connect(SERVER_URL)
    await sio.wait()
  except Exception as e:
    print(f"Connection failed X_X: {e} {SERVER_URL}")


