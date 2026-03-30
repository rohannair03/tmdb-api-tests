import os
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()
_api_key = os.environ.get("TMDB_API_KEY")

def get_connection():
    conn = psycopg2.connect(host = os.environ.get("DB_HOST"), database=os.environ.get("DB_NAME"), user =
            os.environ.get("DB_USER"), password=os.environ.get("DB_PASSWORD"), port=os.environ.get("DB_PORT"))
    return conn

def fetch_genres():
    genres = requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key="+str(_api_key))
    return genres.json()["genres"]

def fetch_movies():
    all_movies = []
    for page in range(1,6):
        movies = requests.get("https://api.themoviedb.org/3/movie/popular?api_key=" + str(_api_key) + "&page="+str(page))
        results = movies.json()["results"]
        all_movies.extend(results)
    return all_movies

def insert_genre(conn, genres):
    cur = conn.cursor()
    for genre in genres:
        cur.execute("INSERT INTO genres (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING", (genre["id"], genre["name"]))
    conn.commit()

def insert_movies(conn, movies):
    cur = conn.cursor()
    for movie in movies:
        cur.execute("INSERT INTO movies (id, title, release_date, vote_average) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                    (movie["id"], movie["title"], movie["release_date"], movie["vote_average"]))
    conn.commit()

def insert_movie_genres(conn, movies):
    cur = conn.cursor()
    for movie in movies:
        for genre_id in movie["genre_ids"]:
            cur.execute("INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s) ON CONFLICT (movie_id, genre_id) DO NOTHING", (movie["id"], genre_id))
    conn.commit()

def main():
    conn = get_connection()
    genres = fetch_genres()
    movies = fetch_movies()
    insert_genre(conn, genres)
    insert_movies(conn, movies)
    insert_movie_genres(conn, movies)
    conn.close()

if __name__ == "__main__":
    main()



