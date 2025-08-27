# Large Dataset Guide: Handling 50,000+ Movies

## Overview
This guide explains how to efficiently handle large movie datasets (50,000+ movies) with poster fetching and caching.

## Available Tools

### 1. **Batch Poster Processor** (`batch_poster_processor.py`)
**Best for: Processing all movies in your dataset at once**

**Features:**
- Processes movies in configurable batches (default: 100)
- Progress tracking and resume capability
- Memory-efficient processing
- Automatic cache management
- Rate limiting to avoid API issues

**Usage:**
```bash
python batch_poster_processor.py
```

**What it does:**
- Loads all movies from your dataset
- Processes them in batches
- Saves progress after each batch
- Can resume if interrupted
- Shows real-time progress

### 2. **Manual Movie Addition** (`add_movies_manually.py`)
**Best for: Adding specific movies one by one**

**Features:**
- Add single movies manually
- Add multiple movies from a text file
- Interactive mode for continuous addition
- Automatic poster fetching
- Duplicate detection

**Usage:**
```bash
python add_movies_manually.py
```

**Options:**
1. **Single movie**: Add one movie with full details
2. **From file**: Add multiple movies from a text file
3. **Interactive**: Add movies continuously until you stop

### 3. **Preload Cache** (`preload_cache.py`)
**Best for: Pre-populating cache with popular movies**

**Features:**
- Processes top 100 movies by popularity
- Good for initial setup
- Faster than full batch processing

**Usage:**
```bash
python preload_cache.py
```

## Step-by-Step Process for 50,000 Movies

### Step 1: Initial Setup
```bash
# Install required packages
pip install tqdm requests pandas

# Run preload script for popular movies first
python preload_cache.py
```

### Step 2: Batch Processing (Recommended)
```bash
# Start batch processing
python batch_poster_processor.py

# Choose batch size (recommended: 100-500)
# The script will:
# - Show progress
# - Save after each batch
# - Resume if interrupted
# - Display success rates
```

### Step 3: Monitor Progress
- Check cache status: `http://localhost:5000/cache/status`
- Monitor `poster_cache.json` file size
- Watch progress in terminal

### Step 4: Resume if Needed
If the process is interrupted:
```bash
# Simply run the batch processor again
python batch_poster_processor.py
# It will automatically resume from where it left off
```

## Performance Expectations

### Time Estimates for 50,000 Movies:
- **Batch size 100**: ~8-12 hours
- **Batch size 500**: ~6-10 hours
- **With good internet**: ~4-8 hours

### Success Rates:
- **Popular movies**: 90-95%
- **Obscure movies**: 60-80%
- **Overall average**: 75-85%

### Memory Usage:
- **Cache file**: ~2-5 MB for 50,000 movies
- **RAM usage**: Minimal (processes in batches)

## File Formats

### Input File for Manual Addition:
Create a text file with movie titles (one per line):
```
The Shawshank Redemption
The Godfather
Pulp Fiction
Fight Club
...
```

### Cache File Structure:
```json
{
  "posters": {
    "Movie Title": "https://image.tmdb.org/t/p/w500/poster_path.jpg"
  },
  "failed": {
    "Failed Movie": {
      "url": "https://placehold.co/500x750/334155/ffffff?text=No+Poster",
      "timestamp": 1234567890
    }
  }
}
```

## Troubleshooting

### If Process is Slow:
1. **Reduce batch size** (try 50 instead of 100)
2. **Check internet connection**
3. **Verify API key is working**

### If Many Posters Fail:
1. **Check movie titles** for typos
2. **Verify TMDB API status**
3. **Try manual refresh for specific movies**

### If Process Stops:
1. **Check disk space**
2. **Verify file permissions**
3. **Restart and resume**

### Memory Issues:
1. **Reduce batch size**
2. **Close other applications**
3. **Restart computer if needed**

## Advanced Usage

### Custom Batch Sizes:
```bash
# For faster processing (if you have good internet)
python batch_poster_processor.py
# Enter batch size: 500

# For slower, more reliable processing
python batch_poster_processor.py
# Enter batch size: 50
```

### Manual Refresh for Failed Posters:
```bash
# Refresh specific movies
python refresh_posters.py "Movie Title"

# Refresh from file
python refresh_posters.py --file failed_movies.txt
```

### Monitor Cache Status:
```bash
# Check via API
curl http://localhost:5000/cache/status

# Check file directly
ls -lh poster_cache.json
```

## Best Practices

### 1. **Start Small**
- Begin with preload script
- Test with batch size 50
- Gradually increase batch size

### 2. **Monitor Progress**
- Check progress every hour
- Monitor success rates
- Watch for errors

### 3. **Backup Regularly**
- Copy `poster_cache.json` periodically
- Keep backup of original dataset

### 4. **Resume Strategy**
- Don't delete progress files
- Let the system resume automatically
- Only clear cache if necessary

### 5. **Rate Limiting**
- Don't run multiple scripts simultaneously
- Respect API limits
- Use delays between requests

## Expected Results

After processing 50,000 movies, you should have:
- **~35,000-42,000 successful posters** (70-85% success rate)
- **~8,000-15,000 failed posters** (with placeholders)
- **Cache file size**: 2-5 MB
- **Processing time**: 6-12 hours

## Next Steps

1. **Run batch processor** for all movies
2. **Monitor progress** and success rates
3. **Manually refresh** any important failed posters
4. **Start your Flask application** with the populated cache
5. **Enjoy fast poster loading** for all movies!

## Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify your internet connection
3. Test with a small batch first
4. Check the cache status endpoint
