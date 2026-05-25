import json, os, time
import urllib.request
import urllib.error

api_key = os.environ["AWN_API_KEY"].strip()
app_key = os.environ["AWN_APP_KEY"].strip()
mac     = os.environ["AWN_MAC"].strip().upper()

def fetch_url(url, retries=3):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 65 * (attempt + 1)
                print(f"Rate limited (429), waiting {wait}s before retry {attempt+1}/{retries}...")
                time.sleep(wait)
            else:
                raise
    raise Exception(f"Failed after {retries} retries due to rate limiting")

url = f"https://api.ambientweather.net/v1/devices?apiKey={api_key}&applicationKey={app_key}"
devices = fetch_url(url)
device = next((d for d in devices if d.get("macAddress","").upper() == mac), devices[0])
exact_mac = device["macAddress"]
station = device.get("info", {}).get("name", "Weather Station")
print(f"Fetching rainfall history for: {station} ({exact_mac})")

all_records = []
cutoff_ms = int((time.time() - 366 * 24 * 3600) * 1000)
end_ms = int(time.time() * 1000)
page = 0

while True:
    page += 1
    page_url = "https://api.ambientweather.net/v1/devices/" + exact_mac + "/data?apiKey=" + api_key + "&applicationKey=" + app_key + "&endDate=" + str(end_ms) + "&limit=288"
    print(f"Page {page} → {time.strftime('%Y-%m-%d', time.gmtime(end_ms/1000))}...", flush=True)
    data = fetch_url(page_url)
    if not data:
        print("No more data.")
        break
    all_records.extend(data)
    oldest_ms = data[-1].get("dateutc") or data[-1].get("date")
    print(f"  {len(data)} records, oldest: {time.strftime('%Y-%m-%d', time.gmtime(oldest_ms/1000))}")
    if oldest_ms <= cutoff_ms:
        print("Reached 12-month limit.")
        break
    end_ms = oldest_ms - 1
    time.sleep(1.1)

print(f"Total: {len(all_records)} records fetched.")
cache = {
    "updatedAt": int(time.time() * 1000),
    "station": station,
    "mac": exact_mac,
    "records": all_records,
}
with open("rainfall-cache.json", "w") as f:
    json.dump(cache, f)
print(f"Saved rainfall-cache.json ({len(all_records)} records)")
