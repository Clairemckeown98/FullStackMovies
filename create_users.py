from pymongo import MongoClient
import bcrypt


client = MongoClient("mongodb://127.0.0.1:27017")
db = client.moviesDB
users = db.users

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.moviesDB
users = db.users
users_list = [
                {
                    "name" : "Claire",
                    "username" : "claire",
                    "password" : b"sootyboy",
                    "email" : "claire@gmail.com",
                    "admin" : False
                },
                ]

for new_users_user in users_list:
    new_users_user["password"] = bcrypt.hashpw(new_users_user["password"], bcrypt.gensalt())
    users.insert_one(new_users_user)