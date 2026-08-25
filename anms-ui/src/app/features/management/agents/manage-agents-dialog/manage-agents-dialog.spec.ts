import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { NotificationService } from '../../../../shared/notification.service';
import { ManageAgentsDialog } from './manage-agents-dialog';

describe('ManageAgentsDialog', () => {
  let component: ManageAgentsDialog;
  let fixture: ComponentFixture<ManageAgentsDialog>;
  let httpMock: HttpTestingController;
  const notificationService = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManageAgentsDialog, HttpClientTestingModule],
      providers: [
        { provide: MatDialogRef, useValue: { close: () => {} } },
        { provide: MAT_DIALOG_DATA, useValue: { agents: [] } },
        { provide: NotificationService, useValue: notificationService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ManageAgentsDialog);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    // Triggers ngOnInit (ARI query). The embedded AriCommandBuilder
    // constructor also queries the ARI list, so two requests total.
    fixture.detectChanges();
    // Both requests hit the same URL and are both open by this point, so
    // expectOne() is ambiguous; match() returns and removes all of them.
    httpMock
      .match((req: { url: string }) => req.url.startsWith('/api/build/ari/all'))
      .forEach((req) => req.flush([]));
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
