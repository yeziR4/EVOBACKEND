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
    data = request.get_json()
    if not data or not data.get("playlists"):
        return jsonify({"error": "No data provided"}), 400

    playlists = data["playlists"]
    tracks_data = data["tracks"]  # Assuming each track has 'name', 'artists', 'genres', etc.

    # Organize data
    playlist_years = {playlist["year"]: playlist["id"] for playlist in playlists}
    tracks_by_year = defaultdict(list)
    all_tracks = []

    for track in tracks_data:
        year = track.get("year")
        tracks_by_year[year].append(track)
        all_tracks.append(track)

    # Analysis Functions
    def constant_artists_across_years():
        """Identify artists that appear in all playlists."""
        artists_by_year = {year: set(track["artists"]) for year, tracks in tracks_by_year.items() for track in tracks}
        common_artists = set.intersection(*artists_by_year.values())
        return list(common_artists)

    def genre_consistency_and_evolution():
        """Analyze genre trends across years."""
        genres_by_year = {year: [genre for track in tracks for genre in track.get("genres", [])]
                          for year, tracks in tracks_by_year.items()}
        return {year: Counter(genres) for year, genres in genres_by_year.items()}

    def persisting_songs():
        """Identify songs appearing in multiple playlists."""
        track_counts = Counter(track["name"] for track in all_tracks)
        return [track for track, count in track_counts.items() if count > 1]

    def abandoned_artists_or_genres():
        """Find artists or genres that declined over time."""
        artists_by_year = {year: [artist for track in tracks for artist in track["artists"]]
                           for year, tracks in tracks_by_year.items()}
        all_artists = set(artist for artists in artists_by_year.values() for artist in artists)
        abandoned_artists = {artist for artist in all_artists if sum(artist in artists for artists in artists_by_year.values()) == 1}

        genres_by_year = {year: [genre for track in tracks for genre in track.get("genres", [])]
                          for year, tracks in tracks_by_year.items()}
        all_genres = set(genre for genres in genres_by_year.values() for genre in genres)
        abandoned_genres = {genre for genre in all_genres if sum(genre in genres for genres in genres_by_year.values()) == 1}

        return {"artists": list(abandoned_artists), "genres": list(abandoned_genres)}

    def most_consistent_songs():
        """Find songs appearing every year."""
        songs_by_year = {year: set(track["name"] for track in tracks) for year, tracks in tracks_by_year.items()}
        consistent_songs = set.intersection(*songs_by_year.values())
        return list(consistent_songs)

    def new_vs_old():
        """Analyze new vs. old tracks."""
        unique_tracks_by_year = {year: set(track["name"] for track in tracks) for year, tracks in tracks_by_year.items()}
        result = {}
        for year, current_tracks in unique_tracks_by_year.items():
            previous_tracks = set(track for yr, track_set in unique_tracks_by_year.items() if yr < year for track in track_set)
            new_tracks = current_tracks - previous_tracks
            old_tracks = current_tracks & previous_tracks
            result[year] = {"new": len(new_tracks), "old": len(old_tracks)}
        return result

    def listening_trends():
        """Analyze average audio features."""
        audio_features = ["length", "tempo", "energy", "danceability", "valence"]
        trends = {feature: {year: sum(track[feature] for track in tracks) / len(tracks) if tracks else 0
                            for year, tracks in tracks_by_year.items()} for feature in audio_features}
        return trends

    def genre_diversification():
        """Check genre variety over time."""
        genre_counts_by_year = {year: len(set(genre for track in tracks for genre in track.get("genres", [])))
                                for year, tracks in tracks_by_year.items()}
        return genre_counts_by_year

    def artist_growth():
        """Track if some artists gained prominence."""
        artist_counts_by_year = {year: Counter(artist for track in tracks for artist in track["artists"])
                                 for year, tracks in tracks_by_year.items()}
        growth = {artist: {year: count.get(artist, 0) for year, count in artist_counts_by_year.items()}
                  for artist in set(artist for counts in artist_counts_by_year.values() for artist in counts)}
        return growth

    def rare_songs_or_artists():
        """Find songs or artists appearing only once."""
        song_counts = Counter(track["name"] for track in all_tracks)
        artist_counts = Counter(artist for track in all_tracks for artist in track["artists"])
        rare_songs = [song for song, count in song_counts.items() if count == 1]
        rare_artists = [artist for artist, count in artist_counts.items() if count == 1]
        return {"songs": rare_songs, "artists": rare_artists}

    def feature_artists():
        """Find artists appearing primarily as featured artists."""
        feature_counts = Counter(artist for track in all_tracks for artist in track["artists"] if "feat" in track["name"].lower())
        return feature_counts

    # Aggregate Results
    analysis_result = {
        "constant_artists": constant_artists_across_years(),
        "genre_consistency": genre_consistency_and_evolution(),
        "persisting_songs": persisting_songs(),
        "abandoned": abandoned_artists_or_genres(),
        "consistent_songs": most_consistent_songs(),
        "new_vs_old": new_vs_old(),
        "listening_trends": listening_trends(),
        "genre_diversification": genre_diversification(),
        "artist_growth": artist_growth(),
        "rare": rare_songs_or_artists(),
        "feature_artists": feature_artists(),
    }

    return jsonify(analysis_result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
