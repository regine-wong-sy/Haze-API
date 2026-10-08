from flask import Flask
import requests

app = Flask(__name__)

@app.route("/haze")

def haze():
    response = requests.get("https://api.data.gov.sg/v1/environment/psi")
    data = response.json()
    psi = data["items"][0]["readings"]["psi_twenty_four_hourly"]
    return psi

if __name__ == "__main__":
    app.run(port=8080, debug=True)