import { provideHttpClient } from '@angular/common/http';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { provideToastr } from 'ngx-toastr';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import {AgentModal} from './agent-modal';


describe('AgentModal', () => {
  let component: AgentModal;
  let fixture: ComponentFixture<AgentModal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AgentModal, HttpClientTestingModule],
      providers: [
        provideHttpClient(),
        provideToastr(),
        { provide: MatDialogRef, useValue: { close: () => {} } },
        { provide: MAT_DIALOG_DATA, useValue: {} },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AgentModal);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
