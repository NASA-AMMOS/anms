import {Injectable, signal, computed, inject} from '@angular/core';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {catchError, tap, delay} from 'rxjs/operators';
import {of, throwError} from 'rxjs';
import {ApiAdmService} from '../../shared/api-adm.service';

export interface Adm {
  data_model_id: number,
  namespace_type: string,
  enumeration: number,
  version_name: string,
  name: string,
  namespace: string,
  use_desc: string
}

export interface ErrorDetail {
  obj_type: any,
  name: any,
  issue: any
}

export interface UploadResponse {
  message?: string;
  data?: any;
}

export interface ErrorResponse {
  status: number;
  message?: string;
  error_details?: ErrorDetail[];
}

@Injectable({
  providedIn: 'root'
})
export class AdmService {
  private apiAdm = inject(ApiAdmService);

  // State signals (replacing Vuex state)
  private admsSignal = signal<Adm[]>([]);
  private requestErrorSignal = signal<string>('');
  private uploadErrorsSignal = signal<ErrorDetail[]>([]);
  private uploadStatusSignal = signal<string>('');
  private loadingSignal = signal<boolean>(true);

  // Computed getters (replacing Vuex getters)
  adms = this.admsSignal.asReadonly();
  requestError = this.requestErrorSignal.asReadonly();
  uploadErrors = this.uploadErrorsSignal.asReadonly();
  uploadStatus = this.uploadStatusSignal.asReadonly();
  loading = this.loadingSignal.asReadonly();

  // API base URL - adjust as needed
  private readonly API_BASE_URL = '/api/adms'; // Update with your actual API URL

  /**
   * Fetch all ADMs from the API
   * Equivalent to Vuex action: getAdms
   */
  public getAdms() {
    this.loadingSignal.set(true);
    this.requestErrorSignal.set('');

    try {
      this.apiAdm.apiGetAdms()
        .pipe(
          delay(1000), // Simulating the sleep function from Vue code
          tap((data) => {
            if (!data) {
              throw new Error('Receiving no data from request');
            }
          }),
          catchError((error: HttpErrorResponse) => {
            return throwError(() => error);
          })
        ).subscribe((response => {
        this.admsSignal.set(response || []);
        this.loadingSignal.set(false);
      }));
    } catch (error: any) {
      this.admsSignal.set([]);
      this.requestErrorSignal.set(error?.message || 'An error occurred');
      this.loadingSignal.set(false);
    }
  }

  /**
   * Upload an ADM file
   * @param admFile - The file to upload
   */
  public uploadAdm(admFile: File) {
    this.requestErrorSignal.set('');
    this.uploadErrorsSignal.set([]);

    try {
      this.apiAdm.apiUpdateAdm(admFile)
        .pipe(
          tap((res) => {
            if (!res) {
              throw new Error('Receiving no data from request');
            }
          }),
          catchError((error: HttpErrorResponse) => {
            return throwError(() => error);
          })
        ).subscribe((response) => {
        const message =
          response?.data?.message ||
          response?.message ||
          'Update success';

        this.uploadStatusSignal.set(message);
      });
    } catch (error: any) {
      const response = error?.error as ErrorResponse;
      const status = error?.status || 500;
      const message = response?.message || 'Internal server error';
      const errors = response?.error_details || [];

      this.requestErrorSignal.set(`${status}: ${message}`);
      this.uploadErrorsSignal.set(errors);
    }
  }

  /**
   * Reset upload state
   * Helper method to clear upload-related signals
   */
  resetUploadState(): void {
    this.uploadStatusSignal.set('');
    this.uploadErrorsSignal.set([]);
    this.requestErrorSignal.set('');
  }

  /**
   * Reset all state
   * Helper method to reset the entire service state
   */
  resetState(): void {
    this.admsSignal.set([]);
    this.requestErrorSignal.set('');
    this.uploadErrorsSignal.set([]);
    this.uploadStatusSignal.set('');
    this.loadingSignal.set(true);
  }

  public hasRequestError() {
    return this.requestError() != "";
  }

  public hasUploadErrors() {
    return this.uploadErrors().length > 0;
  }

  public hasAdms() {
    //return !this.loading && this.adms.length > 0;
    return this.adms().length > 0;
  }
}
