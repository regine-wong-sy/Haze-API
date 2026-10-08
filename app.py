from flask import Flask, request
import requests
import time
app = Flask(__name__)

cached_psi = None
cached_at = 0
CACHE_SECONDS = 10 * 60 #number of minutes * seconds per minute


AREA_TO_REGION = {
    "yishun": "north", 
    "marina bay": "south", 
    "bedok": "east", 
    "jurong": "west",
    "orchard": "central"
}

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

@app.route("/haze")

def haze():
    #caching
    global cached_psi, cached_at
    curr_time = time.time()
    #if nothing cached, cache now
    if cached_psi is None or (curr_time-cached_at)>CACHE_SECONDS:
        response = requests.get("https://api.data.gov.sg/v1/environment/psi")
        data = response.json()
        psi = data["items"][0]["readings"]["psi_twenty_four_hourly"]
        cached_at = curr_time
        cached_psi = psi
        print("Fetching from NEA")
    
    #psi from cached
    psi = cached_psi
    #Reads the URL. Now region is "bedok".
    region = request.args.get("region")
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

if __name__ == "__main__":
    app.run(port=8080, debug=True)