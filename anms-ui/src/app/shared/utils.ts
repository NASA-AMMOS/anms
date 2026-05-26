import { Injectable } from '@angular/core';
import {KeyValue} from '@angular/common';

@Injectable({
  providedIn: 'root',
})
export class Utils {

  public sortKeyValueRecords(a: KeyValue<string, any>, b: KeyValue<string, any>, isDesc?: boolean) {
    // sort by key in descending order if isDesc is true, otherwise in ascending order by default
    if(isDesc) {
      return a.key > b.key ? -1 : (b.key > a.key ? 1 : 0);
    }
    return a.key > b.key ? 1 : (b.key > a.key ? -1 : 0);
  }
}
