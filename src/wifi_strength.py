import subprocess
import re
import time

def run_wifi_strength(queue):
  while True:
    try:
      result = subprocess.check_output(["iwconfig", "wlan0"]).decode()
      strength = re.search(r"Signal level=(-?\d+) dBm",result)
      strength = int(strength.group(1))
      print(strength)
      queue.put(strength)
    except subprocess.CalledProcessError:
      print(f"[Error] Wifi: Failed to run iwconfig")
    except Exception as e:
      print(f"[Error] Wifi: {e}")
    time.sleep(5)

