from flask import Flask

app = Flask(__name__)

@app.route("/haze")

def haze():
    return "Haze endpoint works!"

if __name__ == "__main__":
    app.run(port=8080, debug=True)