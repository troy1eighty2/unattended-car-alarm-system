import psutil
import re
import time

def run_sys_info(queue):
  while True:
    try:
      cpu_usage = psutil.cpu_percent(interval=1)
      usage= str(psutil.virtual_memory())
      match = re.search(r"percent=(\d+\.?\d*)", usage)
      ram_usage = float(match.group(1)) if match else None
      print("qqq")
      print(cpu_usage)
      print(ram_usage)
      print("qqq")
      queue.put((cpu_usage, ram_usage))
    except Exception as e:
      print("[Error] System Info: failed to get info")
    time.sleep(5)




