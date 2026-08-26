import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { NotificationService } from '../../../shared/notification.service';
import { Agents } from './agents';

describe('Agents', () => {
  let component: Agents;
  let fixture: ComponentFixture<Agents>;
  let httpMock: HttpTestingController;
  const notificationService = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Agents, HttpClientTestingModule],
      providers: [
        { provide: NotificationService, useValue: notificationService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Agents);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    // Triggers ngAfterViewInit: agent list query + manager version check.
    fixture.detectChanges();
    // Flush them so no request ever leaves the test backend.
    httpMock.expectOne((req) => req.url === '/api/agents').flush({ items: [], total: 0 });
    httpMock.expectOne('/api/nm/version').flush({ amp_version: null });
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
