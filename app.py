import pickle
import pandas as pd
import requests
import time
import json
import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

# Initialize the Flask application
app = Flask(__name__, static_folder='static')

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyD5JwpKqIm6B_bLHtEy-CU25Xk4XCksNhA"
genai.configure(api_key=GEMINI_API_KEY)

# --- Load the recommendation models ---
try:
    # Load movie models
    movies_dict = pickle.load(open('models/movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('models/similarity.pkl', 'rb'))
    
    # Load credits dataset for cast information
    credits_df = pd.read_csv('Dataset/tmdb_5000_credits.csv')
    # Create a mapping from movie title to credits
    credits_mapping = {}
    for _, row in credits_df.iterrows():
        try:
            cast_data = json.loads(row['cast']) if pd.notna(row['cast']) else []
            crew_data = json.loads(row['crew']) if pd.notna(row['crew']) else []
            credits_mapping[row['title']] = {
                'cast': cast_data,
                'crew': crew_data
            }
        except:
            credits_mapping[row['title']] = {'cast': [], 'crew': []}
    
    print("✅ Loaded movie models successfully!")
            
except FileNotFoundError as e:
    print(f"ERROR: Model file not found. {e}")
    exit()

# --- Poster cache and configuration ---
POSTER_CACHE_FILE = 'poster_cache.json'
poster_cache = {}
failed_poster_cache = {}  # Track failed attempts to avoid repeated failures

def load_poster_cache():
    """Load poster cache from file if it exists."""
    global poster_cache, failed_poster_cache
    if os.path.exists(POSTER_CACHE_FILE):
        try:
            with open(POSTER_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                poster_cache = cache_data.get('posters', {})
                failed_poster_cache = cache_data.get('failed', {})
            print(f"Loaded {len(poster_cache)} cached poster URLs and {len(failed_poster_cache)} failed entries")
        except Exception as e:
            print(f"Error loading poster cache: {e}")
            poster_cache = {}
            failed_poster_cache = {}

def save_poster_cache():
    """Save poster cache to file."""
    try:
        cache_data = {
            'posters': poster_cache,
            'failed': failed_poster_cache
        }
        with open(POSTER_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        print(f"Error saving poster cache: {e}")

# Load cache on startup
load_poster_cache()

def verify_poster_url(url):
    """Verify if a poster URL is actually accessible."""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except:
        return False

def fetch_poster_with_retry(movie_title, max_retries=3):
    """
    Fetch poster with retry mechanism and multiple fallback strategies.
    """
    # Check if we've already failed this movie recently
    if movie_title in failed_poster_cache:
        last_failure = failed_poster_cache[movie_title].get('timestamp', 0)
        # Retry after 1 hour
        if time.time() - last_failure < 3600:
            return failed_poster_cache[movie_title].get('url', "https://placehold.co/500x750/334155/ffffff?text=No+Poster")
    
    # Check cache first
    if movie_title in poster_cache:
        cached_url = poster_cache[movie_title]
        # Verify the cached URL still works
        if verify_poster_url(cached_url):
            return cached_url
        else:
            # Remove invalid cached URL
            del poster_cache[movie_title]
    
    api_key = "97847f7f21868cfb23839599f4853830"
    
    # Multiple search strategies
    search_queries = [
        movie_title,
        movie_title.split('(')[0].strip(),  # Remove year if present
        movie_title.replace(':', '').replace('-', ' '),  # Clean special characters
    ]
    
    for attempt in range(max_retries):
        for query in search_queries:
            url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}"
            
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                # Try different poster sizes for better reliability
                poster_sizes = ['w500', 'w342', 'w185', 'original']
                
                for movie_result in data.get('results', []):
                    poster_path = movie_result.get('poster_path')
                    if poster_path:
                        for size in poster_sizes:
                            full_path = f"https://image.tmdb.org/t/p/{size}{poster_path}"
                            
                            # Verify the poster URL is accessible
                            if verify_poster_url(full_path):
                                poster_cache[movie_title] = full_path
                                
                                # Save cache periodically
                                if len(poster_cache) % 10 == 0:
                                    save_poster_cache()
                                
                                return full_path
                
                # If we get here, no valid poster found for this query
                continue
                
            except requests.exceptions.RequestException as e:
                print(f"ERROR: API request failed for '{movie_title}' (attempt {attempt + 1}): {e}")
                continue
            except Exception as e:
                print(f"ERROR: Unexpected error for '{movie_title}' (attempt {attempt + 1}): {e}")
                continue
        
        # Wait before retry
        if attempt < max_retries - 1:
            time.sleep(1 + attempt * 2)  # Exponential backoff
    
    # If all attempts failed, use placeholder and cache the failure
    placeholder_url = "https://placehold.co/500x750/334155/ffffff?text=No+Poster"
    failed_poster_cache[movie_title] = {
        'url': placeholder_url,
        'timestamp': time.time()
    }
    save_poster_cache()
    return placeholder_url

# --- Function to fetch movie poster from TMDB API ---
def fetch_poster(movie_title):
    """
    Fetches the movie poster URL from The Movie Database (TMDB) API by searching for the title.
    Includes caching, retry mechanisms, and fallback strategies for better reliability.
    """
    return fetch_poster_with_retry(movie_title)

# --- Function to fetch multiple posters efficiently ---
def fetch_multiple_posters(movie_titles):
    """
    Fetch posters for multiple movies with better error handling and caching.
    """
    posters = {}
    
    for title in movie_titles:
        posters[title] = fetch_poster(title)
        # Small delay to avoid overwhelming the API
        time.sleep(0.2)
    
    # Save cache after batch operation
    save_poster_cache()
    return posters

def get_movie_details(movie_title):
    """
    Get detailed information about a movie including cast, release date, and overview.
    """
    try:
        # Find movie in the dataset
        movie_row = movies[movies['title'].str.lower() == movie_title.lower()]
        if movie_row.empty:
            return None
        
        movie_data = movie_row.iloc[0]
        
        # Get basic movie info
        details = {
            'title': movie_data['title'],
            'release_date': movie_data.get('release_date', 'Unknown'),
            'overview': movie_data.get('overview', 'No overview available.'),
            'genres': movie_data.get('genres', ''),
            'vote_average': movie_data.get('vote_average', 0),
            'runtime': movie_data.get('runtime', 0),
            'poster': fetch_poster(movie_title)
        }
        
        # Get cast information
        credits = credits_mapping.get(movie_title, {'cast': [], 'crew': []})
        cast = credits['cast']
        crew = credits['crew']
        
        # Extract main cast (first 5 actors)
        main_cast = []
        for actor in cast[:5]:
            main_cast.append({
                'name': actor.get('name', 'Unknown'),
                'character': actor.get('character', 'Unknown'),
                'order': actor.get('order', 999)
            })
        
        # Extract director
        director = "Unknown"
        for crew_member in crew:
            if crew_member.get('job') == 'Director':
                director = crew_member.get('name', 'Unknown')
                break
        
        details['cast'] = main_cast
        details['director'] = director
        
        # Get streaming platforms (placeholder - would need additional API)
        details['streaming_platforms'] = get_streaming_platforms(movie_title)
        
        return details
        
    except Exception as e:
        print(f"Error getting movie details for {movie_title}: {e}")
        return None

def get_streaming_platforms(movie_title):
    """
    Get streaming platforms where the movie is available.
    This is a simplified version - in a real implementation, you'd use a streaming availability API.
    """
    # This is a placeholder implementation
    # In a real app, you'd integrate with services like JustWatch API or similar
    platforms = ['Netflix', 'Amazon Prime', 'Disney+', 'HBO Max']
    import random
    # Randomly assign 1-3 platforms for demo purposes
    return random.sample(platforms, random.randint(1, 3))

def generate_movie_summary(movie_title, overview, cast_info):
    """
    Generate a short summary using Gemini API.
    """
    try:
        # Use Gemini Flash 1.5 for efficiency
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create a prompt for the summary
        cast_text = ", ".join([f"{actor['name']} as {actor['character']}" for actor in cast_info[:3]])
        
        prompt = f"""
        Write a brief, engaging 2-3 sentence summary of the movie "{movie_title}" based on this information:
        
        Overview: {overview}
        Main Cast: {cast_text}
        
        Make it concise, interesting, and avoid spoilers. Focus on the plot and what makes it worth watching.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Error generating summary for {movie_title}: {e}")
        return overview[:200] + "..." if len(overview) > 200 else overview

# --- Define the routes for the web application ---

@app.route('/')
def home():
    """Renders the main page of the web application."""
    return render_template('index.html')

@app.route('/movies')
def get_movies():
    """Provides a list of all movie titles for the autocomplete feature."""
    movie_titles = movies['title'].to_list()
    return jsonify(movie_titles)

@app.route('/recommend', methods=['POST'])
def recommend():
    """
    Takes a movie title and returns recommendations with detailed information (without AI summaries).
    """
    movie_title_from_user = request.json.get('movie')
    matched_movie = movies[movies['title'].str.lower() == movie_title_from_user.lower()]

    if matched_movie.empty:
        return jsonify({'error': 'Movie not found in our database. Please try another.'}), 404

    try:
        movie_index = matched_movie.index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

        # Get all recommended movie titles first
        recommended_titles = [movies.iloc[i[0]].title for i in movies_list]
        
        # Get detailed information for each recommended movie (without AI summary)
        recommended_movies_data = []
        for title in recommended_titles:
            movie_details = get_movie_details(title)
            if movie_details:
                # Don't generate AI summary here - it will be generated on-demand
                recommended_movies_data.append(movie_details)
        
        return jsonify({'recommendations': recommended_movies_data})

    except Exception as e:
        # This will print a detailed error for any unexpected issues.
        print(f"FATAL: An unexpected error occurred in /recommend route: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

@app.route('/get_summary', methods=['POST'])
def get_summary():
    """
    Generate AI summary for a specific movie on-demand.
    """
    try:
        movie_title = request.json.get('movie')
        if not movie_title:
            return jsonify({'error': 'Movie title is required'}), 400
        
        # Get movie details
        movie_details = get_movie_details(movie_title)
        if not movie_details:
            return jsonify({'error': 'Movie not found'}), 404
        
        # Generate AI summary on-demand
        summary = generate_movie_summary(movie_title, movie_details['overview'], movie_details['cast'])
        
        return jsonify({
            'movie': movie_title,
            'ai_summary': summary,
            'original_overview': movie_details['overview']
        })
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return jsonify({'error': 'Failed to generate summary'}), 500

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the poster cache."""
    global poster_cache, failed_poster_cache
    try:
        poster_cache.clear()
        failed_poster_cache.clear()
        if os.path.exists(POSTER_CACHE_FILE):
            os.remove(POSTER_CACHE_FILE)
        return jsonify({'message': 'Cache cleared successfully'})
    except Exception as e:
        print(f"Error clearing cache: {e}")
        return jsonify({'error': 'Failed to clear cache'}), 500

@app.route('/cache/status')
def cache_status():
    """Get cache status information."""
    return jsonify({
        'cached_posters': len(poster_cache),
        'failed_posters': len(failed_poster_cache),
        'cache_file_exists': os.path.exists(POSTER_CACHE_FILE)
    })

@app.route('/poster/refresh/<movie_title>', methods=['POST'])
def refresh_poster(movie_title):
    """Force refresh a specific movie poster."""
    try:
        # Remove from both caches to force fresh fetch
        if movie_title in poster_cache:
            del poster_cache[movie_title]
        if movie_title in failed_poster_cache:
            del failed_poster_cache[movie_title]
        
        # Fetch fresh poster
        new_poster_url = fetch_poster(movie_title)
        save_poster_cache()
        
        return jsonify({
            'movie': movie_title,
            'poster': new_poster_url,
            'message': 'Poster refreshed successfully'
        })
    except Exception as e:
        print(f"Error refreshing poster for '{movie_title}': {e}")
        return jsonify({'error': 'Failed to refresh poster'}), 500

@app.route('/Images/<path:filename>')
def serve_image(filename):
    """Serve images from the Images folder."""
    from flask import send_from_directory
    return send_from_directory('Images', filename)

@app.route('/health')
def health_check():
    """Health check endpoint to verify the server is running."""
    try:
        # Check if all required models are loaded
        movies_status = 'movies' in globals() and movies is not None
        similarity_status = 'similarity' in globals() and similarity is not None
        
        return jsonify({
            'status': 'healthy' if all([movies_status, similarity_status]) else 'unhealthy',
            'models': {
                'movies_loaded': len(movies) if movies_status else 0,
                'movie_similarity_shape': similarity.shape if similarity_status else None
            },
            'cache': {
                'poster_cache_size': len(poster_cache),
                'failed_cache_size': len(failed_poster_cache)
            }
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# --- Run the Flask application ---
if __name__ == '__main__':
    app.run(debug=True)
