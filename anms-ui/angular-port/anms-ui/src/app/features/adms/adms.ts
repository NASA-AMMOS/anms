import {AfterViewInit, Component, inject} from '@angular/core';
import {AdmService} from '../../store/modules/adm-service';
import * as _ from 'lodash';
import {FormsModule} from '@angular/forms';

@Component({
  selector: 'app-adms',
  imports: [
    FormsModule
  ],
  templateUrl: './adms.html',
  styleUrl: './adms.css',
})
export class Adms implements AfterViewInit {
  protected admService = inject(AdmService);
  protected file: any = null;

  ngAfterViewInit(): void {
    if(!this.admService.hasAdms()) {
      this.admService.getAdms();
    }
  }

  protected hasValidFile() {
    return (!_.isNull(this.file) );
  }

  protected async uploadFile() {
    let yang_file: File = this.file;
    this.file = null;
    await this.admService.uploadAdm(yang_file);
    if (!_.isNil(this.admService.requestError()) && this.admService.requestError() !== '') {
      // toastr.error(this.requestError);
      console.log(this.admService.requestError());
    }
    else if (!_.isNil(this.admService.uploadStatus()) && this.admService.uploadStatus() !== '') {
      // toastr.success(this.uploadStatus);uploadStatus
      this.admService.getAdms();
    }
  }
}
