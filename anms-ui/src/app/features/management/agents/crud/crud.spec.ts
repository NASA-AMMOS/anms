import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { ToastrService } from 'ngx-toastr';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { Crud } from './crud';

describe('Crud', () => {
  let component: Crud;
  let fixture: ComponentFixture<Crud>;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Crud, HttpClientTestingModule],
      providers: [{ provide: ToastrService, useValue: { error: vi.fn() } }],
    }).compileComponents();

    fixture = TestBed.createComponent(Crud);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    // Triggers ngOnInit. Crud makes no HTTP calls on init;
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
