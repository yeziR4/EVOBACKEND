from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Flask app is running in a clean environment!"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        playlists = data.get("playlists", [])
        tracks = data.get("tracks", [])

        # Example analysis: Count total tracks per playlist
        analysis = {
            "total_playlists": len(playlists),
            "total_tracks": len(tracks),
            "result": [
                {
                    "playlist_name": playlist["name"],
                    "track_count": sum(
                        1 for track in tracks if track.get("playlist_id") == playlist.get("id")
                    ),
                }
                for playlist in playlists
            ],
        }

        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
