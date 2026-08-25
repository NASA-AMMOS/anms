import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

import { ApiService } from '../../../../shared/api.service';
import { NotificationService } from '../../../../shared/notification.service';

import { ManageAgentsDialog } from './manage-agents-dialog';

describe('ManageAgentsDialog', () => {
  let component: ManageAgentsDialog;
  let fixture: ComponentFixture<ManageAgentsDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManageAgentsDialog],
      providers: [
        { provide: MatDialogRef, useValue: { close: () => {} } },
        { provide: MAT_DIALOG_DATA, useValue: { agents: [] } },
        {
          provide: ApiService,
          useValue: {
            apiQueryForARIs: () => of([]),
            apiPutTranscodedString: () => of({ id: 1 }),
            apiGetTranscoderLogById: () => of({ cbor: '' }),
            apiSendRawCommand: () => of({}),
          },
        },
        { provide: NotificationService, useValue: { success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn() } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ManageAgentsDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
