import { Router } from '@angular/router';
import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { NotificationService } from '../../../shared/notification.service';
import { Builder } from './builder';

describe('Builder', () => {
  let component: Builder;
  let fixture: ComponentFixture<Builder>;
  let httpMock: HttpTestingController;
  const notificationService = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Builder, HttpClientTestingModule],
      providers: [
        { provide: NotificationService, useValue: notificationService },
        { provide: Router, useValue: { navigate: vi.fn() } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Builder);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    // Triggers ngOnInit -> loadTranscoderLogs(). The embedded
    // AriCommandBuilder constructor also queries the ARI list.
    fixture.detectChanges();
    // Flush them so no request ever leaves the test backend.
    httpMock
      .expectOne((req) => req.url.startsWith('/api/build/ari/all'))
      .flush([]);
    httpMock
      .expectOne((req) => req.url.startsWith('/api/transcoder/ui/log'))
      .flush({ items: {}, total: 0, page: 1, size: 10 });
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
