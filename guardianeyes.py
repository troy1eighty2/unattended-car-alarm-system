import cv2
import numpy as np
import board
import busio
import adafruit_mlx90640
import serial
import time
import threading
import pynmea2
from picamera2 import Picamera2
import os

# ====== Initialize AI Camera (IMX500) ======
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
config["controls"]["FrameRate"] = 30  # FPS
picam2.configure(config)

# Confidence Threshold
CONFIDENCE_THRESHOLD = 0.3

# Labels for detection
LABELS = {0: "Person", 1: "Pet", 2: "Other"}

# ====== Initialize Thermal Camera (MLX90640) ======
i2c = busio.I2C(board.SCL, board.SDA)
mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ

# ====== Initialize GPS ======
gps = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)

def capture_ai_image():
    """Captures an image using the AI Camera."""
    image_path = f"detected_ai_{int(time.time())}.jpg"
    picam2.start()
    time.sleep(1)  # Allow camera to adjust
    picam2.capture_file(image_path)
    picam2.stop()
    print(f"AI Image saved: {image_path}")
    return image_path

def detect_objects():
    """Runs AI detection and captures image if a person/pet is found."""
    print("AI Camera: Running object detection...")

    while True:
        request = picam2.capture_request()
        metadata = request.get_metadata()
        request.release()
        
        print("Metadata: ", metadata)
        if "objects" in metadata and metadata["objects"]:
            for detection in metadata["objects"]:
                x, y, w, h = detection["bbox"]
                label = LABELS.get(detection["label"], "Unknown")
                conf = detection["confidence"]

                if conf > CONFIDENCE_THRESHOLD:
                    print(f"AI Detection: {label} ({conf:.2f}) at [{x}, {y}, {w}, {h}]")

                    # Save AI image and stop AI camera
                    image_path = capture_ai_image()
                    return image_path  # Stop AI detection and return image path

def capture_thermal_image():
    """Captures thermal image and saves it."""
    print("Thermal Camera: Capturing infrared image...")
    frame_data = np.zeros((24 * 32,))

    # Capture one thermal frame
    try:
        mlx.getFrame(frame_data)
        img = np.reshape(frame_data, (24, 32))
        img = cv2.resize(img, (320, 240), interpolation=cv2.INTER_CUBIC)
        img = cv2.applyColorMap(np.uint8(img * 255 / np.max(img)), cv2.COLORMAP_INFERNO)
        
        # Save the thermal image
        thermal_image_path = f"thermal_{int(time.time())}.jpg"
        cv2.imwrite(thermal_image_path, img)
        print(f"Thermal Image saved: {thermal_image_path}")

        return thermal_image_path
    except ValueError:
        print("Thermal camera error.")
        return None

def read_gps():
    """Reads GPS coordinates."""
    print("GPS: Fetching coordinates...")
    while True:
        data = gps.readline().decode('ascii', errors='ignore')
        if data.startswith('$GPGGA') or data.startswith('$GPRMC'):
            try:
                msg = pynmea2.parse(data)
                gps_data = f"Latitude: {msg.latitude}, Longitude: {msg.longitude}"
                print(gps_data)
                return gps_data
            except pynmea2.ParseError:
                print("GPS Parse Error.")

# ====== Main Process ======
if __name__ == "__main__":
    print("Starting Unattended Car Alarm System...")

    # Step 1: AI Camera Runs First
    ai_image_path = detect_objects()
    
    if ai_image_path:
        print("Person/Pet detected! Switching to thermal camera...")
        time.sleep(1)

        # Step 2: Run Thermal Camera
        thermal_image_path = capture_thermal_image()

        # Step 3: Capture GPS Coordinates
        gps_data = read_gps()

        # Step 4: Save Data for Transmission
        alert_data = {
            "AI_Image": ai_image_path,
            "Thermal_Image": thermal_image_path,
            "GPS_Coordinates": gps_data,
        }

        # Print or save the data
        print("Alert Data Saved:", alert_data)

    else:
        print("No detection. System is idle.")
