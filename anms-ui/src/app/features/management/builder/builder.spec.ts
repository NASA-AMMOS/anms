import { provideHttpClient } from '@angular/common/http';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { provideToastr } from 'ngx-toastr';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Builder } from './builder';

describe('Builder', () => {
  let component: Builder;
  let fixture: ComponentFixture<Builder>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Builder, HttpClientTestingModule],
      providers: [provideHttpClient(), provideToastr()],
    }).compileComponents();

    fixture = TestBed.createComponent(Builder);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
