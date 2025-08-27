#!/usr/bin/env python3
"""
Utility script to manually refresh specific movie posters.
Use this when you have specific movies with missing posters.
"""

import requests
import json
import time
import sys

def refresh_specific_poster(movie_title):
    """Refresh a specific movie poster via the Flask API."""
    try:
        # URL encode the movie title for the API call
        import urllib.parse
        encoded_title = urllib.parse.quote(movie_title)
        
        url = f"http://localhost:5000/poster/refresh/{encoded_title}"
        response = requests.post(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Successfully refreshed poster for '{movie_title}'")
            print(f"  New poster URL: {data['poster']}")
            return True
        else:
            print(f"✗ Failed to refresh poster for '{movie_title}': {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error refreshing poster for '{movie_title}': {e}")
        return False

def refresh_multiple_posters(movie_titles):
    """Refresh multiple movie posters."""
    print(f"Refreshing {len(movie_titles)} movie posters...")
    
    successful = 0
    failed = 0
    
    for i, title in enumerate(movie_titles, 1):
        print(f"\n[{i}/{len(movie_titles)}] Refreshing: {title}")
        
        if refresh_specific_poster(title):
            successful += 1
        else:
            failed += 1
        
        # Small delay between requests
        time.sleep(0.5)
    
    print(f"\n=== Summary ===")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(movie_titles)}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python refresh_posters.py 'Movie Title'")
        print("  python refresh_posters.py --file movies.txt")
        print("  python refresh_posters.py --interactive")
        return
    
    if sys.argv[1] == "--file" and len(sys.argv) > 2:
        # Read movie titles from file
        filename = sys.argv[2]
        try:
            with open(filename, 'r') as f:
                movie_titles = [line.strip() for line in f if line.strip()]
            refresh_multiple_posters(movie_titles)
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except Exception as e:
            print(f"Error reading file: {e}")
    
    elif sys.argv[1] == "--interactive":
        # Interactive mode
        print("Interactive poster refresh mode")
        print("Enter movie titles (one per line, empty line to finish):")
        
        movie_titles = []
        while True:
            title = input("Movie title: ").strip()
            if not title:
                break
            movie_titles.append(title)
        
        if movie_titles:
            refresh_multiple_posters(movie_titles)
        else:
            print("No movies entered.")
    
    else:
        # Single movie title
        movie_title = " ".join(sys.argv[1:])
        refresh_specific_poster(movie_title)

if __name__ == "__main__":
    main()
