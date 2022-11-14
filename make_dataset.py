from pymongo import MongoClient
import json
from pathlib import Path
from bson import ObjectId


def create_database():
    client = MongoClient("mongodb://127.0.0.1:27017")
    db = client.moviesDB

    movies = db.movies   
    with open('movies.json') as f:
        for line in f:
            movies.insert_one(json.loads(line))
    print("movies loaded")

    credits = db.credits    
    with open('credits.json') as f:
        for line in f:
            credits.insert_one(json.loads(line))
    print("credits loaded")

    
    
def add_credits_to_movies():
    client = MongoClient("mongodb://127.0.0.1:27017")
    db = client.moviesDB  
    movies = db.movies
    credits = db.credits

    num_processed = 0
    for movie in movies.find( {}, { "movie_id":1 }, no_cursor_timeout = True):
        credits_of_movie = []
        for credit in credits.find( { "movie_id" : movie["movie_id"] } ):
            credits_of_movie.append(credit)

        movies.update_one( { "movie_id" : movie["movie_id"] } , 
                               { "$set" : { "credits" : credits_of_movie, "review_count" : len(credits_of_movie) } } )
        num_processed = num_processed + 1
        if num_processed % 1000 == 0:
            print(str(num_processed) + " movies processed")

create_database()
add_credits_to_movies()