#!/usr/bin/env python3
"""
Batch Poster Processor for Large Movie Datasets (50,000+ movies)
Handles large datasets efficiently with progress tracking and resume capability.
"""

import pickle
import pandas as pd
import requests
import time
import json
import os
import sys
from datetime import datetime
from tqdm import tqdm

class BatchPosterProcessor:
    def __init__(self, batch_size=100, max_workers=5):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.api_key = "97847f7f21868cfb23839599f4853830"
        self.cache_file = 'poster_cache.json'
        self.progress_file = 'batch_progress.json'
        self.posters = {}
        self.failed = {}
        self.processed_count = 0
        
    def load_existing_cache(self):
        """Load existing cache and progress."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.posters = data.get('posters', {})
                    self.failed = data.get('failed', {})
                print(f"Loaded existing cache: {len(self.posters)} posters, {len(self.failed)} failed")
            except Exception as e:
                print(f"Error loading cache: {e}")
        
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                    self.processed_count = progress.get('processed_count', 0)
                print(f"Resuming from position: {self.processed_count}")
            except Exception as e:
                print(f"Error loading progress: {e}")
    
    def save_cache(self):
        """Save cache to file."""
        try:
            data = {
                'posters': self.posters,
                'failed': self.failed,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def save_progress(self):
        """Save progress to file."""
        try:
            progress = {
                'processed_count': self.processed_count,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def verify_poster_url(self, url):
        """Verify if a poster URL is accessible."""
        try:
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def fetch_poster_for_movie(self, movie_title, max_retries=2):
        """Fetch poster for a single movie with retry logic."""
        # Check if already processed
        if movie_title in self.posters:
            if self.verify_poster_url(self.posters[movie_title]):
                return self.posters[movie_title]
            else:
                del self.posters[movie_title]
        
        # Check if recently failed
        if movie_title in self.failed:
            last_failure = self.failed[movie_title].get('timestamp', 0)
            if time.time() - last_failure < 3600:  # 1 hour cooldown
                return self.failed[movie_title].get('url', "https://placehold.co/500x750/334155/ffffff?text=No+Poster")
        
        # Search strategies
        search_queries = [
            movie_title,
            movie_title.split('(')[0].strip(),
            movie_title.replace(':', '').replace('-', ' '),
        ]
        
        for attempt in range(max_retries):
            for query in search_queries:
                url = f"https://api.themoviedb.org/3/search/movie?api_key={self.api_key}&query={query}"
                
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
                                if self.verify_poster_url(full_path):
                                    self.posters[movie_title] = full_path
                                    return full_path
                    
                except Exception as e:
                    continue
            
            if attempt < max_retries - 1:
                time.sleep(1)
        
        # If all attempts failed
        placeholder_url = "https://placehold.co/500x750/334155/ffffff?text=No+Poster"
        self.failed[movie_title] = {
            'url': placeholder_url,
            'timestamp': time.time()
        }
        return placeholder_url
    
    def process_batch(self, movie_titles):
        """Process a batch of movie titles."""
        batch_results = {
            'successful': 0,
            'failed': 0,
            'cached': 0
        }
        
        for title in movie_titles:
            # Check if already cached and working
            if title in self.posters and self.verify_poster_url(self.posters[title]):
                batch_results['cached'] += 1
                continue
            
            poster_url = self.fetch_poster_for_movie(title)
            
            if poster_url != "https://placehold.co/500x750/334155/ffffff?text=No+Poster":
                batch_results['successful'] += 1
            else:
                batch_results['failed'] += 1
            
            # Rate limiting
            time.sleep(0.1)
        
        return batch_results
    
    def process_all_movies(self, movie_titles):
        """Process all movies in batches."""
        total_movies = len(movie_titles)
        print(f"Starting batch processing of {total_movies} movies...")
        print(f"Batch size: {self.batch_size}")
        print(f"Starting from position: {self.processed_count}")
        
        # Skip already processed movies
        movies_to_process = movie_titles[self.processed_count:]
        
        if not movies_to_process:
            print("All movies have been processed!")
            return
        
        # Process in batches
        total_batches = (len(movies_to_process) + self.batch_size - 1) // self.batch_size
        
        with tqdm(total=len(movies_to_process), desc="Processing movies") as pbar:
            for i in range(0, len(movies_to_process), self.batch_size):
                batch = movies_to_process[i:i + self.batch_size]
                batch_num = i // self.batch_size + 1
                
                print(f"\n--- Batch {batch_num}/{total_batches} ---")
                print(f"Processing movies {self.processed_count + i + 1} to {min(self.processed_count + i + self.batch_size, total_movies)}")
                
                # Process batch
                results = self.process_batch(batch)
                
                # Update progress
                self.processed_count += len(batch)
                pbar.update(len(batch))
                
                # Print batch results
                print(f"Batch results: {results['successful']} new, {results['cached']} cached, {results['failed']} failed")
                
                # Save progress every batch
                self.save_cache()
                self.save_progress()
                
                # Progress summary
                success_rate = (len(self.posters) / self.processed_count) * 100 if self.processed_count > 0 else 0
                print(f"Overall progress: {self.processed_count}/{total_movies} ({success_rate:.1f}% success rate)")
                
                # Small delay between batches
                time.sleep(1)
        
        print(f"\n=== Processing Complete ===")
        print(f"Total processed: {self.processed_count}")
        print(f"Successful posters: {len(self.posters)}")
        print(f"Failed posters: {len(self.failed)}")
        print(f"Success rate: {(len(self.posters) / self.processed_count) * 100:.1f}%")

def load_movies_data():
    """Load movies data from pickle file."""
    try:
        movies_dict = pickle.load(open('models/movies_dict.pkl', 'rb'))
        return pd.DataFrame(movies_dict)
    except FileNotFoundError as e:
        print(f"ERROR: Model file not found. {e}")
        return None

def main():
    print("=== Batch Poster Processor for Large Datasets ===")
    
    # Load movies data
    movies_df = load_movies_data()
    if movies_df is None:
        return
    
    # Get all movie titles
    movie_titles = movies_df['title'].tolist()
    print(f"Found {len(movie_titles)} movies in dataset")
    
    # Ask user for batch size
    print("\nConfiguration:")
    batch_size = input(f"Batch size (default 100): ").strip()
    batch_size = int(batch_size) if batch_size.isdigit() else 100
    
    # Create processor
    processor = BatchPosterProcessor(batch_size=batch_size)
    
    # Load existing progress
    processor.load_existing_cache()
    
    # Confirm before starting
    remaining = len(movie_titles) - processor.processed_count
    print(f"\nRemaining movies to process: {remaining}")
    
    if remaining == 0:
        print("All movies have been processed!")
        return
    
    confirm = input(f"Start processing {remaining} movies? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Processing cancelled.")
        return
    
    # Start processing
    start_time = time.time()
    processor.process_all_movies(movie_titles)
    end_time = time.time()
    
    # Final summary
    duration = end_time - start_time
    print(f"\n=== Final Summary ===")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Average time per movie: {duration/len(movie_titles):.2f} seconds")
    print(f"Cache file: {processor.cache_file}")
    print(f"Progress file: {processor.progress_file}")

if __name__ == "__main__":
    main()
