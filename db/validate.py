import pytest
import psycopg2
from dotenv import load_dotenv
from ingest import get_connection
import os

load_dotenv()

@pytest.fixture(scope="session")
def conn():
    connection = get_connection()
    yield connection
    connection.close()

def test_movies_have_titles(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM movies WHERE title IS NULL")
    results = cur.fetchall()
    assert len(results) == 0

def test_movies_have_release_dates(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM movies WHERE release_date IS NULL")
    results = cur.fetchall()
    assert len(results) == 0

def test_movies_have_vote_averages(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM movies WHERE vote_average IS NULL")
    results = cur.fetchall()
    assert len(results) == 0

def test_genres_have_names(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM genres WHERE name IS NULL")
    results = cur.fetchall()
    assert len(results) == 0

def test_vote_average_in_range(conn):
    cur = conn.cursor()
    cur.execute("SELECT vote_average FROM movies WHERE vote_average > 10.0 OR vote_average < 0.0")
    results = cur.fetchall()
    assert len(results) == 0

def test_no_orphaned_movie_genres(conn):
    cur = conn.cursor()
    cur.execute("SELECT movie_genres.movie_id FROM movie_genres LEFT JOIN movies ON movie_genres.movie_id = movies.id WHERE movies.id IS NULL")
    results = cur.fetchall()
    assert len(results) == 0

def test_no_duplicate_movie_ids(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, COUNT(*) FROM movies GROUP BY id HAVING COUNT(*) > 1;")
    results = cur.fetchall()
    assert len(results) == 0