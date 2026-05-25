import json, os, time
import urllib.request

api_key = os.environ["AWN_API_KEY"]
app_key = os.environ["AWN_APP_KEY"]
mac     = os.environ["AWN_MAC"].upper()

url = f"https://api.ambientweather.net/v1/devices?apiKey={api_key}&applicationKey={app_key}"
with urllib.request.urlopen(url) as r:
    devices = json.load(r)

device = next((d for d in devices if d.get("macAddress","").upper() == mac), devices[0])
data   = device.get("lastData", {})

output = {
    "updatedAt": int(time.time() * 1000),
    "station":   device.get("info", {}).get("name", "Weather Station"),
    "mac":       device.get("macAddress", ""),
    "current":   data
}

with open("weather-data.json", "w") as f:
    json.dump(output, f)

print(f"Saved weather-data.json for {output['station']}")
