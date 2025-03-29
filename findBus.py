import smbus
bus = smbus.SMBus(20)
address = 0x38
try:
  data = bus.read_byte(device)
  print(f"Device fouinud at address:{device:02X}")
except:
  print(f"nothing foudn")
  pass
