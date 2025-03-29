# thermal camera
#!/usr/bin/env python3
import adafruit_mlx90640
import time
import busio
import board

def run_thermal_camera(queue):
  print("[Starting] Thermal Camera")
  print("[Online] Thermal Camera")

  i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)  # 400kHz I2C
  mlx = adafruit_mlx90640.MLX90640(i2c)
  mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_8_HZ

  print("MLX90640 initialized with refresh rate: 8Hz")
  frame = np.zeros((24 * 32,))

  try:
    while True:
      try:
        mlx.getFrame(frame)
        queue.put(frame.copy())
      except ValueError:
        print("Frame dropped")
        continue
  except KeyboardInterrupt:
    print("Ending thermal camera process")

