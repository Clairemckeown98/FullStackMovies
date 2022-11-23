import bcrypt
import jwt
from flask import Flask, json, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS, cross_origin

import datetime
from functools import wraps


app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecret'

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.moviesDB # select the database
movies = db.movies # select the collection
users = db.users
blacklist = db.blacklist

def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid'}), 401
        bl_token = blacklist.find_one({"token":token})
        if bl_token is not None:
            return make_response(jsonify({'message' : 'Token has been cancelled'}), 401)
        return func(*args, **kwargs)
    return jwt_required_wrapper


def admin_required(func):
    @wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        token = request.headers['x-access-token']
        data = jwt.decode(token, app.config['SECRET_KEY'])
        if data["admin"]:
            return func(*args, **kwargs)
        else:
            return make_response(jsonify({'message' : 'Admin access required'}), 401)
    return admin_required_wrapper

@app.route("/api/v1.0/movies", methods=["GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
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
        for review in movie["reviews"]:
            review['_id'] = str(review['_id'])
        data_to_return.append(movie)
   
    return make_response( jsonify(data_to_return), 200 )


@app.route("/api/v1.0/movies/<string:id>", methods=["GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@jwt_required
def show_one_movie(id):
    movie = movies.find_one({'_id':ObjectId(id)})
    if movie is not None:
        movie['_id'] = str(movie['_id'])
        if movie['reviews'] is not None:
            for review in movie['reviews']:
                review['_id'] = str(review['_id'])
            return make_response( jsonify( movie ), 200 )
        else:
            return make_response( jsonify({"error" : "Invalid review ID"} ), 404 )
    else:
        return make_response( jsonify({"error" : "Invalid movie ID"} ), 404 )
    
    

@app.route("/api/v1.0/movies", methods=["POST"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def add_movie():
    if "title" in request.form and "overview" in request.form and "runtime" in request.form: 
        new_movie = {
        "title" : request.form["title"],
        "overview" : request.form["overview"],
        "runtime" : request.form["runtime"],
        "reviews" : [], 
        }

        new_movie_id = movies.insert_one(new_movie)
        new_movie_link = "http://localhost:5000/api/v1.0/movies/" + str(new_movie_id.inserted_id)
        return make_response( jsonify({"url": new_movie_link} ), 201)
    else:
        return make_response( jsonify(
        {"error":"Missing form data"} ), 404)


@app.route("/api/v1.0/movies/<string:id>", methods=["PUT"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def edit_movie(id):
    if "title" in request.form and "overview" in request.form and "runtime" in request.form:
        result = movies.update_one( \
        { "_id" : ObjectId(id) }, {"$set" : { "title" : request.form["title"], "overview" : request.form["overview"], "runtime" : request.form["runtime"]}} )

        if result.matched_count == 1:
            edited_movie_link = "http://localhost:5000/api/v1.0/movies/" + id
            return make_response( jsonify({ "url":edited_movie_link } ), 200)
        else:
            return make_response( jsonify({ "error":"Invalid movie ID" } ), 404)
    else:
        return make_response( jsonify({ "error" : "Missing form data" } ), 404)


@app.route("/api/v1.0/movies/<string:id>", methods=["DELETE"])
@jwt_required
@admin_required
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def delete_movie(id):
    result = movies.delete_one( { "_id" : ObjectId(id) } )
    if result.deleted_count == 1:
        return make_response( jsonify( {} ), 204)
    else:
        return make_response( jsonify({ "error" : "Invalid movie ID" } ), 404)

#REVIEW STARTS HERE
@app.route("/api/v1.0/movies/<string:id>/reviews", methods=["POST"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def add_new_review(id):
    new_review = {
    "_id" : ObjectId(),
    "username" : request.form["username"],
    "comment" : request.form["comment"],
    "stars" : request.form["stars"]
    }
    movies.update_one( { "_id" : ObjectId(id) }, { "$push": { "reviews" : new_review } } )
    new_review_link = "http://localhost:5000/api/v1.0/movies/" + id +"/reviews/" + str(new_review['_id'])
    return make_response( jsonify( { "url" : new_review_link } ), 201 )


@app.route("/api/v1.0/movies/<string:id>/reviews", methods=["GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def fetch_all_reviews(id):
    data_to_return = []
    movie = movies.find_one( { "_id" : ObjectId(id) }, { "reviews" : 1, "_id" : 0 } )
    for review in movie["reviews"]:
        review["_id"] = str(review["_id"])
        data_to_return.append(review)
    return make_response( jsonify( data_to_return ), 200 )

@app.route("/api/v1.0/movies/<bid>/reviews/<rid>", methods=["GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def fetch_one_review(bid, rid):
    movie = movies.find_one( { "reviews._id" : ObjectId(rid) }, { "_id" : 0, "reviews.$" : 1 } )
    if movie is None:
        return make_response( jsonify( {"error":"Invalid movie ID or reviews ID"}),404)
    movie['reviews'][0]['_id'] = str((movie['reviews'][0]['_id']))
    return make_response( jsonify( movie['reviews'][0]), 200)

@app.route("/api/v1.0/movies/<bid>/reviews/<rid>", methods=["PUT"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
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
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@jwt_required
@admin_required
def delete_review(bid, rid):
    movies.update_one( { "_id" : ObjectId(bid) }, { "$pull" : { "reviews" : { "_id" : ObjectId(rid) } } } )
    return make_response( jsonify( {} ), 204)

#USER STARTS HERE

@app.route('/api/v1.0/login', methods=['GET'])
def login():
    auth = request.authorization

    if auth:
        user = users.find_one({'username':auth.username})
        if user is not None:
            if bcrypt.checkpw(bytes(auth.password, 'UTF-8'), user["password"]):
                token = jwt.encode({'user':auth.username,'admin':user["admin"], 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
                return make_response(jsonify({'token':token.decode('UTF-8')}), 200)
            else:
                return make_response(jsonify({'message': 'Bad Password'}), 401)
        else:
            return make_response(jsonify({'message': 'Bad Username'}), 401)
    return make_response(jsonify({'message': 'Authentication required'}), 401)

    # if auth and auth.password == 'password':
    #     token = jwt.encode( {'user' : auth.username, 'exp' : datetime.datetime.utcnow() + \
    #             datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    #     return jsonify({'token' : token.decode('UTF-8')})
    # return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm = "Login required"'})

@app.route('/api/v1.0/logout', methods=["GET"])
@jwt_required
def logout():
    token = request.headers['x-access-token']
    blacklist.insert_one({"token":token})
    return make_response(jsonify( {'message' : 'Logout successful'}), 200)


if __name__ == "__main__":
    app.run(debug=True)



@app.route("/api/v1.0/register", methods=["POST"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def add_user():

    if "username" in request.form and "email" in request.form and "password" in request.form:
        username = request.form.get('username')
        email = request.form.get("email")
        password = request.form.get("password")
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
        users.insert_one({'username': username, 'email': email, 'password': hashed, 'admin': False})
        return make_response(jsonify({}), 201)
    else:
        return make_response(jsonify({'message': 'missing data'}), 404)


@app.route("/api/v1.0/users", methods=["GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def show_all_users():
    
    data_to_return = []
    for user in users.find():
        user['_id'] = str(user["_id"])        
        str(user["username"])
        str(user["admin"])
        data_to_return.append({"_id": user["_id"], "username": user["username"], "admin": user["admin"]})
        
    return make_response(jsonify(data_to_return), 200)   
   

@app.route("/api/v1.0/user/delete/<string:id>", methods=["DELETE"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def delete_user(id):
    result = users.delete_one( { "_id" : ObjectId(id)})
    if result.deleted_count == 1:
        return make_response(jsonify({}), 204)
    else:
        return make_response(jsonify({"error": "Invalid user ID"}), 404)
    
    
@app.route("/api/v1.0/users/<string:id>", methods=["GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def current_user(id):
    
    data_to_return = []
    user = users.find_one({"_id": ObjectId(id)})
    if user is not None:
        user['_id'] = str(user["_id"])        
        str(user["username"])
        str(user["admin"])
        data_to_return.append({"_id": user["_id"], "username": user["username"], "admin": user["admin"]})
        
    return make_response(jsonify(data_to_return), 200)  
    

if __name__ == "__main__":
    app.run(debug=True)