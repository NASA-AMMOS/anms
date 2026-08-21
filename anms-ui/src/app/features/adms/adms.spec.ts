import { provideHttpClient } from '@angular/common/http';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { provideToastr } from 'ngx-toastr';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Adms } from './adms';

describe('Adms', () => {
  let component: Adms;
  let fixture: ComponentFixture<Adms>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Adms, HttpClientTestingModule],
      providers: [provideHttpClient(), provideToastr()],
    }).compileComponents();

    fixture = TestBed.createComponent(Adms);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
