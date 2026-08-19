import { provideHttpClient } from '@angular/common/http';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { provideToastr } from 'ngx-toastr';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManageAgentsDialog } from './manage-agents-dialog';

describe('ManageAgentsDialog', () => {
  let component: ManageAgentsDialog;
  let fixture: ComponentFixture<ManageAgentsDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManageAgentsDialog, HttpClientTestingModule],
      providers: [
        provideHttpClient(),
        provideToastr(),
        { provide: MatDialogRef, useValue: { close: () => {} } },
        { provide: MAT_DIALOG_DATA, useValue: { agents: [] } },
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
