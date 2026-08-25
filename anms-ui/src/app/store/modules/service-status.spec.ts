import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { NotificationService } from '../../shared/notification.service';
import { ServiceStatusService } from './service-status.service';

describe('StatusStore', () => {
  let service: ServiceStatusService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        {
          provide: NotificationService,
          useValue: { success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn() },
        },
      ],
    });
    service = TestBed.inject(ServiceStatusService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    // Fails the test if the service made any request we did not account for.
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should fetch alerts and service status without error', () => {
    service.updateStatus();

    const alertsReq = httpMock.expectOne('/api/alerts/incoming');
    expect(alertsReq.request.method).toBe('GET');
    alertsReq.flush([]);

    const statusReq = httpMock.expectOne('/api/core/service_status');
    expect(statusReq.request.method).toBe('GET');
    statusReq.flush({});
  });

  it('should handle a failed service status request', () => {
    service.updateStatus();

    httpMock.expectOne('/api/alerts/incoming').flush([]);
    httpMock
      .expectOne('/api/core/service_status')
      .flush({ message: 'server error' }, { status: 500, statusText: 'Server Error' });
  });
});
