import {Component, OnInit, inject, ViewChild} from '@angular/core';
import { SelectionModel } from '@angular/cdk/collections';
import {
  MatCell,
  MatCellDef,
  MatColumnDef,
  MatHeaderCell,
  MatHeaderCellDef, MatHeaderRow, MatHeaderRowDef, MatRow, MatRowDef, MatTable,
  MatTableDataSource
} from '@angular/material/table';
import {AriCommandBuilder, AriCommandOutput} from '../shared/ari-command-builder/ari-command-builder';

import { ApiService } from '../../../shared/api.service';
import { NotificationService } from '../../../shared/notification.service';
import {MatPaginator, PageEvent} from '@angular/material/paginator';
import {MatButton} from '@angular/material/button';
import {MatCheckbox} from '@angular/material/checkbox';
import {MatFormField, MatInput} from '@angular/material/input';
import {FormsModule} from '@angular/forms';
import {MatDivider} from '@angular/material/divider';
import {MatLabel} from '@angular/material/form-field';
import { CommandHandoffService } from '../../../shared/command-handoff.service';
import {Router} from '@angular/router';

export interface TranscoderLogEntry {
  transcoder_log_id: number;
  input_string: string;
  parsed_as: string;
  ari: string;
  uri: string;
  cbor: string;
}

export interface TranscoderLogResponse {
  items: Record<number, TranscoderLogEntry>;
  total: number;
  page: number;
  size: number;
}

@Component({
  selector: 'app-builder',
  templateUrl: './builder.html',
  styleUrls: ['./builder.css'],
  imports: [
    MatColumnDef,
    MatHeaderCell,
    MatCell,
    MatHeaderCellDef,
    MatCellDef,
    MatHeaderRow,
    MatHeaderRowDef,
    MatRow,
    MatRowDef,
    MatButton,
    MatPaginator,
    MatCheckbox,
    MatTable,
    MatInput,
    MatFormField,
    FormsModule,
    MatDivider,
    MatLabel,
    AriCommandBuilder
  ],
  standalone: true
})
export class Builder implements OnInit {
  private api = inject(ApiService);
  private notificationService = inject(NotificationService);
  private commandHandoffService = inject(CommandHandoffService);
  private router = inject(Router);

  @ViewChild(MatPaginator)
  paginator!: MatPaginator;

  protected displayedColumns: string[] = [
    'select',
    'id',
    'inputString',
    'parsedAs',
    'cbor',
    'ari',
  ];

  protected dataSource = new MatTableDataSource<TranscoderLogEntry>([]);
  protected selection = new SelectionModel<TranscoderLogEntry>(true, []);

  protected searchText = '';

  protected pageIndex = 0;
  protected pageSize = 10;
  protected totalResults = 0;

  ngOnInit(): void {
    this.loadTranscoderLogs();
  }

  protected loadTranscoderLogs(): void {
    const payload = {
      searchString: this.searchText.trim(),
      page: this.pageIndex + 1, // angular page indices are 0-indexed, backend transcoder table is not
      size: this.pageSize,
    };

    this.api.apiQueryForTranscoderLog(payload).subscribe({
      next: (response: TranscoderLogResponse) => {
        const logs = Object.values(response.items ?? {});

        this.dataSource.data = logs;
        this.totalResults = response.total ?? logs.length;

        // Clear stale selections when the page/search changes
        this.selection.clear();
      },
      error: (err) => {
        console.error('Failed to load transcoder logs', err);
        this.notificationService.error(err, 'Failed to load transcoder logs');
      },
    });
  }

  protected applyFilter(): void {
    this.pageIndex = 0;

    if (this.paginator) {
      this.paginator.firstPage();
    }

    this.loadTranscoderLogs();
  }

  protected handlePageEvent(event: PageEvent): void {
    this.pageIndex = event.pageIndex;
    this.pageSize = event.pageSize;

    this.loadTranscoderLogs();
  }

  protected handleBuiltCommand(command: AriCommandOutput): void {
    const value = command.value.trim();

    if (!value) {
      this.notificationService.error('No command value to submit');
      return;
    }

    this.api.apiPutTranscodedString(value).subscribe({
      next: (response) => {
        this.notificationService.success(
          `${response.status ?? 'Transcoded successfully'}`
        );

        this.pageIndex = 0;
        this.loadTranscoderLogs();
      },
      error: (err) => {
        this.notificationService.error(err, 'Failed to transcode ARI');
      },
    });
  }

  protected getParsedAs(log: TranscoderLogEntry): string {
    return log.uri ? 'URI' : 'error';
  }

  protected toggleRow(log: TranscoderLogEntry): void {
    this.selection.toggle(log);
  }

  protected sendToAgents(): void {
    const cborCommands = this.selection.selected
      .map((log) => log.cbor)
      .filter((cbor): cbor is string => !!cbor);

    if (cborCommands.length != this.selection.selected.length) {
      this.notificationService.error('Not all selected entries contain valid CBOR', 'Erroneous Entries Selected'); // FIXME: toastr messages appear at top of page which might not be visible if window is scrolled down to table
      return;
    }

    this.commandHandoffService.setCborCommands(cborCommands);
    this.router.navigate(['/dashboard/agents']);
  }
}
