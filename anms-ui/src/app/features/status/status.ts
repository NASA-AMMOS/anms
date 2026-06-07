import {Component, inject, OnInit} from '@angular/core';
import {KeyValuePipe} from '@angular/common';
import {Utils} from '../../shared/utils';
import {ServiceStatusService} from '../../store/modules/service-status.service';

@Component({
  selector: 'app-status',
  imports: [
    KeyValuePipe
  ],
  templateUrl: './status.html',
  styleUrl: './status.css',
})
export class Status implements OnInit {

  protected serviceStatus = inject(ServiceStatusService);
  protected utils = inject(Utils);

  ngOnInit(): void {
    this.updateServiceStatus();
  }

  protected updateServiceStatus() {
    this.serviceStatus.updateStatus();
  }

}
