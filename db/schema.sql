DROP TABLE IF EXISTS movie_genres;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS genres;

CREATE TABLE movies (id INTEGER PRIMARY KEY, title TEXT, release_date DATE, vote_average  NUMERIC(3,1));
CREATE TABLE genres (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE movie_genres (movie_id INTEGER, genre_id INTEGER, PRIMARY KEY (movie_id, genre_id), FOREIGN KEY (genre_id) REFERENCES genres(id), FOREIGN KEY (movie_id) REFERENCES movies(id));