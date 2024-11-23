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

        def abandoned_artists_or_genres():
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
            songs_by_year = {year: set(track["name"] for track in tracks) for year, tracks in tracks_by_year.items()}
            if not songs_by_year:
                return []
            return list(set.intersection(*songs_by_year.values()))

        def new_vs_old():
            result = {}
            for year, tracks in tracks_by_year.items():
                unique_songs = set(track["name"] for track in tracks)
                unique_artists = set(artist for track in tracks for artist in track["artists"])
                previous_songs = set(track["name"] for year_key, tracks_key in tracks_by_year.items() if year_key < year for track in tracks_key)
                previous_artists = set(artist for year_key, tracks_key in tracks_by_year.items() if year_key < year for track in tracks_key for artist in track["artists"])
                new_songs = unique_songs - previous_songs
                new_artists = unique_artists - previous_artists
                result[year] = {
                    "new_songs": len(new_songs),
                    "repeat_songs": len(unique_songs & previous_songs),
                    "new_artists": len(new_artists),
                    "repeat_artists": len(unique_artists & previous_artists)
                }
            return result
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

        def rare_songs_and_artists():
            song_years = defaultdict(list)
            artist_years = defaultdict(list)
            for year, tracks in tracks_by_year.items():
                for track in tracks:
                    song_years[track["name"]].append(year)
                    for artist in track["artists"]:
                        artist_years[artist].append(year)
            rare_songs = [song for song, years in song_years.items() if len(years) == 1]
            rare_artists = [artist for artist, years in artist_years.items() if len(years) == 1]
            return {"rare_songs": rare_songs, "rare_artists": rare_artists}

        def artists_through_features():
            feature_counts = Counter()
            for track in all_tracks:
                main_artist = track["artists"][0]
                feature_artists = track["artists"][1:]
                for artist in feature_artists:
                    feature_counts[artist] += 1
            return feature_counts

      
         
       


        analysis_result = {
            "constant_artists": constant_artists_across_years(),
            "genre_consistency": genre_consistency_and_evolution(),
            "persisting_songs": persisting_songs(),
            "abandoned": abandoned_artists_or_genres(),
            "consistent_songs": most_consistent_songs(),
            "new_vs_old": artists_through_features(),
            "top_growing_artists": artist_growth()[0],
            "top_declining_artists": artist_growth()[1],
            "artists_through_features": artists_through_features(),
        }
        top_3_featured_artists = sorted(analysis_result["artists_through_features"].items(), key=lambda x: x[1], reverse=True)[:3]
        for artist, count in top_3_featured_artists:
            print(artist)
        return jsonify(analysis_result)
   
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
