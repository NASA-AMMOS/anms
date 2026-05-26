import { ComponentFixture, TestBed } from '@angular/core/testing';
import {AgentModal} from './agent-modal';


describe('AgentModal', () => {
  let component: AgentModal;
  let fixture: ComponentFixture<AgentModal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AgentModal],
    }).compileComponents();

    fixture = TestBed.createComponent(AgentModal);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
