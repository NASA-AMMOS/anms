import { provideHttpClient } from '@angular/common/http';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { provideToastr } from 'ngx-toastr';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Agents } from './agents';

describe('Agents', () => {
  let component: Agents;
  let fixture: ComponentFixture<Agents>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Agents, HttpClientTestingModule],
      providers: [provideHttpClient(), provideToastr()],
    }).compileComponents();

    fixture = TestBed.createComponent(Agents);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
