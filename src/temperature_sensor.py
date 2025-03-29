import adafruit_dht
import board
import time

# Initialize the DHT22 sensor (use the GPIO pin connected to the signal wire)
def run_temperature_sensor(queue):
  print("[Starting] Temperature Sensor")
  dht_device = adafruit_dht.DHT22(board.D4)  # GPIO4 (Pin 7 on Raspberry Pi)
  print("[Online] Temperature Sensor")

  try:
    while True:
      temperature = dht_device.temperature  # Read temperature in Celsius
      humidity = dht_device.humidity  # Read humidity

      if temperature is not None and humidity is not None:
        # print(f"Temp: {temperature:.1f}°C  Humidity: {humidity:.1f}%")
        queue.put((temperature,humidity))
      else:
        print("Failed to retrieve data from the sensor")

      time.sleep(3)  # Wait 2 seconds between readings

  except KeyboardInterrupt:
    print("Program stopped by user")

  except RuntimeError as error:
    print(error.args[0])  # Handle intermittent errors that may occur with DHT sensors
    time.sleep(3.0)

  finally:
    dht_device.exit()  # Clean up resources when exiting
