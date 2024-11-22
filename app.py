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

        # More flexible validation
        if not data or "playlists" not in data:
            return jsonify({"error": "Invalid input data"}), 400

        playlists = data.get("playlists", [])
        tracks_data = data.get("tracks", [])

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
    """
    Analyze genre trends across years with enhanced metrics:
    - Genre frequency per year (as percentage)
    - Year-over-year changes
    - Dominant genres per year
    - Genre trajectory (rising/declining/stable)
    """
    # Initialize data structures
    genres_by_year = {
        year: [genre for track in tracks for genre in track.get("genres", [])]
        for year, tracks in tracks_by_year.items()
    }
    
    analysis = {}
    
    for year, genres in genres_by_year.items():
        total_genres = len(genres)
        if total_genres == 0:
            continue
            
        # Calculate frequency and percentage for each genre
        genre_counts = Counter(genres)
        genre_stats = {
            genre: {
                "count": count,
                "percentage": round((count / total_genres) * 100, 2)
            }
            for genre, count in genre_counts.items()
        }
        
        # Find top genres (those representing >10% of tracks)
        significant_genres = {
            genre: stats
            for genre, stats in genre_stats.items()
            if stats["percentage"] > 10
        }
        
        analysis[year] = {
            "all_genres": genre_stats,
            "top_genres": significant_genres,
            "total_tracks_with_genres": total_genres
        }
    
    # Calculate year-over-year changes and trends
    sorted_years = sorted(analysis.keys())
    genre_trends = {}
    
    # Get all unique genres across all years
    all_genres = set()
    for year_data in analysis.values():
        all_genres.update(year_data["all_genres"].keys())
    
    for genre in all_genres:
        trajectory = []
        percentages = []
        
        for year in sorted_years:
            percentage = analysis[year]["all_genres"].get(genre, {}).get("percentage", 0)
            percentages.append(percentage)
            
        # Calculate trend
        if len(percentages) > 1:
            changes = [percentages[i] - percentages[i-1] for i in range(1, len(percentages))]
            avg_change = sum(changes) / len(changes)
            
            if avg_change > 1:  # More than 1% average increase
                trend = "rising"
            elif avg_change < -1:  # More than 1% average decrease
                trend = "declining"
            else:
                trend = "stable"
                
            genre_trends[genre] = {
                "trend": trend,
                "avg_change": round(avg_change, 2),
                "percentages_by_year": dict(zip(sorted_years, percentages))
            }
    
    # Add trends to final analysis
    analysis["trends"] = genre_trends
    
    return analysis
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
