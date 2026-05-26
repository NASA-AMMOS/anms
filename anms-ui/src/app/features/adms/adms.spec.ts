import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Adms } from './adms';

describe('Adms', () => {
  let component: Adms;
  let fixture: ComponentFixture<Adms>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Adms],
    }).compileComponents();

    fixture = TestBed.createComponent(Adms);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
