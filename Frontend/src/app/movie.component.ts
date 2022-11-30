import { Component } from '@angular/core';
import { WebService } from './web.service';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, Validators } from '@angular/forms'

@Component({
  selector: 'movie',
  templateUrl: './movie.component.html',
  styleUrls: ['./movie.component.css']
})

export class MovieComponent {
  //movie_list: any;
  reviewForm: any;
  reviews: any = [];

  constructor(public webService: WebService,
    private route: ActivatedRoute,
    private formBuilder: FormBuilder) {}

  ngOnInit() {

    this.reviewForm = this.formBuilder.group({
      username: ['', Validators.required],
      comment: ['', Validators.required],
      stars: 5
    });

    this.webService.getMovie(this.route.snapshot.params['id']);
    this.reviews = this.webService.getReviews(this.route.snapshot.params['id'])
  }

  onSubmit() {
    this.webService.postReview(this.reviewForm.value)
      .subscribe((response: any) => {
        this.reviewForm.reset();
        this.reviews = this.webService.getReviews(this.route.snapshot.params['id']);
      }); 
      //console.log(this.reviewForm.value);
      //this.webService.postReview(this.reviewForm.value)
      //this.reviewForm.reset();
  }

  isInvalid(control:any){
    return this.reviewForm.controls[control].invalid &&
          this.reviewForm.controls[control].touched;
  }

  isUntouched(){
    return this.reviewForm.controls.username.pristine ||
            this.reviewForm.controls.comment.pristine;
  }

  isIncomplete(){
    return this.isInvalid('username')||
    this.isInvalid('comment')||
    this.isUntouched();
  }

}
