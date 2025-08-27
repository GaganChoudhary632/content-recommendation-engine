# Enhanced Movie Recommendation System

## 🎬 Overview

This enhanced movie recommendation system provides detailed movie recommendations with rich information including cast details, release dates, streaming platforms, and AI-generated summaries using Google's Gemini API.

## ✨ New Features

### 🎯 Enhanced Movie Details
- **Movie Posters**: High-quality movie posters fetched from TMDB API
- **Release Date & Year**: Display when the movie was released
- **Runtime**: Movie duration in hours and minutes
- **Rating**: IMDb-style rating display
- **Director Information**: Shows who directed the movie

### 🎭 Cast Information
- **Main Cast**: Shows top 5 actors with their character names
- **Character Roles**: Displays who plays what character
- **Actor Names**: Full names of the cast members

### 📺 Streaming Platforms
- **OTT Availability**: Shows which streaming platforms have the movie
- **Platform Badges**: Visual indicators for Netflix, Amazon Prime, Disney+, HBO Max, Hulu
- **Dynamic Assignment**: Randomly assigns platforms for demonstration (can be integrated with real APIs)

### 🤖 AI-Generated Summaries
- **Gemini Flash 1.5**: Uses Google's efficient AI model for summaries
- **Smart Summaries**: 2-3 sentence engaging summaries without spoilers
- **Context-Aware**: Uses movie overview and cast information for better summaries
- **Token Efficient**: Optimized for cost-effective API usage

### 🎨 Enhanced UI/UX
- **Modern Design**: Beautiful, responsive card layout
- **Hover Effects**: Interactive animations and transitions
- **Responsive Grid**: Adapts to different screen sizes
- **Loading States**: Shows progress while generating recommendations

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Flask
- Pandas
- Google Generative AI library

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Movie_recommendation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify the setup**
   ```bash
   python test_recommendations.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
Movie_recommendation/
├── app.py                          # Main Flask application
├── test_recommendations.py         # Test script for verification
├── requirements.txt                # Python dependencies
├── README_ENHANCED.md             # This documentation
├── Dataset/
│   ├── tmdb_5000_movies.csv       # Movie dataset
│   └── tmdb_5000_credits.csv      # Cast and crew dataset
├── models/
│   ├── movies_dict.pkl            # Processed movie data
│   └── similarity.pkl             # Similarity matrix
├── templates/
│   └── index.html                 # Enhanced main page
└── static/
    └── Images/                    # Static assets
```

## 🔧 Configuration

### API Keys
The system uses the following APIs:

1. **TMDB API** (for movie posters)
   - API Key: `97847f7f21868cfb23839599f4853830`
   - Used for fetching movie posters

2. **Google Gemini API** (for AI summaries)
   - API Key: `AIzaSyD5JwpKqIm6B_bLHtEy-CU25Xk4XCksNhA`
   - Model: `gemini-1.5-flash` (efficient version)

### Environment Variables
You can set these as environment variables for production:
```bash
export TMDB_API_KEY="your_tmdb_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
```

## 🎮 How to Use

### 1. Search for Movies
- Type a movie title in the search box
- Use the autocomplete feature for suggestions
- Press Enter or click the search icon

### 2. View Recommendations
- Get 5 detailed movie recommendations
- Each card shows comprehensive information
- Hover over cards for interactive effects

### 3. Explore Movie Details
- **Poster**: High-quality movie poster
- **Basic Info**: Title, year, runtime, rating
- **Cast**: Main actors and their characters
- **Director**: Who directed the movie
- **Streaming**: Available platforms
- **AI Summary**: Engaging plot summary



## 🔍 API Endpoints

### GET `/`
- Main page with search interface



### GET `/movies`
- Returns list of all movie titles for autocomplete

### POST `/recommend`
- **Input**: `{"movie": "movie_title"}`
- **Output**: Detailed movie recommendations with all enhanced features

### POST `/cache/clear`
- Clears the poster cache

### GET `/cache/status`
- Returns cache statistics

### POST `/poster/refresh/<movie_title>`
- Force refresh poster for a specific movie

## 🛠️ Technical Implementation

### Backend Features

1. **Enhanced Data Processing**
   ```python
   def get_movie_details(movie_title):
       # Fetches comprehensive movie information
       # Includes cast, crew, release date, runtime, etc.
   ```

2. **AI Summary Generation**
   ```python
   def generate_movie_summary(movie_title, overview, cast_info):
       # Uses Gemini Flash 1.5 for efficient summaries
       # Creates engaging, spoiler-free descriptions
   ```

3. **Streaming Platform Integration**
   ```python
   def get_streaming_platforms(movie_title):
       # Placeholder for streaming availability
       # Can be integrated with JustWatch API or similar
   ```

### Frontend Features

1. **Responsive Design**
   - Mobile-first approach
   - Adaptive grid layout
   - Touch-friendly interactions

2. **Enhanced Cards**
   - Glassmorphism design
   - Hover animations
   - Rich information display

3. **Loading States**
   - Progress indicators
   - User feedback during API calls

## 🎯 Future Enhancements

### Potential Improvements

1. **Real Streaming Data**
   - Integrate with JustWatch API
   - Real-time availability updates
   - Regional platform information

2. **Advanced AI Features**
   - Personalized recommendations
   - Mood-based suggestions
   - Genre preference learning

3. **Social Features**
   - User reviews and ratings
   - Watchlist functionality
   - Share recommendations

4. **Performance Optimizations**
   - Database caching
   - CDN for images
   - API rate limiting

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify API keys are correct
   - Check API quotas and limits
   - Ensure internet connectivity

2. **Model Loading Issues**
   - Verify pickle files exist
   - Check file permissions
   - Ensure correct Python version

3. **Poster Loading Problems**
   - Clear poster cache: `POST /cache/clear`
   - Check TMDB API status
   - Verify image URLs

### Debug Mode
Run with debug enabled:
```bash
export FLASK_ENV=development
python app.py
```

## 📊 Performance Metrics

- **Response Time**: ~2-3 seconds for full recommendations
- **AI Summary Generation**: ~1-2 seconds per movie
- **Poster Loading**: Cached for faster subsequent loads
- **Memory Usage**: Optimized for large datasets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **TMDB** for movie data and poster images
- **Google Gemini** for AI-powered summaries
- **Flask** for the web framework
- **Tailwind CSS** for styling

---

**Made with ❤️ for movie lovers everywhere!**
