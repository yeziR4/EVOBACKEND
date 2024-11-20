from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Flask app is running in a clean environment!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
