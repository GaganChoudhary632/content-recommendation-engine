#!/usr/bin/env python3
"""
Script to preload poster cache with popular movies for better performance.
Run this script once to populate the cache before starting the main application.
"""

import pickle
import pandas as pd
import requests
import time
import json
import os

def load_movies_data():
    """Load the movies data from pickle file."""
    try:
        movies_dict = pickle.load(open('models/movies_dict.pkl', 'rb'))
        return pd.DataFrame(movies_dict)
    except FileNotFoundError as e:
        print(f"ERROR: Model file not found. {e}")
        return None

def verify_poster_url(url):
    """Verify if a poster URL is actually accessible."""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except:
        return False

def fetch_poster_with_retry(movie_title, poster_cache, failed_cache, api_key, max_retries=3):
    """Fetch poster with retry mechanism and multiple fallback strategies."""
    # Check if we've already failed this movie recently
    if movie_title in failed_cache:
        last_failure = failed_cache[movie_title].get('timestamp', 0)
        # Retry after 1 hour
        if time.time() - last_failure < 3600:
            return failed_cache[movie_title].get('url', "https://placehold.co/500x750/334155/ffffff?text=No+Poster")
    
    # Check cache first
    if movie_title in poster_cache:
        cached_url = poster_cache[movie_title]
        # Verify the cached URL still works
        if verify_poster_url(cached_url):
            return cached_url
        else:
            # Remove invalid cached URL
            del poster_cache[movie_title]
    
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
    failed_cache[movie_title] = {
        'url': placeholder_url,
        'timestamp': time.time()
    }
    return placeholder_url

def preload_cache():
    """Preload the poster cache with popular movies."""
    print("Starting poster cache preload...")
    
    # Load movies data
    movies = load_movies_data()
    if movies is None:
        return
    
    # Load existing cache
    POSTER_CACHE_FILE = 'poster_cache.json'
    poster_cache = {}
    failed_cache = {}
    
    if os.path.exists(POSTER_CACHE_FILE):
        try:
            with open(POSTER_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                poster_cache = cache_data.get('posters', {})
                failed_cache = cache_data.get('failed', {})
            print(f"Loaded existing cache with {len(poster_cache)} entries and {len(failed_cache)} failed entries")
        except Exception as e:
            print(f"Error loading existing cache: {e}")
    
    # API key
    api_key = "97847f7f21868cfb23839599f4853830"
    
    # Get top 100 movies by popularity (increased from 50)
    # If no popularity column, just take first 100 movies
    if 'popularity' in movies.columns:
        top_movies = movies.nlargest(100, 'popularity')['title'].tolist()
    else:
        top_movies = movies.head(100)['title'].tolist()
    
    print(f"Preloading posters for {len(top_movies)} popular movies...")
    
    # Fetch posters for popular movies
    successful_fetches = 0
    failed_fetches = 0
    
    for i, title in enumerate(top_movies, 1):
        print(f"Processing {i}/{len(top_movies)}: {title}")
        
        # Skip if already in cache and working
        if title in poster_cache and verify_poster_url(poster_cache[title]):
            print(f"  ✓ Already cached and working")
            successful_fetches += 1
            continue
        
        poster_url = fetch_poster_with_retry(title, poster_cache, failed_cache, api_key)
        
        if poster_url != "https://placehold.co/500x750/334155/ffffff?text=No+Poster":
            successful_fetches += 1
            print(f"  ✓ Successfully fetched poster")
        else:
            failed_fetches += 1
            print(f"  ✗ Failed to fetch poster")
        
        time.sleep(0.3)  # Rate limiting
        
        # Save cache every 20 movies
        if i % 20 == 0:
            cache_data = {
                'posters': poster_cache,
                'failed': failed_cache
            }
            try:
                with open(POSTER_CACHE_FILE, 'w') as f:
                    json.dump(cache_data, f, indent=2)
                print(f"  💾 Cache saved ({i}/{len(top_movies)})")
            except Exception as e:
                print(f"  Error saving cache: {e}")
    
    # Final save
    cache_data = {
        'posters': poster_cache,
        'failed': failed_cache
    }
    try:
        with open(POSTER_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
        print(f"Successfully saved cache with {len(poster_cache)} successful entries and {len(failed_cache)} failed entries")
        print(f"Summary: {successful_fetches} successful, {failed_fetches} failed")
    except Exception as e:
        print(f"Error saving cache: {e}")

if __name__ == "__main__":
    preload_cache()
