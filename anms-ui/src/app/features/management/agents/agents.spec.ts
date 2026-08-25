import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { ApiService } from '../../../shared/api.service';
import { NotificationService } from '../../../shared/notification.service';

import { Agents } from './agents';

describe('Agents', () => {
  let component: Agents;
  let fixture: ComponentFixture<Agents>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Agents],
      providers: [
        {
          provide: ApiService,
          useValue: {
            apiAmpVersion: () => of({ amp_version: null }),
            apiQueryForAgents: () => of({ items: [], total: 0 }),
          },
        },
        { provide: NotificationService, useValue: { success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn() } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Agents);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
