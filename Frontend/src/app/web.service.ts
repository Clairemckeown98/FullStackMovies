import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
@Injectable()

export class WebService {

movie_list: any;
single_movie_list: any;
private movieID:any;

constructor(private http: HttpClient) {}

 getMovies(page: number) {

    return this.http.get(
    'http://localhost:5000/api/v1.0/movies?pn=' + page)
    .subscribe((response: any) => {
    this.movie_list = response;
    console.log(response)
    })
    }

 getMovie (id: any){
   this.movieID = id;
    return this.http.get(
        'http://localhost:5000/api/v1.0/movies/' + id)
        .subscribe((response: any) => {
         this.single_movie_list = response;
         console.log(response)
         })
   };

getReviews(id: any) {
   return this.http.get(
      'http://localhost:5000/api/v1.0/movies/' +
       id + '/reviews');
         
   }

postReview(review: any){
   let postData = new FormData();
   postData.append("username", review.username);
   postData.append("comment", review.comment);
   postData.append("stars", review.stars);

   let today = new Date();
   let todayDate = today.getFullYear() + "-" +
                  today.getMonth() + "-" +
                  today.getDate();
   postData.append("date", todayDate);

   return this.http.post('http://localhost:5000/api/v1.0/movies/' +
                        this.movieID + '/reviews', postData); 

   }

}
