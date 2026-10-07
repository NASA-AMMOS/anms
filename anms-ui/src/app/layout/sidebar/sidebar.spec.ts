import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { NotificationService } from '../../shared/notification.service';
import { Sidebar } from './sidebar';

describe('Sidebar', () => {
  let component: Sidebar;
  let fixture: ComponentFixture<Sidebar>;
  let httpMock: HttpTestingController;
  const notificationService = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Sidebar, HttpClientTestingModule],
      providers: [
        {provide: NotificationService, useValue: notificationService},
        provideRouter([]),
      ],
    }).compileComponents();

    // Provide DOM element that sidebar.ngAfterViewInit looks for
    document.body.innerHTML = '<details id="managementDetails"></details>';

    fixture = TestBed.createComponent(Sidebar);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    // Triggers ngAfterViewInit. Sidebar makes no HTTP calls on init;
    // verify() in afterEach guards against any future request.
    fixture.detectChanges();
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
