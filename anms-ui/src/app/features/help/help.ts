import {Component} from '@angular/core';
import {MatButton} from '@angular/material/button';
import { environment } from '../../../environments/environment'

enum Resource {
  API_DOCS,
  GRAFANA,
}

@Component({
  selector: 'app-help',
  imports: [
    MatButton,
  ],
  templateUrl: './help.html',
  styleUrl: './help.css',
  standalone: true
})
export class Help {
  protected resource = Resource;
  private baseHostname = environment.BASE_API_URL;
  private baseHost = window.location.host;


  protected openUrl(resource: Resource) {
    switch(resource) {
      case Resource.API_DOCS:
        window.open(`/docs`, '_self');
        break;
      case Resource.GRAFANA:
        window.open(`/grafana`, '_self');
        break;
    }
  }
}
