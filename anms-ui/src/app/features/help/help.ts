/*
 * Copyright (c) 2026 The Johns Hopkins University Applied Physics
 * Laboratory LLC.
 *
 * This file is part of the Asynchronous Network Management System (ANMS).
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *     http://www.apache.org/licenses/LICENSE-2.0
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * This work was performed for the Jet Propulsion Laboratory, California
 * Institute of Technology, sponsored by the United States Government under
 * the prime contract 80NM0018D0004 between the Caltech and NASA under
 * subcontract 1658085.
 */
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
        window.open(`/core/docs`, '_self');
        break;
      case Resource.GRAFANA:
        window.open(`/grafana`, '_self');
        break;
    }
  }
}
