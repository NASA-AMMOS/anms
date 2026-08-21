import { provideHttpClient } from '@angular/common/http';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { provideToastr } from 'ngx-toastr';
import { TestBed } from '@angular/core/testing';

import {ServiceStatusService} from './service-status.service';

describe('StatusStore', () => {
  let service: ServiceStatusService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [provideHttpClient(), provideToastr()],
    });
    service = TestBed.inject(ServiceStatusService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

