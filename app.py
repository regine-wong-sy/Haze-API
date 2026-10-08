from flask import Flask, request
import requests
import time
import math
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

cached_psi = None
cached_at = 0
CACHE_SECONDS = 10 * 60 #number of minutes * seconds per minute
cached_regions = None

AREA_TO_REGION = {
    "yishun": "north", 
    "marina bay": "south", 
    "bedok": "east", 
    "jurong": "west",
    "orchard": "central"
}
def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1-lat2)**2+(lon1-lon2)**2)

def nearest_region(lat, lon, regions):
    best_name = None
    best_dist = float("inf")
    for r in regions:
        r_lat = r["label_location"]["latitude"]
        r_lon = r["label_location"]["longitude"]
        d = distance(lat, lon, r_lat, r_lon)
        if d<best_dist:
            best_dist = d
            best_name = r["name"]
    return best_name

def get_level(psi):
    if psi<=50:
        return "Good"
    elif psi<=100:
        return "Moderate"
    elif psi<=200:
        return "Unhealthy"
    elif psi<=300:
        return "Very unhealthy"
    else:
        return "Hazardous"

@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/haze")
def haze():
    #caching
    global cached_psi, cached_at
    global cached_regions
    curr_time = time.time()
    #if nothing cached, cache now
    if cached_psi is None or (curr_time-cached_at)>CACHE_SECONDS:
        response = requests.get("https://api.data.gov.sg/v1/environment/psi")
        data = response.json()
        psi = data["items"][0]["readings"]["psi_twenty_four_hourly"]
        cached_at = curr_time
        cached_psi = psi
        cached_regions = data["region_metadata"]
        print("Fetching from NEA")
    
    #psi from cached
    psi = cached_psi
    #Reads the URL. Now region is "bedok".
    region = request.args.get("region")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if lat is not None and lon is not None:
        try:
            region = nearest_region(float(lat), float(lon), cached_regions)
        except ValueError:
            return {"error": "lat and lon must be numbers"}, 400
    if region is None:
        return {"error": "No region"}, 400
    query = region
    region = region.lower()

    if region in AREA_TO_REGION:
        #AREA_TO_REGION["bedok"] -> "east"
        region = AREA_TO_REGION[region]

    if region not in psi:
        return {"error": "Invalid Region",
                "valid_regions": list(psi.keys())
        }, 400

    return {"query": query, "region": region, "psi": psi[region], "level": get_level(psi[region])}

@app.route("/haze/history")
def haze_history():
    region = request.args.get("region")
    if region is None:
        return {"error": "No region"}, 400
    region = region.lower()
    if region in AREA_TO_REGION:
        region = AREA_TO_REGION[region]

    today = datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y-%m-%d")
    response = requests.get("https://api-open.data.gov.sg/v2/real-time/api/psi",
                            params={"date": today})
    body = response.json()
    items = body["data"]["items"]

    valid = list(items[0]["readings"]["psi_twenty_four_hourly"].keys())
    if region not in valid:
        return {"error": "Invalid Region", "valid_regions": valid}, 400


    readings = []
    for item in items:
        readings.append({
            "time": item["timestamp"],
            "psi": item["readings"]["psi_twenty_four_hourly"][region]   
        })


    readings.reverse()

    return {"region": region, "readings": readings}
if __name__ == "__main__":
    app.run(port=8080, debug=True)