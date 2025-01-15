import pickle
import streamlit as st
import requests
import os

def fetch_poster(movie_id):
    try:
        # TMDB API endpoint for fetching movie details
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8f239e3e9444dc57120f11598e51a03c&append_to_response=images".format(movie_id)
        
        # Make a GET request with a timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the JSON response
        data = response.json()
        
        # Extract the poster path
        poster_path = data.get('poster_path')
        
        if poster_path:
            # Construct and return the full poster URL
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            # Return a placeholder image if no poster is available
            return "https://via.placeholder.com/500"
    except requests.exceptions.RequestException as e:
        # Log any request-related errors
        print(f"Error fetching poster for movie ID {movie_id}: {e}")
        # Return a placeholder image in case of error
        return "https://via.placeholder.com/500"

def recommend(movie):
    # Check if the movie exists in the dataset
    if movie not in movies['title'].values:
        st.error(f"'{movie}' not found in the dataset.")
        return [], []

    # Get the index of the movie
    index = movies[movies['title'] == movie].index
    if index.empty:
        st.error(f"Index for '{movie}' not found.")
        return [], []
    index = index[0]

    # Check similarity matrix dimensions
    if index >= len(similarity):
        st.error(f"Index {index} is out of bounds for similarity matrix.")
        return [], []

    # Calculate distances and recommend top 5 movies
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:  # Skip the first (self-match)
        try:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i[0]].title)
        except IndexError as e:
            st.warning(f"Error fetching data for recommended movie at index {i[0]}: {e}")
    return recommended_movie_names, recommended_movie_posters

# Streamlit App UI
st.header("Movie Recommender System")

# Load data files
movies_file = os.path.join('movie_list.pkl')
similarity_file = os.path.join('similarity.pkl')

try:
    movies = pickle.load(open(movies_file, 'rb'))
    similarity = pickle.load(open(similarity_file, 'rb'))
except FileNotFoundError as e:
    st.error(f"Required file not found: {e}")
    st.stop()

# Dropdown for movie selection
movies_list = movies['title'].values
selected_movie = st.selectbox(
    'Type movie name to get recommendations',
    movies_list
)

# Button to trigger recommendations
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    
    # Display recommendations if available
    if recommended_movie_names and recommended_movie_posters:
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i])
    else:
        st.warning("No recommendations to display.")
