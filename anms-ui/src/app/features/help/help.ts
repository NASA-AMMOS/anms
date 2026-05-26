import {Component} from '@angular/core';
import {MatButton} from '@angular/material/button';

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
})
export class Help {
  protected resource = Resource;
  // FIXME: use environment.ts or BASE_URL, etc.
  // private baseHostname = window.location.hostname;
  private baseHostname = 'http://anms-test';
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
