import { provideHttpClient } from '@angular/common/http';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { provideToastr } from 'ngx-toastr';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Crud } from './crud';

describe('Crud', () => {
  let component: Crud;
  let fixture: ComponentFixture<Crud>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Crud, HttpClientTestingModule],
      providers: [provideHttpClient(), provideToastr()],
    }).compileComponents();

    fixture = TestBed.createComponent(Crud);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
