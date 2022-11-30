import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { MovieComponent } from './movie.component';
import { ReactiveFormsModule } from '@angular/forms';


import { AppComponent } from './app.component';
import { MoviesComponent } from './movies.component';
import { WebService } from './web.service';
import { HttpClientModule } from '@angular/common/http';
import { HomeComponent } from './home.component';
import { RouterModule } from '@angular/router';

var routes: any = [
  {
  path: '',
  component: HomeComponent
  },
  {
  path: 'movies',
  component: MoviesComponent
  },
  {
    path: 'movies/:id',
    component: MovieComponent
  }
 ];

@NgModule({
  declarations: [
    AppComponent,
    MoviesComponent, 
    HomeComponent,
    MovieComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
    ReactiveFormsModule
  ],
  providers:  [WebService],
  bootstrap: [AppComponent]
})
export class AppModule { }
