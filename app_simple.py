import pickle
import pandas as pd
import requests
import time
import json
import os
from flask import Flask, render_template, request, jsonify

# Initialize the Flask application
app = Flask(__name__, static_folder='static')

# --- Load the recommendation models ---
try:
    # Load movie models
    movies_dict = pickle.load(open('models/movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('models/similarity.pkl', 'rb'))
    
    # Load anime models
    anime_dict = pickle.load(open('models/Anime/anime_list.pkl', 'rb'))
    animes = pd.DataFrame(anime_dict)
    anime_similarity = pickle.load(open('models/Anime/similarity.pkl', 'rb'))
    print("✅ Loaded both movie and anime models successfully!")
            
except FileNotFoundError as e:
    print(f"ERROR: Model file not found. {e}")
    exit()

@app.route('/')
def home():
    """Renders the main page of the web application."""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint to verify the server is running."""
    try:
        return jsonify({
            'status': 'healthy',
            'movies_loaded': len(movies) if 'movies' in globals() else 0,
            'animes_loaded': len(animes) if 'animes' in globals() else 0
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/animes')
def get_animes():
    """Provides a list of all anime titles for the autocomplete feature."""
    try:
        anime_titles = animes['name'].to_list()
        return jsonify(anime_titles)
    except Exception as e:
        print(f"Error getting anime titles: {e}")
        return jsonify([]), 500

@app.route('/recommend_anime', methods=['POST'])
def recommend_anime_route():
    """Takes an anime name and returns recommendations."""
    try:
        anime_name_from_user = request.json.get('anime')
        
        if not anime_name_from_user:
            return jsonify({'error': 'Anime name is required'}), 400
        
        if not anime_name_from_user.strip():
            return jsonify({'error': 'Anime name cannot be empty'}), 400
        
        # Find the anime in the dataset
        matched_anime = animes[animes['name'].str.lower() == anime_name_from_user.lower()]
        
        if matched_anime.empty:
            return jsonify({'error': 'Anime not found in our database. Please try another anime title.'}), 404
        
        anime_index = matched_anime.index[0]
        distances = anime_similarity[anime_index]
        anime_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]
        
        recommended_animes = []
        for i in anime_list:
            try:
                anime_data = animes.iloc[i[0]]
                # Handle missing 'members' column by using a default value
                members_value = anime_data.get('members', 0)
                if pd.isna(members_value):
                    members_value = 0
                
                anime_basic = {
                    'name': anime_data['name'],
                    'anime_id': anime_data['anime_id'],
                    'genre': anime_data.get('genre', 'Unknown'),
                    'type': anime_data.get('type', 'Unknown'),
                    'episodes': anime_data.get('episodes', 'Unknown'),
                    'rating': anime_data.get('rating', 0),
                    'members': members_value,
                    'similarity_score': float(i[1]),
                    'poster': "https://placehold.co/500x750/ff6b6b/ffffff?text=Loading..."
                }
                recommended_animes.append(anime_basic)
            except Exception as e:
                print(f"Error processing anime recommendation {i[0]}: {e}")
                continue
        
        if len(recommended_animes) == 0:
            return jsonify({'error': 'No recommendations found for this anime. Please try another anime.'}), 404
        
        return jsonify({'recommendations': recommended_animes})
        
    except Exception as e:
        print(f"Unexpected error in recommend_anime_route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred. Please try again later.'}), 500

# --- Run the Flask application ---
if __name__ == '__main__':
    app.run(debug=True)
