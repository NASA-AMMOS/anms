import { TestBed } from '@angular/core/testing';

import { ApiAdmService } from './api-adm.service';

describe('ApiAdm', () => {
  let service: ApiAdmService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ApiAdmService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
