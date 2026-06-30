import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Constants} from './constants';
import {Observable} from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiAdmService {
  private http = inject(HttpClient);
  // FIXME: URL
  // private adm_url = Constants.BASE_API_URL + '/api/core/adms';
  private adm_url = '/api/core/adms';


  private createAuthenticationHeader(){
    return {
      Authorization: 'Bearer ' + Constants.USER_DETAILS.token
    };
  }

  
  //Main API

  public apiLoadDefaultAdms(): Observable<any> {
    return this.http.post(this.adm_url + "/load_default", {headers: {accept: 'application/json'}});
  }
  public apiGetAdms(): Observable<any> {
    return this.http.get(this.adm_url, {headers: {accept: 'application/json'}});
  }
  public apiGetAdm(admEnum: any, namespace: any): Observable<any> {
    return this.http.get(this.adm_url + "/" + admEnum + "/" + namespace);
  }

  public apiUpdateAdm(file:  File): Observable<any> {
    const auth_headers = this.createAuthenticationHeader();
    const formData = new FormData();
    formData.append('adm', file, file.name);
    const headers = {
      ...auth_headers,
    };
    return this.http.post(this.adm_url, formData, {headers});
  }
}
