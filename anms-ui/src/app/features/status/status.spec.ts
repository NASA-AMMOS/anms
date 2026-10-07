import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { NotificationService } from '../../shared/notification.service';
import { Status } from './status';

describe('Status', () => {
  let component: Status;
  let fixture: ComponentFixture<Status>;
  let httpMock: HttpTestingController;
  const notificationService = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Status, HttpClientTestingModule],
      providers: [
        {provide: NotificationService, useValue: notificationService},
        provideRouter([]),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Status);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    // Triggers ngOnInit -> updateStatus(), which opens two requests.
    fixture.detectChanges();
    // Flush them so no request ever leaves the test backend.
    httpMock.expectOne('/api/alerts/incoming').flush([]);
    httpMock.expectOne('/api/core/service_status').flush({});
    await fixture.whenStable();
  });

  afterEach(() => {
    // Fails the test if the component made any request we did not account for.
    httpMock.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
