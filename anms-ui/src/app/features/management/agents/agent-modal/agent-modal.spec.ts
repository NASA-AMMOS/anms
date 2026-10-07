import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ToastrService } from 'ngx-toastr';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { NotificationService } from '../../../../shared/notification.service';
import { AgentModal } from './agent-modal';

describe('AgentModal', () => {
  let component: AgentModal;
  let fixture: ComponentFixture<AgentModal>;
  let httpMock: HttpTestingController;
  const notificationService = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AgentModal, HttpClientTestingModule],
      providers: [
        { provide: MatDialogRef, useValue: { close: () => {} } },
        { provide: MAT_DIALOG_DATA, useValue: { registered_agents_id: 'test-agent-id' } },
        { provide: NotificationService, useValue: notificationService },
        // Embedded <app-crud> injects ToastrService directly.
        { provide: ToastrService, useValue: { error: vi.fn() } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AgentModal);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    // Triggers ngOnInit -> reloadAgent(): GET agent, then GET report template.
    fixture.detectChanges();
    // Flush them so no request ever leaves the test backend.
    httpMock.expectOne('/api/agents/id/test-agent-id').flush({ registered_agents_id: 'test-agent-id' });
    httpMock.expectOne('/api/report/entry/name/test-agent-id').flush([]);
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
