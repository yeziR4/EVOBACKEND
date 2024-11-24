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

        if not data or "playlists" not in data:
            return jsonify({"error": "Invalid input data"}), 400

        playlists = data.get("playlists", [])
        tracks_data = data.get("tracks", [])

        tracks_by_year = defaultdict(list)
        all_tracks = []

        for track in tracks_data:
            year = track.get("year")
            if year:
                tracks_by_year[year].append(track)
            all_tracks.append(track)

        def constant_artists_across_years():
            artists_by_year = {
                year: set(artist for track in tracks for artist in track["artists"])
                for year, tracks in tracks_by_year.items()
            }
            if not artists_by_year:
                return []
            return list(set.intersection(*artists_by_year.values()))

        def genre_consistency_and_evolution():
            genres_by_year = {
                year: [genre for track in tracks for genre in track.get("genres", [])]
                for year, tracks in tracks_by_year.items()
            }
            return {year: Counter(genres) for year, genres in genres_by_year.items()}

        def persisting_songs():
            track_counts = Counter(track["name"] for track in all_tracks)
            return [track for track, count in track_counts.items() if count > 1]

      

        def most_consistent_songs():
            songs_by_year = {year: set(track["name"] for track in tracks) for year, tracks in tracks_by_year.items()}
            if not songs_by_year:
                return []
            return list(set.intersection(*songs_by_year.values()))

       
            
        def artist_growth():
            artist_year_counts = defaultdict(Counter)
            for year, tracks in tracks_by_year.items():
                for track in tracks:
                    for artist in track["artists"]:
                        artist_year_counts[artist][year] += 1

            artist_growth = {}
            artist_decline = {}
            for artist, year_counts in artist_year_counts.items():
                years = sorted(year_counts.keys())
                for i in range(1, len(years)):
                    growth_rate = (year_counts[years[i]] - year_counts[years[i-1]]) / (year_counts[years[i-1]] or 1) * 100
                    if growth_rate > 0:
                        artist_growth[artist] = growth_rate
                    else:
                        artist_decline[artist] = abs(growth_rate)

            top_growing_artists = sorted(artist_growth.items(), key=lambda x: x[1], reverse=True)[:5]
            top_declining_artists = sorted(artist_decline.items(), key=lambda x: x[1], reverse=True)[:5]

            # Remove overlapping artists
            top_declining_artists = [artist for artist in top_declining_artists if artist[0] not in [artist[0] for artist in top_growing_artists]]

            return top_growing_artists, top_declining_artists

       

        def artists_through_features():
                feature_counts = Counter()
                for track in all_tracks:
                    if not track["artists"]:  # Check for empty list
                        continue

                    if isinstance(track["artists"], list):
                        artists = track["artists"]
                    else:
                        artists = track["artists"].split(",")  # Split if it's a string
                    print(f"Artist data: {artists}")

                    main_artist = artists[0]
                    feature_artists = artists[1:]
                    for artist in feature_artists:
                        feature_counts[artist] += 1
                    print(f"Feature counts: {feature_counts}")  # Check function execution

                # ... other function logic

                return feature_counts








        analysis_result = {
            "constant_artists": constant_artists_across_years(),
            "genre_consistency": genre_consistency_and_evolution(),
            "persisting_songs": persisting_songs(),
            
            "consistent_songs": most_consistent_songs(),
            "top_growing_artists": artist_growth()[0],
            "top_declining_artists": artist_growth()[1],
            "artists_through_features": artists_through_features(),
        }

        return jsonify(analysis_result)

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
