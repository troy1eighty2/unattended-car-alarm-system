#!/usr/bin/env python3
import asyncio
from multiprocessing import Process, Queue
from src.connection import run_client

from src.ai_camera import run_ai_camera
from src.object_detection import run_detection
from src.wifi_strength import run_wifi_strength
from src.sys_info import run_sys_info

from src.temperature_sensor import run_temperature_sensor
from src.cpu_temperature import run_cpu_temperature

async def main():
  ai_queue = Queue()
  detection_queue = Queue()
  sys_info_queue = Queue()

  temp_queue = Queue()
  cpu_temp_queue = Queue()
  wifi_queue = Queue()

  temperature_sensor = Process(target=run_temperature_sensor, args=(temp_queue,), daemon=True)
  cpu_temperature = Process(target=run_cpu_temperature, args=(cpu_temp_queue,), daemon=True)
  wifi = Process(target=run_wifi_strength, args=(wifi_queue,), daemon=True)
  sys_info = Process(target=run_sys_info, args=(sys_info_queue,), daemon=True)

  ai_camera = Process(target=run_detection, args=(ai_queue, detection_queue), daemon=True)
  #ai_camera = Process(target=run_ai_camera, args=(ai_queue,), daemon=True)

  ai_camera.start()
  temperature_sensor.start()
  cpu_temperature.start()
  wifi.start()
  sys_info.start()

  await run_client(ai_queue, temp_queue, cpu_temp_queue, wifi_queue, detection_queue, sys_info_queue)

if __name__ == "__main__":
  asyncio.run(main())
