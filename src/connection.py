#!/usr/bin/env python3
import socketio
from dotenv import load_dotenv
import os
import time
import asyncio
import cv2
import base64
from datetime import datetime
from pathlib import Path

from src.sms import run_sms
from src.history import run_write_json, run_update_json, run_package_json, run_write_pictures, run_package_pictures

async def run_client(ai_queue, temp_queue, cpu_temp_queue, wifi_queue, detections_queue, sys_info_queue):
  env_path = Path(__file__).resolve().parent.parent/ ".env"
  load_dotenv(env_path)
  sio = socketio.AsyncClient()
  emergency = False
  shutdown = False

  async def send_frames_ai():
    while True:
      if ai_queue.qsize() > 0:
        frame = ai_queue.get()
        success, buffer = cv2.imencode(".jpg",frame)
        if success:
          # encode base64
          frame_b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")
          await sio.emit("frame", frame_b64)
        await asyncio.sleep(.01)
  
  async def send_temp():
    while True:
      if temp_queue.qsize() > 0:
        temp = temp_queue.get()
        T = round(((temp[0] * (9/5)) + 32),2)
        RH = temp[1]
        heat_index = -42.379 + 2.04901523*T + 10.14333127*RH - .22475541*T*RH - .00683783*T*T - .05481717*RH*RH + .00122874*T*T*RH + .00085282*T*RH*RH - .00000199*T*T*RH*RH
        heat_index = round(heat_index, 2)

        await sio.emit("temp",[T, RH, heat_index])
      await asyncio.sleep(3)

  async def send_cpu_temp():
    while True:
      if cpu_temp_queue.qsize() > 0:
        temp = cpu_temp_queue.get()
        await sio.emit("cpu_temp",round((temp/1000),2))
      await asyncio.sleep(5)

  async def send_runtime():
    time = 0
    while True:
      time = time + 1
      print(time)
      await sio.emit("uptime", time)
      await asyncio.sleep(1)

  async def send_wifi_strength():
    while True:
      if wifi_queue.qsize() > 0:
        strength = wifi_queue.get()
        await sio.emit("wifi_strength", strength)
        await asyncio.sleep(5)

  async def send_detections():
    nonlocal emergency
    while True:
      if detections_queue.qsize() > 0:
        detections = detections_queue.get()
        if detections:
          emergency = True
          shutdown = True
        await sio.emit("detections", detections)
        await asyncio.sleep(0.01)

  async def send_sys_info():
    while True:
      if sys_info_queue.qsize() > 0:
        info = sys_info_queue.get()
        await sio.emit("sys_info", [info[0], info[1]])
        await asyncio.sleep(5)

  async def send_config():
    await sio.emit("config", [os.getenv('LOCATION'), os.getenv('GPS_CONNECTION_STRENGTH')])

  async def countdown():
    pass

  async def send_emergency():
    while True:
      if emergency:
        break
      await asyncio.sleep(0.01)

    print("SUBJECT DETECTED")
    detections = detections_queue.get()

    print("DETECTIONS GRABBED")
    picture = ai_queue.get()
    success, buffer = cv2.imencode(".jpg", picture)
    frame_b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")

    print("PICTURE GRABBED")
    temperature = temp_queue.get()
    T = round(((temperature[0] * (9/5)) + 32),2)
    time = datetime.now().strftime("%m-%d-%Y %H:%M:%S")

    print("TEMPERATURE GRABBED")
    newDoc = run_write_json(time, T, detections, [os.getenv('LOCATION')])
    newPicture = run_write_pictures(time, frame_b64)


    print("PICTURE AND HISTORY WRITTEN")
    await sio.emit("emergency", True)
    run_sms(picture, T, time, detections)

    await sio.emit("pictures", newPicture)
    await sio.emit("history", newDoc)

  
    
      
      

  SERVER_URL=f"ws://{os.getenv('INDEX_ADDRESS')}:{os.getenv('PORT')}"


# define event handlers for events from server
  async def connect():
    print("Connected to websocket server")
    await sio.emit("message", "I connected")
    await send_config()

    history_data = run_package_json()
    pictures_data = run_package_pictures()
    await sio.emit("history", history_data)
    await sio.emit("pictures", pictures_data)

    asyncio.create_task(send_frames_ai())
    asyncio.create_task(send_temp())
    asyncio.create_task(send_cpu_temp())
    asyncio.create_task(send_runtime())
    asyncio.create_task(send_wifi_strength())
    asyncio.create_task(send_detections())
    asyncio.create_task(send_sys_info())
    asyncio.create_task(send_emergency())
      

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


