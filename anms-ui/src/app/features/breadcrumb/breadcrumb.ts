import {Component, inject} from '@angular/core';
import {NavigationEnd, Router} from '@angular/router';
import {filter} from 'rxjs';
import {DataShareService} from '../../shared/data-share.service';

@Component({
  selector: 'app-breadcrumb',
  imports: [],
  templateUrl: './breadcrumb.html',
  styleUrl: './breadcrumb.css',
})
export class Breadcrumb {
  router = inject(Router);
  dataShareService = inject(DataShareService);

  currentUri: string = '';

  constructor() {
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: NavigationEnd) => {
        this.currentUri = event.urlAfterRedirects;
        this.dataShareService.setBreadcrumbs(this.currentUri);
      });
  }
}
