import {inject, Injectable} from '@angular/core';
import {Constants} from './constants';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private http = inject(HttpClient);

  public createAuthenticationHeader() {
    return {
      Authorization: 'Bearer ' + Constants.USER_DETAILS.token
    };
  };

  public apiGetHello(): Observable<any> {
    return this.http.get('hello');
  }

  public apiGetUsers(): Observable<any> {
    return this.http.get('users', {
      headers: this.createAuthenticationHeader()
    });
  }

  public apiGetUserById(userId: any): Observable<any> {
    const id = encodeURIComponent(userId) ? encodeURIComponent(userId) : userId;
    return this.http.get('users/' + id, {
      headers: this.createAuthenticationHeader()
    });
  }

  public apiGetUserByUsername(userName: string): Observable<any> {
    const name = encodeURIComponent(userName) ? encodeURIComponent(userName) : userName;
    console.info("name: ", name);
    return this.http.get('users/' + name, {
      headers: this.createAuthenticationHeader()
    });
  }

  public apiCreateUserProfile(payload: any): Observable<any> {
    return this.http.post('users',
      {data: payload},
      {
        headers: this.createAuthenticationHeader()
      });
  }

  public apiUpdateUserProfile(userName: any, payload: any): Observable<any> {
    return this.http.put('users/' + encodeURIComponent(userName),
      {data: payload},
      {
        headers: this.createAuthenticationHeader()
      })
  }

  public apiPutUserProfile(userId: any, payload: any): Observable<any> {
    return this.http.put('users/' + encodeURIComponent(userId) + '/profile',
      {data: payload},
      {
        headers: this.createAuthenticationHeader()
      });
  }

  public apiChangePassword(userId: any, payload: any): Observable<any> {
    return this.http.post('users/' + encodeURIComponent(userId) + '/password',
      {data: payload},
      {
        headers: this.createAuthenticationHeader()
      });
  }

  public apiEnableUser(userId: any): Observable<any> {
    return this.http.patch('users/enable/' + encodeURIComponent(userId),
      {},
      {
        headers: this.createAuthenticationHeader()
      });
  }

  public apiDisableUser(userId: any): Observable<any> {
    return this.http.patch('users/disable/' + encodeURIComponent(userId),
      {}, {headers: this.createAuthenticationHeader()});
  }

  public apiToggleUserMfa(userId: any, newValue: any): Observable<any> {
    return this.http.patch('users/mfa/' + encodeURIComponent(userId),
      {newState: newValue},
      {
        headers: this.createAuthenticationHeader()
      });
  }

  // agents api
  public apiQueryForAgents(payload: any): Observable<any> {
    let params: any = {};
    if (payload.page) {
      params['page'] = encodeURIComponent(payload.page);
    }
    if (payload.size) {
      params['size'] = encodeURIComponent(payload.size);
    }

    if (payload.searchString === '') {
      return this.http.get('/api/agents', {params: params});
    } else {
      const searchString = encodeURIComponent(payload.searchString);
      return this.http.get(`/api/agents/search/${searchString}`, {params: params});
    }
  }

  public apiGetAgent(agentId: any): Observable<any> {
    return this.http.get(`/api/agents/id/${agentId}`);
  }

  // ari all
  public apiQueryForARIs(): Observable<any> {
    return this.http.get('/api/build/ari/all');
  }

  // ari by id
  public apiQueryForARIById(meta_id: any, obj_id: any): Observable<any> {
    return this.http.get(`build/ari/id/${meta_id}/${obj_id}`);
  }

  public apiAmpVersion(): Observable<any> {
    return this.http.get('/api/nm/version');

  }

  public apiDeregister(nodeEID: any): Observable<any> {
    return this.http.get('nm/agents', nodeEID);
  }

  public apiEntriesForReport(obj_agent_id: any, correlator_nonce: any): Observable<any> {
    return this.http.get(`/api/report/entries/table/${obj_agent_id}/${correlator_nonce}`);
  }

  public apiEntriesForReportTemplate(agentId: any): Observable<any> {
    console.log("agentId: ", agentId);
    return this.http.get(`/api/report/entry/name/${agentId}`);
  }

  public apiEntriesForOperations(agentId: any): Observable<any> { // get the names of crude operations
    return this.http.get(`agents/parameter/name/${agentId}`);
  }

  public apiPutCRUD(agentId: any, optId: any, params: any): Observable<any> {
    return this.http.put(`agents/parameter/send/${agentId}/${optId}`, params);
  }

  public apiBuildControl(nodeEID: any): Observable<any> {
    return this.http.put('nm/agents', nodeEID, {headers: {},});
  }

  public apiSendRawCommand(nodeEID: any, command: any): Observable<any> {
    return this.http.put('nm/agents/eid/' + nodeEID + '/hex', {"data": command});
  }

  public apiPrintAgentReports(nodeEID: any): Observable<any> {
    return this.http.get('nm/agents/eid/' + nodeEID + '/reports/json');
  }

  public apiClearAgentReports(nodeEID: any): Observable<any> {
    return this.http.put('nm/agents/eid/' + nodeEID + '/clear_reports', null);
  }

  public apiClearAgentTables(nodeEID: any): Observable<any> {
    return this.http.put('nm/agents/eid/' + nodeEID + '/clear_tables', null);
  }

  public apiWriteAgentReportstofile(nodeEID: any): Observable<any> {
    return this.http.get('nm/agents', nodeEID);
  }

  public apiPostAgent(node: any): Observable<any> {
    return this.http.post('/api/nm/agents', {'data': node});
  }

  public apiGetAgents(): Observable<any> {
    return this.http.get('nm/agents/');
  }

  public apiGetDbStatus(): Observable<any> {
    return this.http.get('sys_status/db_status');
  }

  public apiGetAlerts(): Observable<any> {
    return this.http.get('/api/alerts/incoming', {headers: {accept: 'application/json'}});
  }

  public apiAcknowledgeAlerts(index: any): Observable<any> {
    return this.http.put('/api/alerts/acknowledge/' + index, null);
  }

  public apiGetServiceStatus(): Observable<any> {
    return this.http.get('/api/core/service_status', {headers: {accept: 'application/json'}});
  }

  public apiPutTranscodedHex(cbor: string): Observable<any> {
    return this.http.put('transcoder/ui/incoming/' + cbor + '/hex', null);
  }

  public apiPutTranscodedString(ari: string): Observable<any> {
    return this.http.put('transcoder/ui/incoming/str', {"ari": ari});
  }

  public apiGetTranscoderLogById(id: any): Observable<any> {
    return this.http.get(`transcoder/ui/log/id/${id}`);
  }

  public apiQueryForTranscoderLog(payload: any): Observable<any> {
    let params: any = {};
    if (payload.page) {
      params['page'] = encodeURIComponent(payload.page);
    }
    if (payload.size) {
      params['size'] = encodeURIComponent(payload.size);
    }
    if (payload.searchString === '') {
      return this.http.get('transcoder/ui/log', {params: params});
    } else {
      const searchString = encodeURIComponent(payload.searchString);
      return this.http.get(`transcoder/ui/log/search/${searchString}`, {params: params});
    }
  }
}
