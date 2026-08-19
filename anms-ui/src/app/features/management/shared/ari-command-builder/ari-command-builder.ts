import {Component, EventEmitter, Inject, inject, Input, OnInit, Output} from '@angular/core';
import {ApiService} from '../../../../shared/api.service';
import {Ari} from '../../agents/model/ari.model';
import {MatButtonToggle, MatButtonToggleGroup} from '@angular/material/button-toggle';
import {FormsModule} from '@angular/forms';
import {MatCheckbox} from '@angular/material/checkbox';
import {MatLabel, MatFormField, MatPrefix} from '@angular/material/form-field';
import {MatAutocomplete, MatAutocompleteTrigger, MatOption} from '@angular/material/autocomplete';
import {MatIcon} from '@angular/material/icon';
import {MatInput} from '@angular/material/input';
import {MatButton, MatIconButton} from '@angular/material/button';
import {MatSelect, MatSelectChange} from '@angular/material/select';
import {debounceTime, distinctUntilChanged, switchMap, tap} from 'rxjs/operators';
import {Subject, of} from 'rxjs';

export type AriCommandMode = 'builder' | 'text' | 'cbor';

export interface AriCommandOutput {
  mode: AriCommandMode;
  value: string;
}

type ParamInputKind = 'text' | 'ari-list';

const ARI_TYPE_NAMES = ['IDENT', 'CONST', 'CTRL', 'EDD', 'MAC', 'OPER', 'SBR', 'TBR', 'TYPEDEF'] as const;
type AriTypeName = (typeof ARI_TYPE_NAMES)[number];

interface AriParamState {
  index: number;
  name: string;
  type: string;
  kind: ParamInputKind;

  textValue: string;

  selectedAris: Ari[];
  searchText: '';
  filteredAris: Ari[];

  // Auto-filtered type from param's type definition (e.g., 'CONST' from 'CONST/AC')
  requiredAriType: AriTypeName | null;
}

@Component({
  selector: 'app-ari-command-builder',
  templateUrl: './ari-command-builder.html',
  styleUrls: ['./ari-command-builder.css'],
  imports: [
    MatButtonToggleGroup,
    FormsModule,
    MatButtonToggle,
    MatCheckbox,
    MatLabel,
    MatFormField,
    MatAutocompleteTrigger,
    MatAutocomplete,
    MatOption,
    MatIcon,
    MatInput,
    MatIconButton,
    MatPrefix,
    MatButton,
    MatSelect,
  ],
  standalone: true
})
export class AriCommandBuilder implements OnInit {
  protected ariMode: 'builder' | 'text' | 'cbor' = 'builder';
  protected executionSet = false;

  protected correlatorNonce = '';

  protected ariText = '';
  protected manualAriText = '';
  protected manualCborHex = '';

  protected aris: Ari[] = [];
  protected filteredAris: Ari[] = [];
  protected ariSearchText = '';

  // Type filter for main dropdown
  protected selectedTypeFilter: AriTypeName | 'ALL' = 'ALL';
  protected ariTypeNames: AriTypeName[] = [...ARI_TYPE_NAMES];

  protected selectedAri: Ari | null = null;
  protected ariParams: AriParamState[] = [];

  // Validation
  protected validationErrors: string[] = [];
  protected validationStatus: 'none' | 'checking' | 'valid' | 'invalid' = 'none';
  protected validationMessage: string = '';

  // Debounced backend validation for text/CBOR modes
  private textInput$ = new Subject<string>();
  private cborInput$ = new Subject<string>();

  @Output()
  commandReady = new EventEmitter<AriCommandOutput>();

  @Input() initialMode: AriCommandMode = 'builder';
  @Input() initialCborCommands: string[] = [];

  constructor(
    private api: ApiService,
  ) {
    // Subscribe to ARI list updates from server
    this.api.apiQueryForARIs().subscribe({
      next: (data: Ari[]) => {
        this.aris = data;
        this.applyMainFilter();
      },
      error: (err) => console.error('Failed to load ARIs', err),
    });
  }

  ngOnInit(): void {
    this.ariMode = this.initialMode;

    if (this.initialCborCommands.length > 0) {
      this.manualCborHex = this.initialCborCommands.join(',');
    }

    // Debounced backend validation for text mode
    this.textInput$.pipe(
      debounceTime(400),
      distinctUntilChanged(),
      switchMap((value: string) => {
        if (!value.trim()) {
          return of({valid: false, error: 'ARI text is required'});
        }
        return this.api.apiValidateAri(value.trim(), 'text');
      }),
      tap((result) => {
        if (result.valid) {
          this.validationStatus = 'valid';
          this.validationMessage = '';
          this.validationErrors = [];
        } else {
          this.validationStatus = 'invalid';
          this.validationMessage = result.error || 'Invalid ARI';
          this.validationErrors = [this.validationMessage];
        }
      })
    ).subscribe();

    // Debounced backend validation for CBOR mode
    this.cborInput$.pipe(
      debounceTime(400),
      distinctUntilChanged(),
      switchMap((value: string) => {
        if (!value.trim()) {
          return of({valid: false, error: 'CBOR hex is required'});
        }
        return this.api.apiValidateAri(value.trim(), 'cbor');
      }),
      tap((result) => {
        if (result.valid) {
          this.validationStatus = 'valid';
          this.validationMessage = '';
          this.validationErrors = [];
        } else {
          this.validationStatus = 'invalid';
          this.validationMessage = result.error || 'Invalid CBOR';
          this.validationErrors = [this.validationMessage];
        }
      })
    ).subscribe();
  }

  protected onTypeFilterChange(change: MatSelectChange | string | null): void {
    this.selectedTypeFilter = (typeof change === 'string' ? change : change?.value) ?? 'ALL';

    // Fetch server-side filtered list when type changes (or resets to ALL)
    const typeForServer = this.selectedTypeFilter === 'ALL' ? undefined : this.selectedTypeFilter;
    this.api.apiQueryForARIs(typeForServer).subscribe({
      next: (data: Ari[]) => {
        this.aris = data;
        this.applyMainFilter();
      },
      error: (err) => console.error('Failed to load ARIs', err),
    });
  }

  protected filterAris(value: string | Ari | null): void {
    this.ariSearchText = typeof value === 'string' ? value : this.displayAri(value);
    this.applyMainFilter();
  }

  protected onModeChange(): void {
    // Reset validation state when switching modes
    this.validationStatus = 'none';
    this.validationMessage = '';
    this.validationErrors = [];
  }

  private applyMainFilter(): void {
    const search = this.ariSearchText?.toLowerCase() ?? '';

    this.filteredAris = this.aris.filter(ari => {
      // Text search (server already filtered by type, client filters by text)
      if (search && !ari.display.toLowerCase().includes(search)) {
        return false;
      }
      return true;
    });
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

        requiredAriType: this.getTypeFilterFromParamType(type),
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

    // Also check for type-specific AC, e.g. "CONST/AC", "CTRL/AC"
    const parts = type.split('/');
    const firstNonEmpty = parts.find(Boolean);
    if (firstNonEmpty && ARI_TYPE_NAMES.includes(firstNonEmpty as AriTypeName) &&
        (parts.includes('AC') || parts.includes('EXECSET'))) {
      return 'ari-list';
    }

    return 'text';
  }

  /**
   * Extract the ARI type filter from a param type string.
   * e.g., "CONST/AC" → "CONST", "CTRL/AC" → "CTRL", "/ARITYPE/AC" → null (any type)
   */
  private getTypeFilterFromParamType(type: string): AriTypeName | null {
    const parts = type.split('/');
    const firstNonEmpty = parts.find(Boolean);

    if (
      firstNonEmpty &&
      ARI_TYPE_NAMES.includes(firstNonEmpty as AriTypeName) &&
      firstNonEmpty !== 'TYPEDEF'
    ) {
      return firstNonEmpty as AriTypeName;
    }

    return null;
  }

  protected onAriSelected(ari: Ari): void {
    this.selectedAri = ari;
    this.ariParams = this.buildParamState(ari);
    // Initialize each param's filtered list with auto-type-restriction
    for (const param of this.ariParams) {
      if (param.kind === 'ari-list') {
        param.filteredAris = this.aris.filter(a =>
          !param.requiredAriType || a.type_name === param.requiredAriType
        );
      }
    }
    this.ariSearchText = ari.display;
    this.updateAriText();
  }

  protected onParamAriSelectedPrim(paramIndex: number, ari: string): void {
    const param = this.ariParams[paramIndex];
    const newAri: Ari = {
      obj_metadata_id: 0,
      obj_id: 0,
      name: ari,
      namespace: './',
      data_model_name: '',
      type_name: '',
      data_model_id: 0,
      parm_id: null,
      actual: true,
      display: ari,
      param_names: [],
      param_types: [],
    };

    param.selectedAris = [...param.selectedAris, newAri];

    param.searchText = '';
    param.filteredAris = this.aris.filter(a =>
      !param.requiredAriType || a.type_name === param.requiredAriType
    );

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
    param.filteredAris = this.aris.filter(a =>
      !param.requiredAriType || a.type_name === param.requiredAriType
    );

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
      this.validationErrors = [];
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

  protected validate(): boolean {
    this.validationErrors = [];

    switch (this.ariMode) {
      case 'builder':
        this.validateBuilderMode();
        break;
      case 'text':
        this.validateTextMode();
        break;
      case 'cbor':
        this.validateCborMode();
        break;
    }

    return this.validationErrors.length === 0;
  }

  private validateBuilderMode(): void {
    if (!this.selectedAri) {
      return;
    }

    // Check required text params are filled
    for (const param of this.ariParams) {
      if (param.kind !== 'text') continue;
      if (!param.textValue?.trim()) {
        this.validationErrors.push(
          `Parameter "${param.name}" (${param.type}) is required`
        );
      }
    }

    // Check ARI param type mismatches
    for (const param of this.ariParams) {
      if (param.kind !== 'ari-list') continue;
      if (!param.requiredAriType) continue;

      for (const selectedAri of param.selectedAris) {
        if (selectedAri.type_name && selectedAri.type_name !== param.requiredAriType) {
          this.validationErrors.push(
            `Parameter "${param.name}" expects ${param.requiredAriType} but "${selectedAri.display}" is ${selectedAri.type_name}`
          );
        }
      }
    }
  }

  protected onTextAriInput(event: Event): void {
    const value = (event.target as HTMLTextAreaElement).value;
    this.manualAriText = value;
    this.validationStatus = 'checking';
    this.validationMessage = '';
    this.validationErrors = [];
    this.textInput$.next(value);
  }

  /**
   * Called when the user types in the CBOR hex input field.
   * Triggers debounced backend validation.
   */
  protected onCborHexInput(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.manualCborHex = value;
    this.validationStatus = 'checking';
    this.validationMessage = '';
    this.validationErrors = [];
    this.cborInput$.next(value);
  }

  private validateTextMode(): void {
    const text = this.manualAriText?.trim() ?? '';
    if (!text) {
      this.validationErrors.push('ARI text is required');
      this.validationStatus = 'invalid';
      return;
    }
    // At send time, use the latest backend validation result
    if (this.validationStatus === 'invalid') {
      this.validationErrors.push(this.validationMessage || 'ARI failed backend validation');
      return;
    }
    if (this.validationStatus === 'none') {
      this.validationErrors.push('ARI has not been validated yet');
      this.validationStatus = 'invalid';
    }
  }

  private validateCborMode(): void {
    const hex = this.manualCborHex?.trim() ?? '';
    if (!hex) {
      this.validationErrors.push('CBOR hex is required');
      this.validationStatus = 'invalid';
      return;
    }
    // At send time, use the latest backend validation result
    if (this.validationStatus === 'invalid') {
      this.validationErrors.push(this.validationMessage || 'CBOR failed backend validation');
      return;
    }
    if (this.validationStatus === 'none') {
      this.validationErrors.push('CBOR has not been validated yet');
      this.validationStatus = 'invalid';
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

    param.filteredAris = this.aris.filter(ari => {
      // Auto-restrict by required type
      if (param.requiredAriType && ari.type_name !== param.requiredAriType) {
        return false;
      }
      // Text search
      if (search && !ari.display?.toLowerCase().includes(search)) {
        return false;
      }
      return true;
    });
  }

  protected send(): void {
    if (!this.validate()) {
      return;
    }

    const value = this.getCommandValue();

    this.commandReady.emit({
      mode: this.ariMode,
      value,
    });
  }

  private normalizedCborInput(): string {
    const value = this.manualCborHex.trim();

    if (!value) {
      return '';
    }

    return value.startsWith('0x') ? value : `0x${value}`;
  }

  private getCommandValue(): string {
    switch (this.ariMode) {
      case 'builder':
        return this.ariText.trim();

      case 'text':
        return this.manualAriText.trim();

      case 'cbor':
        return this.normalizedCborInput();
    }
  }

}
