from flask import Flask, request
import requests

app = Flask(__name__)
AREA_TO_REGION = {
    "yishun": "north", 
    "marina bay": "south", 
    "bedok": "east", 
    "jurong": "west",
    "orchard": "central"
}
@app.route("/haze")

def haze():
    response = requests.get("https://api.data.gov.sg/v1/environment/psi")
    data = response.json()
    psi = data["items"][0]["readings"]["psi_twenty_four_hourly"]
    
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

    return {"query": query, "region": region, "psi": psi[region]}

if __name__ == "__main__":
    app.run(port=8080, debug=True)