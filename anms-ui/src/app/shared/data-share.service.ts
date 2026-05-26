import {Injectable, Signal, signal} from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class DataShareService {
  private breadcrumbsSignal = signal<string>('');
  private updateStatusSignal = signal<boolean>(false);

  public readonly breadcrumbs: Signal<string> = this.breadcrumbsSignal.asReadonly();
  public readonly updateStatus: Signal<boolean> = this.updateStatusSignal.asReadonly();

  public setBreadcrumbs(breadcrumbs: string) {
    this.breadcrumbsSignal.set(breadcrumbs);
  }

  public setUpdateStatus(status: boolean) {
    this.updateStatusSignal.set(status);
  }
}
