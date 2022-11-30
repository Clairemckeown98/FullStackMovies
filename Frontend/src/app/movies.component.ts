import { Component } from '@angular/core';
import { WebService } from './web.service';

@Component({
  selector: 'app-movies',
  templateUrl: './movies.component.html',
  styleUrls: ['./movies.component.css']
})
export class MoviesComponent {
  //movie_list: any;
  constructor(public webService: WebService) {}

  movie_list: any;
  ngOnInit() {
    this.webService.getMovies(this.page);
    if (sessionStorage['page']) {
      this.page = Number(sessionStorage['page']);
      }

  }

  previousPage(){
    if (this.page > 1) {
      this.page = this.page - 1;
      sessionStorage['page'] = this.page;
      this.movie_list = this.webService.getMovies(this.page); 
    }
  }
  nextPage(){
    this.page = this.page + 1;
    this.movie_list = this.webService.getMovies(this.page);
  }

  business_list: any = [ ];
  page: number = 1;

  
}
