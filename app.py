from flask import Flask, request
import requests

app = Flask(__name__)

@app.route("/haze")

def haze():
    response = requests.get("https://api.data.gov.sg/v1/environment/psi")
    data = response.json()
    psi = data["items"][0]["readings"]["psi_twenty_four_hourly"]
    
    region = request.args.get("region")
    if region not in psi:
        return {"error": "Invalid Region",
                "valid_regions": list(psi.keys())
        }, 400

    return {"region": region, "psi": psi[region]}

if __name__ == "__main__":
    app.run(port=8080, debug=True)