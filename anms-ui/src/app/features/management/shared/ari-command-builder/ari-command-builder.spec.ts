import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AriCommandBuilder } from './ari-command-builder';

describe('AriCommandBuilder', () => {
  let component: AriCommandBuilder;
  let fixture: ComponentFixture<AriCommandBuilder>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AriCommandBuilder],
    }).compileComponents();

    fixture = TestBed.createComponent(AriCommandBuilder);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
