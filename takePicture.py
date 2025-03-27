from picamera2 import Picamera2
import time

picam2 = Picamera2()
picam2.configure(picam2.preview_configuration)
picam2.start()
time.sleep(2)
picam2.start_and_record_video("test.mp4", duration=5)
