import pickle
import pandas as pd

# Load anime models
try:
    anime_dict = pickle.load(open('models/Anime/anime_list.pkl', 'rb'))
    animes = pd.DataFrame(anime_dict)
    anime_similarity = pickle.load(open('models/Anime/similarity.pkl', 'rb'))
    print("✅ Loaded anime models successfully!")
    print(f"Number of animes: {len(animes)}")
    print(f"Anime columns: {list(animes.columns)}")
    print(f"Similarity matrix shape: {anime_similarity.shape}")
    
    # Test finding Naruto
    matched_anime = animes[animes['name'].str.lower() == 'naruto'.lower()]
    print(f"Found Naruto entries: {len(matched_anime)}")
    if not matched_anime.empty:
        print(f"Naruto data: {matched_anime.iloc[0].to_dict()}")
        
        # Test recommendation
        anime_index = matched_anime.index[0]
        print(f"Anime index: {anime_index}")
        print(f"Similarity matrix shape: {anime_similarity.shape}")
        
        if anime_index < len(anime_similarity):
            distances = anime_similarity[anime_index]
            print(f"Distances shape: {distances.shape}")
            anime_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
            
            print("Top 5 recommendations:")
            for i in anime_list:
                if i[0] < len(animes):
                    anime_data = animes.iloc[i[0]]
                    print(f"- {anime_data['name']} (similarity: {i[1]:.3f})")
                else:
                    print(f"- Index {i[0]} out of range")
        else:
            print(f"Anime index {anime_index} is out of range for similarity matrix")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
