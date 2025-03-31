from multiprocessing import Process, Queue
import time
def run_cpu_temperature(queue):
  print("[Starting] CPU Temperature")
  print("[Online] CPU Temperature")
  while True:
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
      temp_str = file.read().strip()
      print(temp_str)
      queue.put(float(temp_str))
    time.sleep(2) 
  
