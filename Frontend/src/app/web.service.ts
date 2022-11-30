import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
@Injectable()

export class WebService {

movie_list: any;

constructor(private http: HttpClient) {}

 getMovies() {
    return this.http.get(
    'http://localhost:5000/api/v1.0/movies')
    .subscribe((response: any) => {
    this.movie_list = response;
    console.log(response)
    })
    }

}