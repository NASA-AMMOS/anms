import {AfterViewInit, Component, inject} from '@angular/core';
import {AdmService} from '../../store/modules/adm-service';
import * as _ from 'lodash';
import {FormsModule} from '@angular/forms';
import {NotificationService} from '../../shared/notification.service';

@Component({
  selector: 'app-adms',
  imports: [
    FormsModule
  ],
  templateUrl: './adms.html',
  styleUrl: './adms.css',
  standalone: true,
})
export class Adms implements AfterViewInit {
  protected admService = inject(AdmService);
  protected file: any = null;
  protected notificationService = inject(NotificationService);

  ngAfterViewInit(): void {
    if(!this.admService.hasAdms()) {
      this.admService.getAdms();
    }
  }

  protected hasValidFile() {
    return (!_.isNull(this.file) );
  }

  protected async uploadFile() {
    if (!this.file) {
      this.notificationService.error('No .yang file selected');
      return;
    }

    const yangFile = this.file;
    this.file = null;

    this.admService.uploadAdm(yangFile).subscribe({
      next: (message) => {
        this.notificationService.success(message);
        this.admService.getAdms();
      },
      error: () => {
        this.notificationService.error(this.admService.requestError());
      },
    });
  }

  protected downloadFile(adm: any): void {
    this.admService.downloadAdm(adm).subscribe({
      error: () => {
        this.notificationService.error(this.admService.requestError());
      }
    });
  }
}
