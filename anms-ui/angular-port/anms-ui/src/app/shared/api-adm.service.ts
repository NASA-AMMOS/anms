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
  // private adm_url = Constants.BASE_API_URL + '';
  private adm_url = '/api/core/adms';

  private createAuthenticationHeader(){
    return {
      Authorization: 'Bearer ' + Constants.USER_DETAILS.token
    };
  }

  //Main API
  public apiGetAdms(): Observable<any> {
    return this.http.get(this.adm_url, {headers: {accept: 'application/json'}});
  }
  public apiGetAdm(admEnum: any, namespace: any): Observable<any> {
    return this.http.get(this.adm_url + "/" + admEnum + "/" + namespace);
  }

  public apiUpdateAdm(file:  File): Observable<any> {
    const auth_headers = this.createAuthenticationHeader();
    const formData = new FormData();
    console.log(file);

    formData.append('adm', file);
    const headers = {
      ...auth_headers,
      'Content-Type': 'multipart/form-data'
    };
    // FIXME: upload URL
    // FIXME: unable to test upload CORS error - might be something to do with CAM login session token, etc.
    // return this.http.post(this.adm_url, formData, {headers});
    return this.http.post('/core/adms', formData, {headers});
  }
}
