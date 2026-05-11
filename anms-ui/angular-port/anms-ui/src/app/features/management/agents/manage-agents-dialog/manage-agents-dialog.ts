import {Component, inject, Inject, OnInit} from '@angular/core';
import { ApiService } from '../../../../shared/api.service';
import {Crud} from '../crud/crud';
import {MatButton, MatIconButton} from '@angular/material/button';
import {MatDialogContent, MatDialogTitle} from '@angular/material/dialog';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {AgentInfo} from '../agent-modal/agent-modal';
import {MatChip, MatChipSet} from '@angular/material/chips';
import {MatDivider} from '@angular/material/divider';
import {MatButtonToggle, MatButtonToggleGroup} from '@angular/material/button-toggle';
import {FormsModule} from '@angular/forms';
import {MatFormField, MatPrefix, MatLabel} from '@angular/material/form-field';
import {MatCheckbox} from '@angular/material/checkbox';
import {MatInput} from '@angular/material/input';
import {Ari} from '../model/ari.model';
import {MatAutocomplete, MatAutocompleteTrigger, MatOption} from '@angular/material/autocomplete';
import {MatIcon} from '@angular/material/icon';
import {NotificationService} from '../../../../shared/notification.service';
import {forkJoin, switchMap} from 'rxjs';

type ParamInputKind = 'text' | 'ari-list'; // Leave build.js enumerated types as plaintext for now, let backend worry about validation

interface AriParamState {
  index: number;
  name: string;
  type: string;
  kind: ParamInputKind;

  textValue: string;

  selectedAris: Ari[];
  searchText: string;
  filteredAris: Ari[];
}

@Component({
  selector: 'app-manage-agents-dialog',
  imports: [
    MatButton,
    MatDialogContent,
    MatDialogTitle,
    MatChipSet,
    MatChip,
    MatDivider,
    MatButtonToggleGroup,
    MatButtonToggle,
    FormsModule,
    MatFormField,
    MatCheckbox,
    MatInput,
    MatPrefix,
    MatLabel,
    MatAutocompleteTrigger,
    MatAutocomplete,
    MatOption,
    MatIcon,
    MatIconButton
  ],
  templateUrl: './manage-agents-dialog.html',
  styleUrl: './manage-agents-dialog.css',
  standalone: true
})

export class ManageAgentsDialog implements OnInit {
  protected agentsInfo: AgentInfo[];

  protected ariMode: 'builder' | 'text' | 'cbor' = 'builder';
  protected executionSet = false;

  protected correlatorNonce = '';

  protected selectedAriText = '';
  protected hexInput = '';
  protected ariText = '';
  protected manualAriText = '';
  protected manualCborHex = '';

  protected aris: Ari[] = [];
  protected filteredAris: Ari[] = [];
  protected ariSearchText = '';

  protected selectedAri: Ari | null = null; // used for single select in main input dropdown
  protected selectedAris: Ari[] | null = null; // used for parameter ari multi-select input dropdowns
  protected ariParams: AriParamState[] = [];
  protected notificationService = inject(NotificationService);




  constructor(
    private dialogRef: MatDialogRef<ManageAgentsDialog>,
    @Inject(MAT_DIALOG_DATA) public data: AgentInfo[],
    private api: ApiService,
  ) {
    this.agentsInfo = data;
  }

  ngOnInit(): void {
    this.api.apiQueryForARIs().subscribe({
      next: (data: Ari[]) => {
        this.aris = data;
        this.filteredAris = data;
      },
      error: (err) => console.error('Failed to load ARIs', err),
    });
  }

  close(): void {
    this.dialogRef.close();
  }

  protected submitTextInput(): void { // currently just sets ariText. should this do validation in the future?
    this.ariText = `0x${this.hexInput}`;
  }

  protected filterAris(value: string | Ari | null): void {
    const search =
      typeof value === 'string'
        ? value.toLowerCase()
        : this.displayAri(value).toLowerCase();

    this.filteredAris = this.aris.filter(ari =>
      ari.display.toLowerCase().includes(search)
    );
  }

  protected buildParamState(ari: Ari): AriParamState[] {
    return (ari.param_names ?? []).map((paramName, index) => {
      const type = ari.param_types?.[index] ?? '';

      return {
        index,
        name: paramName,
        type,
        kind: this.getParamKind(type),

        textValue: '',

        selectedAris: [],
        searchText: '',
        filteredAris: [],
      };
    });
  }

  protected getParamKind(type: string): ParamInputKind {
    if (
      type === '/ARITYPE/AC' ||
      type === '/ARITYPE/EXECSET' ||
      type.includes('TYPEDEF')
    ) {
      return 'ari-list';
    }

    return 'text';
  }

  protected onAriSelected(ari: Ari): void {
    this.selectedAri = ari;
    this.ariParams = this.buildParamState(ari);
    this.updateAriText();
  }

  protected onParamAriSelected(paramIndex: number, ari: Ari): void {
    const param = this.ariParams[paramIndex];

    const alreadySelected = param.selectedAris.some(
      selected => selected.obj_metadata_id === ari.obj_metadata_id
    );

    if (!alreadySelected) {
      param.selectedAris = [...param.selectedAris, ari];
    }

    param.searchText = '';
    param.filteredAris = this.aris;

    this.updateAriText();
  }

  protected removeParamAri(paramIndex: number, ari: Ari): void {
    const param = this.ariParams[paramIndex];

    param.selectedAris = param.selectedAris.filter(
      selected => selected.obj_metadata_id !== ari.obj_metadata_id
    );

    this.updateAriText();
  }

  protected updateAriText(): void {
    const rawAriText = this.buildRawAriText();

    if (!rawAriText) {
      this.ariText = '';
      return;
    }

    this.ariText = this.wrapExecutionSetIfNeeded(rawAriText);
  }

  protected getPreviewLabel(): string {
    switch (this.ariMode) {
      case 'builder':
        return 'ARI Text:';
      case 'text':
        return 'ARI Text:';
      case 'cbor':
        return 'CBOR Hex:';
    }
  }

  protected getPreviewText(): string {
    switch (this.ariMode) {
      case 'builder':
        return this.ariText?.trim() || 'None selected';

      case 'text':
        return this.manualAriText?.trim() || 'No ARI text entered';

      case 'cbor':
        return this.normalizedCborInput() || 'No CBOR hex entered';
    }
  }

  private buildRawAriText(): string {
    if (!this.selectedAri) {
      return '';
    }

    if (this.selectedAri.actual || this.ariParams.length === 0) {
      return this.selectedAri.display;
    }

    const paramText = this.ariParams
      .map((param) => this.renderParamValue(param))
      .join(',');

    return (
      `ari://${this.selectedAri.namespace}` +
      `/${this.selectedAri.data_model_name}` +
      `/${this.selectedAri.type_name}` +
      `/${this.selectedAri.name}` +
      `(${paramText})`
    );
  }

  private wrapExecutionSetIfNeeded(rawAriText: string): string {
    if (!this.executionSet) {
      return rawAriText;
    }

    const noncePart = this.correlatorNonce
      ? `n=${this.correlatorNonce};`
      : '';

    return `ari:/EXECSET/${noncePart}(${rawAriText})`;
  }

  protected renderParamValue(param: AriParamState): string {
    if (param.kind === 'ari-list') {
      const values = param.selectedAris.map((ari) => ari.display);

      if (param.type.includes('TYPEDEF') && values.length === 1) {
        return values[0];
      }

      if (values.length > 0) {
        return `/AC/(${values.join(',')})`;
      }

      return '';
    }

    return param.textValue ?? '';
  }

  protected displayAri = (ari: Ari | null): string => {
    return ari?.display ?? '';
  };

  protected filterParamAris(paramIndex: number): void {
    const param = this.ariParams[paramIndex];
    const search = param.searchText.toLowerCase();

    param.filteredAris = this.aris.filter(ari =>
      ari.display?.toLowerCase().includes(search)
    );
  }

  protected send(): void {
    if (this.ariMode === 'cbor') {
      this.sendRawCbor(this.normalizedCborInput());
      return;
    }

    const ariText =
      this.ariMode === 'builder'
        ? this.ariText.trim()
        : this.manualAriText.trim();

    this.transcodeThenSend(ariText);
  }

  private transcodeThenSend(ariText: string): void {
    if (!ariText) {
      this.notificationService.error('No ARI text to send');
      return;
    }

    this.api.apiPutTranscodedString(ariText).pipe(
      switchMap((transcodeResponse) =>
        this.api.apiGetTranscoderLogById(`${transcodeResponse.id}`)
      ),
      switchMap((logResponse) => {
        const cbor = logResponse.cbor;

        if (!cbor) {
          throw new Error(`${logResponse.ari}`);
        }

        return this.sendRawCborRequest(cbor);
      }),
    ).subscribe({
      next: () => this.notificationService.success('ARI sent to selected agents'),
      error: (err) => this.notificationService.error(err, 'Error sending ARI'),
    });
  }

  private sendRawCbor(cborHex: string): void {
    if (!cborHex) {
      this.notificationService.error('No CBOR hex to send');
      return;
    }

    this.sendRawCborRequest(cborHex).subscribe({
      next: () => this.notificationService.success('CBOR sent to selected agents'),
      error: (err) => this.notificationService.error(err, 'Error sending CBOR'),
    });
  }

  private sendRawCborRequest(cborHex: string) {
    const requests = this.agentsInfo.map((agent) =>
      this.api.apiSendRawCommand(agent.agent_endpoint_uri, cborHex)
    );

    return forkJoin(requests);
  }

  private normalizedCborInput(): string {
    const value = this.manualCborHex.trim();

    if (!value) {
      return '';
    }

    return value.startsWith('0x') ? value : `0x${value}`;
  }

}
