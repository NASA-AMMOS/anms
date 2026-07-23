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
  protected files: File[] = [];
  protected notificationService = inject(NotificationService);

  ngAfterViewInit(): void {
    if(!this.admService.hasAdms()) {
      this.admService.getAdms();
    }
  }

  protected hasValidFile(): boolean {
    return this.files.length > 0;
  }

  protected onFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    const selectedFiles = input.files;

    if (!selectedFiles || selectedFiles.length === 0) {
      this.files = [];
      return;
    }

    // Convert FileList -> File[]
    this.files = Array.from(selectedFiles);
  }


  protected async uploadFile() {
    if (this.files.length < 1) {
      this.notificationService.error('No .yang file selected');
      return;
    }



    this.files.forEach((yangFile) => {
      this.admService.uploadAdm(yangFile).subscribe({
        next: (message) => {
          this.notificationService.success(message);
          // Refresh ADMs after each successful upload
          this.admService.getAdms();
        },
        error: () => {
          this.notificationService.error(this.admService.requestError());
        },
      });
    });

    this.files = [];
  }

  protected downloadFile(adm: any): void {
    this.admService.downloadAdm(adm).subscribe({
      error: () => {
        this.notificationService.error(this.admService.requestError());
      }
    });
  }
}
