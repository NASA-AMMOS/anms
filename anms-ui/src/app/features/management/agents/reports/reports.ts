/*
 * Copyright (c) 2026 The Johns Hopkins University Applied Physics
 * Laboratory LLC.
 *
 * This file is part of the Asynchronous Network Management System (ANMS).
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *     http://www.apache.org/licenses/LICENSE-2.0
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * This work was performed for the Jet Propulsion Laboratory, California
 * Institute of Technology, sponsored by the United States Government under
 * the prime contract 80NM0018D0004 between the Caltech and NASA under
 * subcontract 1658085.
 */
import { Component, inject, Input, OnInit, signal } from '@angular/core';
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
      }).catch((error) => {
        console.error('Error preloading reports:', error);
        this.toastr.error('Error preloading reports: ' + error);
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
