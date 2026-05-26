import {inject, Injectable, signal} from '@angular/core';

import {throwError} from 'rxjs';
import {catchError, finalize} from 'rxjs/operators';
import {Constants} from '../../shared/constants';
import * as _ from 'lodash';
import {ApiService} from '../../shared/api.service';

export interface Alert {
  id: string;
  // Add other alert properties as needed
}

export interface ServiceStatus {
  [key: string]: string;
}

@Injectable({
  providedIn: 'root'
})
export class ServiceStatusService {

  // private http = inject(HttpClient);
  private api = inject(ApiService);

  // Signals for state management
  private _errorServices = signal<{ [key: string]: string }>({});
  private _normalServices = signal<{ [key: string]: string }>({});
  private _updateError = signal<string>('');
  private _loading = signal<boolean>(false);
  private _alerts = signal<Alert[]>([]);
  private _alertIds = signal<string[]>([]);

  // Public signals for components to subscribe to
  public readonly errorServices = this._errorServices.asReadonly();
  public readonly normalServices = this._normalServices.asReadonly();
  public readonly updateError = this._updateError.asReadonly();
  public readonly loading = this._loading.asReadonly();
  public readonly alerts = this._alerts.asReadonly();
  public readonly alertIds = this._alertIds.asReadonly();


  updateStatus(): void {
    this._loading.set(true);
    this._updateError.set('');

    // Get alerts
    // FIXME: test display alerts
    // FIXME: this.http.get<IAlert[]>('/api/alerts/incoming')
    this.api.apiGetAlerts().pipe(
      catchError(error => {
        console.error('update status error', error);
        return throwError(() => error);
      })
    ).subscribe({
      next: (res) => {
        this._alerts.set(res);

        // TODO rethink tracking alerts for multiple accounts
        res.forEach((alert: any) => {
          if (!this._alertIds().includes(alert.id)) {
            this._alertIds.update(ids => [...ids, alert.id]);
          }
        });
      },
      error: (error) => {
        console.error('Error fetching alerts:', error);
      }
    });

    // Get service status
    // FIXME: ('/api/core/service_status')
    this.api.apiGetServiceStatus().pipe(
      catchError(error => {
        console.error('update status error', error);
        this._loading.set(false);
        this._errorServices.set({});
        this._normalServices.set({});
        this._updateError.set(error.message || 'Unknown error');
        return throwError(() => error);
      }),
      finalize(() => {
        // This will be handled in the next observable chain
      })
    ).subscribe({
      next: (res) => {
        let jsonStatus: ServiceStatus = {};

        try {
          jsonStatus = typeof res === 'object' ? res : JSON.parse(JSON.stringify(res));
        } catch (e) {
          console.error(e);
          jsonStatus = {};
        }

        // Filter out status
        let errorServices: { [key: string]: string } = {};
        let normalServices: { [key: string]: string } = {};

        Constants.service_info.names.forEach((name: string) => {
          if (jsonStatus[name] === undefined) {
            errorServices[name] = Constants.service_info.error_status[0];
          } else if (!Constants.service_info.normal_status.includes(jsonStatus[name])) {
            errorServices[name] = jsonStatus[name];
          } else {
            normalServices[name] = jsonStatus[name];
          }
        });

        // Simulate sleep delay
        setTimeout(() => {
          this._normalServices.set(normalServices);
          this._errorServices.set(errorServices);
          this._loading.set(false);
        }, 1000);
      },
      error: (error) => {
        console.error('Error fetching service status:', error);
        setTimeout(() => {
          this._normalServices.set({});
          this._errorServices.set({});
          this._updateError.set(error.message || 'Unknown error');
          this._loading.set(false);
        }, 1000);
      }
    });
  }

  setAlert(index: number): void {
    const alertId = this._alerts()[index]?.id;
    if (alertId) {
      // FIXME: this.http.post(`/api/acknowledge-alerts/${alertId}`, {})
      this.api.apiAcknowledgeAlerts(alertId).subscribe({
        next: () => {
          // Handle successful acknowledgment
          console.log(`Alert ${alertId} acknowledged`);
        },
        error: (error) => {
          console.error('Error acknowledging alert:', error);
        }
      });

      // Update local state (if needed)
      // Note: In a real app, you'd want to properly update the alert visibility
      // This would depend on how your alert data structure works
    }
  }

  public hasUpdateError() {
    return this.updateError() !== "";
  }

  public hasData() {
    return !_.isEmpty(this.normalServices());
  }

  public numberErrorServices() {
    // return Object.keys(this.errorServices()).length;
    return 100;
  }
}
