#!/usr/bin/env python3
# ai camera
from picamera2 import Picamera2
import time

def run_ai_camera(queue):
  
  print("[Starting] AI Camera")
  picam2 = Picamera2()
  picam2.configure(picam2.preview_configuration)
  picam2.start()
  print("[Online] AI Camera")
  
  while True:
    frame = picam2.capture_array()
    # print(frame)
    queue.put(frame)
