import requests
from django.shortcuts import render
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.conf import settings


OMDB_KEY = settings.OMDB_API_KEY
yts_end = "https://yts.mx/api/v2/movie_details.json?imdb_id="

def get_movie_details(movie):
    title = movie.get('Title')
    year = movie.get('Year')
    poster_url = movie.get('Poster')
    imdb_id = movie.get('imdbID')  # Extract IMDb ID
    # yts check
    response = requests.get(yts_end + imdb_id)
    data = response.json()
    movie_id = data['data']['movie']['id']
    
    available = 'Not Available' if movie_id == 0 else 'Available'
    return {
        'title': title,
        'year': year,
        'poster_url': poster_url,
        'available': available,
        'imdb_id': imdb_id,  # Include IMDb ID in the details
        'image_source': f'https://www.imdb.com/title/{imdb_id}/'  # Link to the IMDb page
    }

def search_movies(query):
    # Use OMDb API to search for movies by title (no pagination)
    url = f'http://www.omdbapi.com/?s={query}&apikey={OMDB_KEY}'
    response = requests.get(url)
    data = response.json()
    if data.get('Response') == 'True':
        return data['Search']
    return []

def home(request):
    query = request.GET.get('query', '')
    
    # Check if the user is authenticated
    is_authenticated = request.user.is_authenticated

    # Check cache first
    cache_key = f'movie_search_{query}'
    cached_movies = cache.get(cache_key)

    if cached_movies:
        movie_data = cached_movies
    else:
        # Fetch the movies
        search_results = search_movies(query)
        movie_data = [get_movie_details(movie) for movie in search_results]

        print(movie_data)

        # Cache the results for 5 minutes
        cache.set(cache_key, movie_data, timeout=300)

    return render(request, 'search/index.html', {
        'movies': movie_data,
        'query': query,
        'is_authenticated': is_authenticated  # Pass authentication status to the template
    })
