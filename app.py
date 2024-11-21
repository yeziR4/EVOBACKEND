from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Flask app is running in a clean environment!"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    playlists = data.get("playlists", [])
    tracks = data.get("tracks", [])

    # Example Analysis: Count tracks per playlist
    analysis = {
        "total_playlists": len(playlists),
        "total_tracks": len(tracks),
        "playlists": [
            {
                "name": playlist["name"],
                "track_count": sum(1 for track in tracks if track["id"] in [t["id"] for t in tracks]),
            }
            for playlist in playlists
        ],
    }

    return jsonify(analysis)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
