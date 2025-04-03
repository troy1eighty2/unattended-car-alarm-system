import adafruit_dht
import board
import time

# Initialize the DHT22 sensor (use the GPIO pin connected to the signal wire)
def run_temperature_sensor(queue):
  print("[Starting] Temperature Sensor")
  dht_device = adafruit_dht.DHT22(board.D26)  # GPIO4 (Pin 7 on Raspberry Pi)
  print("[Online] Temperature Sensor")

  try:
    while True:
      try:
        temperature = dht_device.temperature  # Read temperature in Celsius
        humidity = dht_device.humidity  # Read humidity

        if temperature is not None and humidity is not None:
          queue.put((temperature,humidity))
        else:
          print("Failed to retrieve data from the sensor")

        time.sleep(2)  # Wait 2 seconds between readings
      except RuntimeError as error:
        print(f"[Error] {error.args[0]}")  # Handle intermittent errors that may occur with DHT sensors
        time.sleep(2.0)
        continue
      time.sleep(2.0)

  except KeyboardInterrupt:
    print("Program stopped by user")


  finally:
    if 'dht_device' in locals():
      dht_device.exit()  # Clean up resources when exiting
