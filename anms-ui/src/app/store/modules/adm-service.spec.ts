import { TestBed } from '@angular/core/testing';

import { AdmService } from './adm-service';

describe('AdmService', () => {
  let service: AdmService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AdmService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
