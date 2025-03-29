import smbus

# Bus 10 since it shows 'UU' for the camera
bus = smbus.SMBus(10)

# Address of the camera (commonly 0x69)
address = 0x69

try:
  # Read a byte to test communication
  data = bus.read_byte(address)
  print(f"Device found at 0x{address:02X}, data: {data}")
except Exception as e:
  print(f"Error communicating with device: {e}")

