import json
import aiofiles

def run_update_json(timestamp, resolved, authorities):

  with open("data/history.json", "r") as f:
    data = json.load(f)

  for entry in data:
    if entry["timestamp"] == timestamp:
      entry["resolved"] = resolved
      entry["authorities"] = authorities
      break

  with open("data/history.json", "w") as f:
    json.dump(data, f, indent=2)

  return data

async def run_write_json(timestamp, temperature, subjects, location):
  data = {
    "timestamp": timestamp,
    "occupant_detected": subjects,
    "location": location,
    "temperature_farenheit": temperature,
    "resolved": False,
    "authorities": False
  }

  filepath = "data/history.json"

  async with aiofiles.open(filepath, "r") as f:
    contents = await f.read()
    array = json.loads(contents)

  array.append(data)

  async with aiofiles.open(filepath, "w") as f:
    await f.write(json.dumps(array, indent=2))

  return array

async def run_write_pictures(timestamp, image):
  data = {
    "timestamp": timestamp,
    "image": image
  }

  filepath = "data/pictures.json"

  async with aiofiles.open(filepath, "r") as f:
    contents = await f.read()
    array = json.loads(contents)

  array.append(data)

  async with aiofiles.open(filepath, "w") as f:
    await f.write(json.dumps(array, indent=2))

  return array

def run_package_json():
  with open("data/history.json", "r") as f:
    data = json.load(f)

  return data

def run_package_pictures():
  with open("data/pictures.json", "r") as f:
    data = json.load(f)

  return data
  


   
