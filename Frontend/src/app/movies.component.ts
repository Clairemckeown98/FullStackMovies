import { Component } from '@angular/core';
import { WebService } from './web.service';

@Component({
  selector: 'app-movies',
  templateUrl: './movies.component.html',
  styleUrls: ['./movies.component.css']
})
export class MoviesComponent {
  movie_list: any;
  constructor(public webService: WebService) {}
  ngOnInit() {
    this.webService.getMovies();

  }
}
