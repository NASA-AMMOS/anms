import { Router } from '@angular/router';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { ApiService } from '../../../shared/api.service';
import { NotificationService } from '../../../shared/notification.service';

import { Builder } from './builder';

describe('Builder', () => {
  let component: Builder;
  let fixture: ComponentFixture<Builder>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Builder],
      providers: [
        {
          provide: ApiService,
          useValue: {
            apiQueryForTranscoderLog: () => of({ items: {}, total: 0, page: 1, size: 10 }),
            apiPutTranscodedString: () => of({ status: 'ok' }),
            apiQueryForARIs: () => of([]),
          },
        },
        { provide: NotificationService, useValue: { success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn() } },
        { provide: Router, useValue: { navigate: vi.fn() } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Builder);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
