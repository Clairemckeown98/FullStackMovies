from pymongo import MongoClient
import random


client = MongoClient("mongodb://127.0.0.1:27017")
db = client.moviesDB # select the database
movies = db.movies # select the collection

images = ['https://i.ebayimg.com/images/g/DJgAAOSwq19XB-hI/s-l1600.jpg',
                'https://i0.wp.com/bloody-disgusting.com/wp-content/uploads/2017/05/text10.jpg',
                'https://milnersblog.files.wordpress.com/2015/09/alien-classic-film-poster-without-word-all-text-removed.jpg',
                'http://test.ultralinx.co/wp-content/uploads/2020/02/1_the-shawshank-redemption_5243_1080x1920.jpg',
                'https://images.squarespace-cdn.com/content/v1/51eed611e4b095302497fd81/1387023227806-RZKHQRE2GKYW8AKD3FQJ/ANPosterSet_2014_01_800.jpg?format=1500w',
                'https://www.heritage-posters.co.uk/wp-content/uploads/2021/04/HeritageEbaySML-HepburnGrant.jpg',
                'https://twistedsifter.com/wp-content/uploads/2015/10/41-mad-max-fury-road.jpg',
                'https://www.fubiz.net/wp-content/uploads/2015/09/the-sound-of-music-900x1178.jpg',
                'https://twistedsifter.com/wp-content/uploads/2015/10/09-beetlejuice.jpg',
                'https://welcometotwinpeaks.com/wp-content/uploads/crisvector-twin-peaks-part-17.jpg',
                'https://allthatsinteresting.com/wordpress/wp-content/uploads/2015/09/labyrinth.jpg',
                'https://images.mymovies.net/images/film/cin/350x522/fid21824.jpg'
			]

for movie in movies.find():
	movies.update_one(
		{ "_id" : movie['_id'] },
			{
				"$set" : {
				"Image" : images[random.randint(0, len(images)-1)]
				}
			}
)