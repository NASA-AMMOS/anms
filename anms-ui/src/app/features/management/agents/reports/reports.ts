import { ChangeDetectorRef, Component, inject, Input, OnInit, signal } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { ApiService } from '../../../../shared/api.service';
import { FormsModule } from '@angular/forms';

export interface ReportOption {
  ari: string;
  cbor: Array<any>;
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

  tableItems = signal<any[][][]>([]);
  tableHeaders = signal<string[][]>([]);
  title = '';
  reports: Record<string, any> = {};
  reportsHeader: Record<string, any> = {};
  loading = true;

  constructor(
  ) { }

  ngOnInit(): void {
    this.loading = true;

    // preload all reports like in mounted()
    const preloadPromises = this.rptts.map((rpt, index) =>
      this.apiService
        .apiEntriesForReport(this.registeredAgentsId, rpt.cbor)
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
    this.tableHeaders = signal<string[][]>([]);
    this.tableItems = signal<any[][][]>([]);

    const nonce_cbor = this.selected.cbor;
    this.apiService.apiEntriesForReport(
      this.registeredAgentsId,
      nonce_cbor
    ).subscribe({
      next: (res) => {
        this.processReport(res);

        const key = JSON.stringify(this.selected);

        this.reports[key] = this.tableItems();
        this.reportsHeader[key] = this.tableHeaders();
      },
      error: (error) => {
        console.error('reports error', error);
        this.toastr.error('reports error: ' + error);
        this.loading = false;
      },
      complete: () => {
        this.loading = false;
      }
    });
  }

  private processReport(report: any): void {
    if (report.length > 0 && report[0].reports?.flat().length > 0) {
      const flatReports = report[0].reports.flat();

      this.tableItems.update(items => [
        ...items,
        flatReports.map(
          (obj: { [s: string]: unknown } | ArrayLike<unknown>) =>
            Object.values(obj)
        )
      ]);

      this.tableHeaders.update(headers => [
        ...headers,
        Object.keys(flatReports[0])
      ]);
    }
  }
}
