#!/usr/bin/env python3
"""
Manual Movie Addition Script
Add movies one by one to your dataset and fetch their posters.
"""

import pickle
import pandas as pd
import requests
import time
import json
import os
import sys

def load_movies_data():
    """Load existing movies data."""
    try:
        movies_dict = pickle.load(open('models/movies_dict.pkl', 'rb'))
        return pd.DataFrame(movies_dict)
    except FileNotFoundError as e:
        print(f"ERROR: Model file not found. {e}")
        return None

def save_movies_data(movies_df):
    """Save movies data back to pickle file."""
    try:
        movies_dict = movies_df.to_dict('records')
        pickle.dump(movies_dict, open('models/movies_dict.pkl', 'wb'))
        print("✓ Movies data saved successfully")
    except Exception as e:
        print(f"✗ Error saving movies data: {e}")

def fetch_poster_for_movie(movie_title):
    """Fetch poster for a single movie."""
    api_key = "97847f7f21868cfb23839599f4853830"
    
    # Search strategies
    search_queries = [
        movie_title,
        movie_title.split('(')[0].strip(),
        movie_title.replace(':', '').replace('-', ' '),
    ]
    
    for query in search_queries:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}"
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Try different poster sizes
            poster_sizes = ['w500', 'w342', 'w185']
            
            for movie_result in data.get('results', []):
                poster_path = movie_result.get('poster_path')
                if poster_path:
                    for size in poster_sizes:
                        full_path = f"https://image.tmdb.org/t/p/{size}{poster_path}"
                        # Verify the URL
                        try:
                            head_response = requests.head(full_path, timeout=10)
                            if head_response.status_code == 200:
                                return full_path
                        except:
                            continue
            
        except Exception as e:
            continue
    
    return "https://placehold.co/500x750/334155/ffffff?text=No+Poster"

def add_movie_manually():
    """Add a single movie manually."""
    print("=== Manual Movie Addition ===")
    
    # Load existing data
    movies_df = load_movies_data()
    if movies_df is None:
        return
    
    print(f"Current dataset has {len(movies_df)} movies")
    
    # Get movie details
    print("\nEnter movie details:")
    title = input("Movie title: ").strip()
    
    if not title:
        print("Title cannot be empty!")
        return
    
    # Check if movie already exists
    if title in movies_df['title'].values:
        print(f"Movie '{title}' already exists in the dataset!")
        return
    
    # Get additional details (optional)
    year = input("Year (optional): ").strip()
    genre = input("Genre (optional): ").strip()
    rating = input("Rating (optional): ").strip()
    
    # Fetch poster
    print(f"\nFetching poster for '{title}'...")
    poster_url = fetch_poster_for_movie(title)
    
    if poster_url != "https://placehold.co/500x750/334155/ffffff?text=No+Poster":
        print("✓ Poster found!")
    else:
        print("✗ No poster found, using placeholder")
    
    # Create new movie entry
    new_movie = {
        'title': title,
        'year': year if year else None,
        'genre': genre if genre else None,
        'rating': float(rating) if rating and rating.replace('.', '').isdigit() else None,
        'poster': poster_url
    }
    
    # Add to dataframe
    movies_df = pd.concat([movies_df, pd.DataFrame([new_movie])], ignore_index=True)
    
    # Save data
    save_movies_data(movies_df)
    
    print(f"\n✓ Movie '{title}' added successfully!")
    print(f"Dataset now has {len(movies_df)} movies")

def add_multiple_movies():
    """Add multiple movies from a file."""
    print("=== Batch Movie Addition ===")
    
    filename = input("Enter filename with movie titles (one per line): ").strip()
    
    if not os.path.exists(filename):
        print(f"File '{filename}' not found!")
        return
    
    # Load existing data
    movies_df = load_movies_data()
    if movies_df is None:
        return
    
    print(f"Current dataset has {len(movies_df)} movies")
    
    # Read movie titles
    try:
        with open(filename, 'r') as f:
            movie_titles = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print(f"Found {len(movie_titles)} movies to add")
    
    # Filter out existing movies
    existing_titles = set(movies_df['title'].values)
    new_titles = [title for title in movie_titles if title not in existing_titles]
    
    if not new_titles:
        print("All movies already exist in the dataset!")
        return
    
    print(f"Adding {len(new_titles)} new movies...")
    
    # Add movies
    added_count = 0
    for i, title in enumerate(new_titles, 1):
        print(f"\n[{i}/{len(new_titles)}] Adding: {title}")
        
        # Fetch poster
        poster_url = fetch_poster_for_movie(title)
        
        # Create new movie entry
        new_movie = {
            'title': title,
            'year': None,
            'genre': None,
            'rating': None,
            'poster': poster_url
        }
        
        # Add to dataframe
        movies_df = pd.concat([movies_df, pd.DataFrame([new_movie])], ignore_index=True)
        added_count += 1
        
        # Rate limiting
        time.sleep(0.2)
    
    # Save data
    save_movies_data(movies_df)
    
    print(f"\n✓ Added {added_count} new movies!")
    print(f"Dataset now has {len(movies_df)} movies")

def interactive_mode():
    """Interactive mode for adding movies."""
    print("=== Interactive Movie Addition ===")
    
    # Load existing data
    movies_df = load_movies_data()
    if movies_df is None:
        return
    
    print(f"Current dataset has {len(movies_df)} movies")
    print("Enter movie titles (empty line to finish):")
    
    added_count = 0
    
    while True:
        title = input("\nMovie title: ").strip()
        
        if not title:
            break
        
        # Check if movie already exists
        if title in movies_df['title'].values:
            print(f"Movie '{title}' already exists!")
            continue
        
        # Fetch poster
        print(f"Fetching poster for '{title}'...")
        poster_url = fetch_poster_for_movie(title)
        
        if poster_url != "https://placehold.co/500x750/334155/ffffff?text=No+Poster":
            print("✓ Poster found!")
        else:
            print("✗ No poster found, using placeholder")
        
        # Create new movie entry
        new_movie = {
            'title': title,
            'year': None,
            'genre': None,
            'rating': None,
            'poster': poster_url
        }
        
        # Add to dataframe
        movies_df = pd.concat([movies_df, pd.DataFrame([new_movie])], ignore_index=True)
        added_count += 1
        
        # Rate limiting
        time.sleep(0.2)
    
    if added_count > 0:
        # Save data
        save_movies_data(movies_df)
        print(f"\n✓ Added {added_count} new movies!")
        print(f"Dataset now has {len(movies_df)} movies")
    else:
        print("\nNo movies added.")

def main():
    print("Movie Addition Tool")
    print("==================")
    print("1. Add single movie manually")
    print("2. Add multiple movies from file")
    print("3. Interactive mode")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        add_movie_manually()
    elif choice == '2':
        add_multiple_movies()
    elif choice == '3':
        interactive_mode()
    elif choice == '4':
        print("Goodbye!")
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
