from picamera2 import Picamera2
import time

picam2 = Picamera2()
picam2.configure(picam2.preview_configuration)
picam2.start()

while True:

  time.sleep(2)
  frame = picam2.capture_array()
  print(frame)

