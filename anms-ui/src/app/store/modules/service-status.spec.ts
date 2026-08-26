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
  let notificationStubs: {
    success: ReturnType<typeof vi.fn>;
    error: ReturnType<typeof vi.fn>;
    warning: ReturnType<typeof vi.fn>;
    info: ReturnType<typeof vi.fn>;
  };

  beforeEach(() => {
    notificationStubs = { success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn() };
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [{ provide: NotificationService, useValue: notificationStubs }],
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
    const testAlert = { id: 'a1', type: 'danger', name: 'Disk', msg: '90% full', visible: true };
    alertsReq.flush([testAlert]);

    const statusReq = httpMock.expectOne('/api/core/service_status');
    expect(statusReq.request.method).toBe('GET');
    statusReq.flush({});

    // The flushed alert must reach the service's state and raise a matching
    // notification - proves the data flow, not just that the request went out.
    expect(service.alerts()).toEqual([testAlert]);
    expect(service.alertIds()).toEqual(['a1']);
    expect(notificationStubs.error).toHaveBeenCalledTimes(1);
  });

  it('should handle a failed service status request', () => {
    // updateStatus() logs the failure via console.error; spy on it so the
    // expected error does not pollute the test output, and assert it ran.
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

    service.updateStatus();

    httpMock.expectOne('/api/alerts/incoming').flush([]);
    httpMock
      .expectOne('/api/core/service_status')
      .flush({ message: 'server error' }, { status: 500, statusText: 'Server Error' });

    // catchError records the failure synchronously.
    expect(service.hasUpdateError()).toBe(true);
    expect(service.loading()).toBe(false);
    // HttpErrorResponse is not an instanceof Error in Angular, so match on
    // the response shape instead of the class.
    expect(consoleError).toHaveBeenCalledWith('Error fetching service status:', expect.objectContaining({ status: 500, statusText: 'Server Error' }));
    consoleError.mockRestore();
  });
});
