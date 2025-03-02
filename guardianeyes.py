import cv2
import numpy as np
import board
import busio
import adafruit_mlx90640
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pynmea2
import serial
import time
from picamera2.devices import imx500
from picamera2 import Picamera2

# Thermal camera initial set up
i2c = busio.I2C(board.SCL, board.SDA)
mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ

def display_thermal_cv():
	frame_data = np.zeros((24 * 32,))
	while True:
		try:
			start_time = time.monotonic()
			mlx.getFrame(frame_data)
			elapsed_time = time.monotonic() - start_time
			print(f"Frame time: {elapsed_time:.3f} sec")
			img = np.reshape(frame_data, (24, 32))
			img = cv2.resize(img, (320, 240), interpolation = cv2.INTER_CUBIC)
			img = cv2.applyColorMap(np.uint8(img * 255 / np.max(img)), cv2.COLORMAP_INFERNO)
			cv2.imshow('Thermal view', img)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		except ValueError:
			pass
	cv2.destroyAllWindows()

display_thermal_cv()

# Open serial connection
gps = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)

def read_gps():
	while True:
		data = gps.readline().decode('ascii', errors='ignore')
		if data.startswith('$GPGGA') or data.startswith('$GPRMC'):
			# Print raw GPS data
			try:
				msg = pynmea2.parse(data)
				print(f"Latitude: {msg.latitude}, Longitude: {msg.longitude}")
			except pynmea2.ParseError:
				print("Parse error")

try:
	read_gps()
except KeyboardInterrupt:
	print("Stopping GPS reader")
	gps.close()

# Initialize Camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
config["controls"]["FrameRate"] = 30 # FPS
picam2.configure(config)
picam2.start()

# Threshold confidence (adjust as needed)
CONFIDENCE_THRESHOLD = 0.5

# Load labels (modify if needed)
LABELS = {0: "Person", 1: "Pet", 2: "Other"}

def detect_objects():
    """Detect objects using IMX500 AI inference."""
    request = picam2.capture_request()
    metadata = request.get_metadata()
    outputs = imx500.get_outputs(metadata)
    request.release()

    if not outputs:
        return []

    detections = []
    boxes, scores, classes = outputs[0][0], outputs[1][0], outputs[2][0]

    for box, score, category in zip(boxes, scores, classes):
        if score > CONFIDENCE_THRESHOLD:
            x, y, w, h = box
            label = LABELS.get(int(category), "Unknown")
            detections.append((x, y, w, h, label, score))
    
    return detections

# Run Detection Loop
while True:
    detections = detect_objects()
    if detections:
        print("Detections:", detections)
