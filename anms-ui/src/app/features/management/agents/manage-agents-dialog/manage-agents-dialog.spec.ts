import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { vi } from 'vitest';
import {HttpErrorResponse} from '@angular/common/http';

import { NotificationService } from '../../../../shared/notification.service';
import { ManageAgentsDialog } from './manage-agents-dialog';

describe('ManageAgentsDialog', () => {
  let component: ManageAgentsDialog;
  let fixture: ComponentFixture<ManageAgentsDialog>;
  let httpMock: HttpTestingController;
  const notificationService = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  };

  beforeEach(async () => {
    vi.clearAllMocks();
    await TestBed.configureTestingModule({
      imports: [ManageAgentsDialog, HttpClientTestingModule],
      providers: [
        { provide: MatDialogRef, useValue: { close: () => {} } },
        { provide: MAT_DIALOG_DATA, useValue: { agents: [] } },
        { provide: NotificationService, useValue: notificationService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ManageAgentsDialog);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    // Triggers ngOnInit (ARI query). The embedded AriCommandBuilder
    // constructor also queries the ARI list, so two requests total.
    fixture.detectChanges();
    // Both requests hit the same URL and are both open by this point, so
    // expectOne() is ambiguous; match() returns and removes all of them.
    httpMock
      .match((req: { url: string }) => req.url.startsWith('/api/build/ari/all'))
      .forEach((req) => req.flush([]));
    await fixture.whenStable();
  });

  afterEach(() => {
    // Fails the test if the component made any request we did not account for.
    httpMock.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('sends each CBOR command without its leading hex prefix', () => {
    const agent = {
      agent_endpoint_uri: 'ipn:1.1',
      registered_agents_id: '1',
      first_registered: '',
      last_registered: '',
    };
    component.data.agents.push(agent);
    component['handleCommand']({mode: 'cbor', value: '0xABCD, 0X1234, 5678'});

    const requests = httpMock.match('/api/nm/agents/eid/ipn:1.1/hex');
    expect(requests.map((request) => request.request.body)).toEqual(['ABCD', '1234', '5678']);
    requests.forEach((request) => request.flush({}));
  });

  describe('server error details', () => {
    beforeEach(() => {
      component.data.agents.push({
        agent_endpoint_uri: 'ipn:1.1', registered_agents_id: '1',
        first_registered: '', last_registered: '',
      });
    });

    it('displays the network manager response when sending raw CBOR fails', () => {
      component['handleCommand']({mode: 'cbor', value: 'ABCD'});
      const message = 'Error talking to NM: {"detail":"Invalid CBOR"}';
      httpMock.expectOne('/api/nm/agents/eid/ipn:1.1/hex')
        .flush(message, {status: 502, statusText: 'Bad Gateway'});

      expect(notificationService.error).toHaveBeenCalledWith(
        `${message}`, 'Error sending CBOR'
      );
    });

    it('displays the network manager response when sending a transcoded ARI fails', () => {
      component['handleCommand']({mode: 'builder', value: 'ari://ietf/test/CTRL/run'});
      httpMock.expectOne('/api/transcoder/ui/incoming/str').flush({id: 1});
      httpMock.expectOne('/api/transcoder/ui/log/id/1').flush({cbor: 'ABCD'});
      const message = 'Error talking to NM: Agent not found';
      httpMock.expectOne('/api/nm/agents/eid/ipn:1.1/hex')
        .flush(message, {status: 502, statusText: 'Bad Gateway'});

      expect(notificationService.error).toHaveBeenCalledWith(message, 'Error sending ARI');
    });

    it('extracts structured response details and falls back to the error message', () => {
      expect(component['getErrorMessage'](new HttpErrorResponse({error: {message: 'Server message'}})))
        .toBe('Server message');
      expect(component['getErrorMessage'](new HttpErrorResponse({error: {detail: {reason: 'Invalid command'}}})))
        .toBe('{"reason":"Invalid command"}');
      const networkError = new HttpErrorResponse({status: 0, error: null});
      expect(component['getErrorMessage'](networkError)).toBe(networkError.message);
      expect(component['getErrorMessage'](new Error('Transcoder log did not include CBOR')))
        .toBe('Transcoder log did not include CBOR');
    });
  });
});
