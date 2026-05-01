import {Component, inject, Input, OnInit} from '@angular/core';
import {ToastrService} from 'ngx-toastr';
import {ApiService} from '../../../../shared/api.service';
import {FormsModule} from '@angular/forms';

export interface ReportOption {
  exec_set: string;
  nonce_cbor: string;
}

@Component({
  selector: 'app-reports',
  templateUrl: './reports.html',
  styleUrls: ['./reports.css'],
  standalone: true,
  imports: [
    FormsModule
  ]
})
export class Reports implements OnInit {
  @Input() agentName!: string;
  @Input() rptts: ReportOption[] = [];
  @Input() registeredAgentsId!: string;

  apiService = inject(ApiService);
  toastr = inject(ToastrService);

  selected?: ReportOption;
  tableHeaders: string[][] = [];
  tableItems: any[][][] = [];
  title = '';
  reports: Record<string, any> = {};
  reportsHeader: Record<string, any> = {};
  loading = true;

  constructor() {
  }

  ngOnInit(): void {
    this.loading = true;

    // preload all reports like in mounted()
    const preloadPromises = this.rptts.map((rpt, index) =>
      this.apiService
        .apiEntriesForReport(this.registeredAgentsId, rpt.nonce_cbor)
        .subscribe({
          next: (res: any) => {
            this.reports[index] = res;
          }, error: (error: any) => {
            console.error('reports error', error);
          }
        })
    );

    Promise.all(preloadPromises)
      .finally(() => {
        this.loading = false;
      });
  }

  async onReportSelect(): Promise<void> {
    if (!this.selected) {
      return;
    }

    this.loading = true;
    this.tableHeaders = [];
    this.tableItems = [];

    const nonce_cbor = this.selected.nonce_cbor;

    try {
      this.apiService.apiEntriesForReport(
        this.registeredAgentsId,
        encodeURIComponent(nonce_cbor)
      ).subscribe((res) => {
        this.processReport(res);

        const key = JSON.stringify(this.selected);
        this.reports[key] = this.tableItems;
        this.reportsHeader[key] = this.tableHeaders;
      });
    } catch (error: any) {
      console.error('reports error', error);
      this.toastr.error('reports error: ' + error);
    } finally {
      this.loading = false;
    }
  }

  private processReport(report: any): void {
    let rpt: any[] = [];

    if (this.selected && this.selected.exec_set in report) {
      rpt = report[this.selected.exec_set];
    } else if (this.selected) {
      rpt = report[this.selected.nonce_cbor];
    }

    if (!rpt || rpt.length === 0) {
      return;
    }

    // header from first item keys
    const holdHeader: string[] = Object.keys(rpt[0]);

    const currTableItems: any[][] = [];

    for (const item of rpt) {
      const row: any[] = [];
      for (const h of holdHeader) {
        row.push(item[h]);
      }
      currTableItems.push(row.flat());
    }

    this.tableHeaders.push(holdHeader);
    this.tableItems.push(currTableItems);
  }
}
