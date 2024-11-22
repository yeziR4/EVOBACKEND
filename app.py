from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import Counter, defaultdict
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route("/")
def home():
    return "Analysis API is running!"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        logger.debug(f"Received data: {data}")

        # More flexible validation
        if not data or "playlists" not in data:
            logger.error("Invalid input data")
            return jsonify({"error": "Invalid input data"}), 400

        playlists = data.get("playlists", [])
        tracks_data = data.get("tracks", [])
        
        logger.debug(f"Number of playlists: {len(playlists)}")
        logger.debug(f"Number of tracks: {len(tracks_data)}")

        # Organize data
        tracks_by_year = defaultdict(list)
        all_tracks = []

        for track in tracks_data:
            year = track.get("year")
            if year:
                tracks_by_year[year].append(track)
            all_tracks.append(track)
        
        logger.debug(f"Tracks by year: {dict(tracks_by_year)}")

        def genre_consistency_and_evolution():
            """
            Analyze genre trends across years with enhanced metrics
            """
            # Initialize data structures
            genres_by_year = {
                year: [genre for track in tracks for genre in track.get("genres", [])]
                for year, tracks in tracks_by_year.items()
            }
            
            logger.debug(f"Genres by year before processing: {genres_by_year}")
            
            # Handle case of no genre data
            if not genres_by_year:
                return {
                    "error": "No genre data available",
                    "tracks_by_year": dict(tracks_by_year)
                }
            
            analysis = {}
            
            for year, genres in genres_by_year.items():
                logger.debug(f"Processing year {year} with genres: {genres}")
                
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
                
                # Find top genres (those representing >5% of tracks)
                significant_genres = {
                    genre: stats
                    for genre, stats in genre_stats.items()
                    if stats["percentage"] > 5
                }
                
                analysis[year] = {
                    "all_genres": genre_stats,
                    "top_genres": significant_genres,
                    "total_tracks_with_genres": total_genres
                }
            
            logger.debug(f"Initial analysis: {analysis}")
            
            # If no analysis was created
            if not analysis:
                return {
                    "error": "No genre analysis could be performed",
                    "tracks_by_year": dict(tracks_by_year)
                }
            
            # Calculate year-over-year changes and trends
            sorted_years = sorted(analysis.keys())
            genre_trends = {}
            
            # Get all unique genres across all years
            all_genres = set()
            for year_data in analysis.values():
                all_genres.update(year_data["all_genres"].keys())
            
            for genre in all_genres:
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
            
            logger.debug(f"Final genre analysis: {analysis}")
            return analysis

        # Ensure robust error handling
        try:
            genre_analysis = genre_consistency_and_evolution()
        except Exception as e:
            logger.error(f"Error in genre analysis: {e}")
            genre_analysis = {"error": str(e)}

        # Aggregate Results
        analysis_result = {
            "genre_consistency": genre_analysis,
        }

        logger.debug(f"Final analysis result: {analysis_result}")
        return jsonify(analysis_result)

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({
            "error": "Internal server error", 
            "details": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
