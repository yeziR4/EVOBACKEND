from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import Counter, defaultdict

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Analysis API is running!"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()

        # Validate input
        if not data or "playlists" not in data or "tracks" not in data:
            return jsonify({"error": "Invalid input data"}), 400

        playlists = data["playlists"]
        tracks_data = data["tracks"]

        # Organize data
        tracks_by_year = defaultdict(list)
        all_tracks = []

        for track in tracks_data:
            year = track.get("year")
            if year:
                tracks_by_year[year].append(track)
            all_tracks.append(track)

        # Analysis Functions
        def constant_artists_across_years():
            """Identify artists that appear in all playlists."""
            artists_by_year = {
                year: set(artist for track in tracks for artist in track["artists"])
                for year, tracks in tracks_by_year.items()
            }
            if not artists_by_year:
                return []
            return list(set.intersection(*artists_by_year.values()))

        def genre_consistency_and_evolution():
            """Analyze genre trends across years."""
            genres_by_year = {
                year: [genre for track in tracks for genre in track.get("genres", [])]
                for year, tracks in tracks_by_year.items()
            }
            return {year: Counter(genres) for year, genres in genres_by_year.items()}

        def persisting_songs():
            """Identify songs appearing in multiple playlists."""
            track_counts = Counter(track["name"] for track in all_tracks)
            return [track for track, count in track_counts.items() if count > 1]

        def abandoned_artists_or_genres():
            """Find artists or genres that declined over time."""
            artists_by_year = {
                year: [artist for track in tracks for artist in track["artists"]]
                for year, tracks in tracks_by_year.items()
            }
            all_artists = set(artist for artists in artists_by_year.values() for artist in artists)
            abandoned_artists = {
                artist for artist in all_artists if sum(artist in artists for artists in artists_by_year.values()) == 1
            }

            genres_by_year = {
                year: [genre for track in tracks for genre in track.get("genres", [])]
                for year, tracks in tracks_by_year.items()
            }
            all_genres = set(genre for genres in genres_by_year.values() for genre in genres)
            abandoned_genres = {
                genre for genre in all_genres if sum(genre in genres for genres in genres_by_year.values()) == 1
            }

            return {"artists": list(abandoned_artists), "genres": list(abandoned_genres)}

        def most_consistent_songs():
            """Find songs appearing every year."""
            songs_by_year = {year: set(track["name"] for track in tracks) for year, tracks in tracks_by_year.items()}
            if not songs_by_year:
                return []
            return list(set.intersection(*songs_by_year.values()))

        # Aggregate Results
        analysis_result = {
            "constant_artists": constant_artists_across_years(),
            "genre_consistency": genre_consistency_and_evolution(),
            "persisting_songs": persisting_songs(),
            "abandoned": abandoned_artists_or_genres(),
            "consistent_songs": most_consistent_songs(),
        }

        return jsonify(analysis_result)

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
