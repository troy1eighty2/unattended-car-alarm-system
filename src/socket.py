#!/usr/bin/env python3
import socketio
from dotenv import load_dotenv
import os
import time

load_dotenv("../.env")

sio = socketio.Client()


SERVER_URL=f"ws://{os.getenv('INDEX_ADDRESS')}:{os.getenv('PORT')}"

# define event handlers for events from server
def connect():
  print("Connected to websocket server")
  sio.emit("message", "I connected")

def disconnect():
  print("Disconnecting from websocket server")

def message(data):
  print(f"Message from Server: {data}")

sio.on("connect", connect)
sio.on("disconnect", disconnect)
sio.on("message", message)

try:
  sio.connect(SERVER_URL)
  time.sleep(3)
  sio.disconnect()
except Exception as e:
  print(f"Connection failed X_X: {e} {SERVER_URL}")
