import { Injectable } from '@angular/core';
import { ToastrService } from 'ngx-toastr';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  constructor(private toastr: ToastrService) {}

  success(message: string, title?: string, timeout = 10000, onClick: () => void = () => {} ) {
    const toast = this.toastr.success(message, title, {timeOut: timeout});
    if(onClick){
      toast.onTap.subscribe(() => onClick());
      toast.onHidden.subscribe(() => onClick());
    }
  }

  error(message: string, title?: string, timeout = 10000, onClick: () => void = () => {} ) {
    const toast = this.toastr.error(message, title, {timeOut: timeout});
    if(onClick){
      toast.onTap.subscribe(() => onClick());
      toast.onHidden.subscribe(() => onClick());
    }
  }

  warning(message: string, title?: string, timeout = 10000, onClick: () => void = () => {} ) {
    const toast = this.toastr.warning(message, title, {timeOut: timeout});
    if(onClick){
      toast.onTap.subscribe(() => onClick());
      toast.onHidden.subscribe(() => onClick());

    }
  }

  info(message: string, title?: string, timeout = 10000, onClick: () => void = () => {} ) {
    const toast = this.toastr.info(message, title, {timeOut: timeout});
    if(onClick){
      toast.onTap.subscribe(() => onClick());
      toast.onHidden.subscribe(() => onClick());
    }
  }
}
