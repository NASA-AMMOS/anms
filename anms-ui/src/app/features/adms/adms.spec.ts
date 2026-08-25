import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { ApiAdmService } from '../../shared/api-adm.service';
import { NotificationService } from '../../shared/notification.service';

import { Adms } from './adms';

describe('Adms', () => {
  let component: Adms;
  let fixture: ComponentFixture<Adms>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Adms],
      providers: [
        {
          provide: ApiAdmService,
          useValue: {
            apiGetAdms: () => of([]),
          },
        },
        { provide: NotificationService, useValue: { success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn() } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Adms);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
