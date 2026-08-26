import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { ToastrService } from 'ngx-toastr';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { Reports } from './reports';

describe('Reports', () => {
  let component: Reports;
  let fixture: ComponentFixture<Reports>;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Reports, HttpClientTestingModule],
      providers: [{ provide: ToastrService, useValue: { error: vi.fn() } }],
    }).compileComponents();

    fixture = TestBed.createComponent(Reports);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    // Triggers ngOnInit. rptts is empty by default, so no preload
    // requests fire; verify() in afterEach guards against any future request.
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
