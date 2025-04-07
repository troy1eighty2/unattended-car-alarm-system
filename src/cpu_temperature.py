from multiprocessing import Process, Queue
import time
import psutil
def run_cpu_temperature(queue):
  print("[Starting] CPU Temperature")
  print("[Online] CPU Temperature")
  while True:
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
      temp_str = file.read().strip()
      temp_f =(float(temp_str) * (9/5)) + 32
      queue.put(temp_f)
    time.sleep(2) 
  
