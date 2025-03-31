#!/usr/bin/env python3
import asyncio
from multiprocessing import Process, Queue
from src.connection import run_client
from src.ai_camera import run_ai_camera
from src.thermal_camera import run_thermal_camera
from src.temperature_sensor import run_temperature_sensor
from src.cpu_temperature import run_cpu_temperature

async def main():
  ai_queue = Queue()
  temp_queue = Queue()
  cpu_temp_queue = Queue()

  ai_camera = Process(target=run_ai_camera, args=(ai_queue,), daemon=True)
  temperature_sensor = Process(target=run_temperature_sensor, args=(temp_queue,), daemon=True)
  cpu_temperature = Process(target=run_cpu_temperature, args=(cpu_temp_queue,), daemon=True)

  ai_camera.start()
  temperature_sensor.start()
  cpu_temperature.start()

  await run_client(ai_queue, temp_queue, cpu_temp_queue)

if __name__ == "__main__":
  asyncio.run(main())
