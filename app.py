from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS, cross_origin
import datetime
import bcrypt
import jwt

app = Flask(__name__)


client = MongoClient("mongodb://127.0.0.1:27017")
db = client.moviesDB # select the database
movies = db.movies # select the collection
users = db.users

# application functionality will go here
@app.route("/api/v1.0/movies", methods=["GET"])

def show_all_movies():
    page_num, page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))
    page_start = (page_size * (page_num - 1))

    data_to_return = []
    for movie in movies.find().skip(page_start).limit(page_size):
        movie['_id'] = str(movie['_id'])
        data_to_return.append(movie)
    return make_response( jsonify(data_to_return), 200 )


@app.route("/api/v1.0/movies/<string:id>", methods=["GET"])
def show_one_movie(id):
    movie = movies.find_one({'_id':ObjectId(id)})
    if movie is not None:
        movie['_id'] = str(movie['_id'])
        return make_response( jsonify( movie ), 200 )
    else:
        return make_response( jsonify({"error" : "Invalid movie ID"} ), 404 )

@app.route("/api/v1.0/movies", methods=["POST"])
def add_movie():
    if "title" in request.form and "overview" in request.form and "stars" in request.form: 
        new_movie = {
        "title" : request.form["title"],
        "overview" : request.form["overview"],
        "stars" : request.form["stars"],
        "reviews" : [], 
        }

        new_movie_id = movies.insert_one(new_movie)
        new_movie_link = "http://localhost:5000/api/v1.0/movies/" + str(new_movie_id.inserted_id)
        return make_response( jsonify({"url": new_movie_link} ), 201)
    else:
        return make_response( jsonify(
        {"error":"Missing form data"} ), 404)

@app.route("/api/v1.0/movies/<string:id>", methods=["PUT"])
def edit_movie(id):
    if "title" in request.form and "overview" in request.form and "stars" in request.form:
        result = movies.update_one( \
        { "_id" : ObjectId(id) }, {"$set" : { "title" : request.form["title"], "overview" : request.form["overview"], "stars" : request.form["stars"]}} )

        if result.matched_count == 1:
            edited_movie_link = "http://localhost:5000/api/v1.0/movies/" + id
            return make_response( jsonify({ "url":edited_movie_link } ), 200)
        else:
            return make_response( jsonify({ "error":"Invalid movie ID" } ), 404)
    else:
        return make_response( jsonify({ "error" : "Missing form data" } ), 404)

@app.route("/api/v1.0/movies/<string:id>", methods=["DELETE"])
def delete_movie(id):
    result = movies.delete_one( { "_id" : ObjectId(id) } )
    if result.deleted_count == 1:
        return make_response( jsonify( {} ), 204)
    else:
        return make_response( jsonify({ "error" : "Invalid movie ID" } ), 404)

@app.route("/api/v1.0/movies/<string:id>/reviews", methods=["POST"])
def add_new_review(id):
    new_review = {
    "_id" : ObjectId(),
    "username" : request.form["username"],
    "comment" : request.form["comment"],
    "stars" : request.form["stars"]
    }
    movies.update_one({ "_id" : ObjectId(id) }, { "$push": { "new_review" : new_review } } )
    new_review_link = "http://localhost:5000/api/v1.0/movies/" + id + "/reviews/" + str(new_review['_id'])
    return make_response( jsonify( { "url" : new_review_link } ), 201 )

@app.route("/api/v1.0/movies/<string:id>/reviews", methods=["GET"])
def fetch_all_reviews(id):
    data_to_return = []
    movie = movies.find_one( { "_id" : ObjectId(id) }, { "reviews" : 1, "_id" : 0 } )
    for reviews in movie["reviews"]:
        reviews["_id"] = str(reviews["_id"])
        data_to_return.append(reviews)
        return make_response( jsonify( data_to_return ), 200 )

@app.route("/api/v1.0/movies/<bid>/reviews/<rid>", methods=["GET"])
def fetch_one_review(bid, rid):
    movie = movies.find_one( { "reviews._id" : ObjectId(rid) }, { "_id" : 0, "reviews.$" : 1 } )
    if movie is None:
        return make_response( jsonify( {"error":"Invalid movie ID or reviews ID"}),404)
    movie['reviews'][0]['_id'] = (movie['reviews'][0]['_id'])
    return make_response( jsonify( movie['reviews'][0]), 200)

@app.route("/api/v1.0/movies/<bid>/reviews/<rid>", methods=["PUT"])
def edit_review(bid, rid):
    edited_review = {
    "reviews.$.username" : request.form["username"],
    "reviews.$.comment" : request.form["comment"],
    "reviews.$.stars" : request.form['stars']
    }
    movies.update_one( { "reviews._id" : ObjectId(rid) }, { "$set" : edited_review } )
    edit_review_url = "http://localhost:5000/api/v1.0/movies/" + bid + "/reviews/" + rid
    return make_response( jsonify( {"url":edit_review_url} ), 200)

@app.route("/api/v1.0/movies/<bid>/reviews/<id>", methods=["DELETE"])
def delete_review(bid, rid):
    movies.update_one( { "_id" : ObjectId(bid) }, { "$pull" : { "reviews" : { "_id" : ObjectId(rid) } } } )
    return make_response( jsonify( {} ), 204)


if __name__ == "__main__":
    app.run(debug=True)