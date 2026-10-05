import { Router } from '@angular/router';
import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { NotificationService } from '../../../shared/notification.service';
import { Builder, TranscoderLogEntry } from './builder';
import { CommandHandoffService } from '../../../shared/command-handoff.service';

describe('Builder', () => {
  let component: Builder;
  let fixture: ComponentFixture<Builder>;
  let httpMock: HttpTestingController;
  const notificationService = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Builder, HttpClientTestingModule],
      providers: [
        { provide: NotificationService, useValue: notificationService },
        { provide: Router, useValue: { navigate: vi.fn() } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Builder);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    // Triggers ngOnInit -> loadTranscoderLogs(). The embedded
    // AriCommandBuilder constructor also queries the ARI list.
    fixture.detectChanges();
    // Flush them so no request ever leaves the test backend.
    httpMock
      .expectOne((req) => req.url.startsWith('/api/build/ari/all'))
      .flush([]);
    httpMock
      .expectOne((req) => req.url.startsWith('/api/transcoder/ui/log'))
      .flush({ items: {}, total: 0, page: 1, size: 10 });
    await fixture.whenStable();
  });

  afterEach(() => {
    // Fails the test if the component made any request we did not account for.
    httpMock.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('removes leading hex prefixes before handing CBOR commands to agents', () => {
    const logs: TranscoderLogEntry[] = ['0xABCD', '0X1234', '5678'].map((cbor, index) => ({
      transcoder_log_id: index,
      input_string: '',
      parsed_as: '',
      ari: '',
      uri: '',
      cbor,
    }));
    component['selection'].select(...logs);
    component['sendToAgents']();

    expect(TestBed.inject(CommandHandoffService).cborCommands()).toEqual(['ABCD', '1234', '5678']);
    expect(TestBed.inject(Router).navigate).toHaveBeenCalledWith(['/dashboard/agents']);
  });
});
