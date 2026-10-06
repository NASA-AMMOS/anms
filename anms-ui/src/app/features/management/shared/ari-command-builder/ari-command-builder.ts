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
import {NgTemplateOutlet} from '@angular/common';

export type AriCommandMode = 'builder' | 'text' | 'cbor';

export interface AriCommandOutput {
  mode: AriCommandMode;
  value: string;
}

type ParamInputKind = 'text' | 'ari-list';

const ARI_TYPE_NAMES = ['IDENT', 'CONST', 'CTRL', 'EDD', 'MAC', 'OPER', 'SBR', 'TBR', 'TYPEDEF'] as const;
type AriTypeName = (typeof ARI_TYPE_NAMES)[number];

interface AriSelection extends Ari {
  parameters?: AriParamState[];
}

interface AriParamState {
  index: number;
  name: string;
  type: string;
  kind: ParamInputKind;
  wrapInAc: boolean;

  textValue: string;

  selectedAris: AriSelection[];
  searchText: string;
  filteredAris: Ari[];
  requiredAriType: AriTypeName | null;
}

@Component({
  selector: 'app-ari-command-builder',
  templateUrl: './ari-command-builder.html',
  styleUrls: ['./ari-command-builder.css'],
  imports: [
    NgTemplateOutlet,
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

    // Debounced backend validation for text/CBOR modes
    this.setupValidationPipeline(this.textInput$, 'text');
    this.setupValidationPipeline(this.cborInput$, 'cbor');
    this.onModeChange();
  }

  private setupValidationPipeline(input$: Subject<string>, mode: 'text' | 'cbor'): void {
    const requiredMsg = mode === 'text' ? 'ARI text is required' : 'CBOR hex is required';
    input$.pipe(
      debounceTime(400),
      distinctUntilChanged(),
      switchMap((value: string) => {
        if (!value.trim()) {
          return of({valid: false, error: requiredMsg});
        }
        return this.api.apiValidateAri(value.trim(), mode);
      }),
      tap((result) => {
        if (result.valid) {
          this.validationStatus = 'valid';
          this.validationMessage = '';
          this.validationErrors = [];
        } else {
          this.validationStatus = 'invalid';
          this.validationMessage = result.error || 'Invalid input';
          this.validationErrors = [this.validationMessage];
        }
      })
    ).subscribe();
  }

  protected onTypeFilterChange(change: MatSelectChange | string | null): void {
    this.selectedTypeFilter = (typeof change === 'string' ? change : change?.value) ?? 'ALL';

    this.applyMainFilter();
  }

  protected filterAris(value: string | Ari | null): void {
    this.ariSearchText = typeof value === 'string' ? value : this.displayAri(value);
    this.applyMainFilter();
  }

  protected onModeChange(): void {
    // Reset validation state when switching modes
    this.validationStatus = this.ariMode === 'cbor' &&
      this.initialCborCommands.length > 0 &&
      this.manualCborHex === this.initialCborCommands.join(',') ? 'valid' : 'none';
    this.validationMessage = '';
    this.validationErrors = [];
  }

  private applyMainFilter(): void {
    const search = this.ariSearchText?.toLowerCase() ?? '';

    this.filteredAris = this.aris.filter(ari => {
      if (this.selectedTypeFilter !== 'ALL' && ari.type_name !== this.selectedTypeFilter) {
        return false;
      }
      if (search && !ari.display.toLowerCase().includes(search)) {
        return false;
      }
      return true;
    });
  }

  protected buildParamState(ari: Ari): AriParamState[] {
    return (ari.param_names ?? []).map((paramName, index) => {
      const type = ari.param_types?.[index] ?? '';
      const kind = this.getParamKind(type);

      const param: AriParamState = {
        index,
        name: paramName,
        type,
        kind,
        wrapInAc: kind === 'ari-list' && !type.includes('TYPEDEF'),

        textValue: '',

        selectedAris: [],
        searchText: '',
        filteredAris: [],
        requiredAriType: this.getTypeFilterFromParamType(type),
      };
      if (param.kind === 'ari-list') {
        this.filterParamAris(param);
      }
      return param;
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
    this.ariSearchText = ari.display;
    this.updateAriText();
  }

  protected onParamAriSelectedPrim(paramTarget: number | AriParamState, ari: string): void {
    if (!ari.trim()) {
      return;
    }

    const param = this.resolveParam(paramTarget);
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
    this.filterParamAris(param);

    this.updateAriText();
  }

  protected onParamAriSelected(paramTarget: number | AriParamState, ari: Ari): void {
    const param = this.resolveParam(paramTarget);

    const alreadySelected = param.selectedAris.some(
      selected => selected.obj_metadata_id === ari.obj_metadata_id
    );

    if (!alreadySelected) {
      param.selectedAris = [...param.selectedAris, {
        ...ari,
        parameters: this.buildParamState(ari),
      }];
    }

    param.searchText = '';
    this.filterParamAris(param);

    this.updateAriText();
  }

  protected removeParamAri(paramTarget: number | AriParamState, ari: Ari): void {
    const param = this.resolveParam(paramTarget);

    param.selectedAris = param.selectedAris.filter(
      selected => selected.obj_metadata_id !== ari.obj_metadata_id
    );

    this.updateAriText();
  }

  private resolveParam(paramTarget: number | AriParamState): AriParamState {
    return typeof paramTarget === 'number' ? this.ariParams[paramTarget] : paramTarget;
  }

  protected updateAriText(): void {
    const rawAriText = this.buildRawAriText();

    if (!rawAriText) {
      this.ariText = '';
      this.validationErrors = [];
      return;
    }

    this.ariText = encodeURI(this.wrapExecutionSetIfNeeded(rawAriText));
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

    this.validateBuilderTextParams();
    this.validateBuilderAriParams();
  }

  private validateBuilderTextParams(): void {
    for (const param of this.getAllParams(this.ariParams)) {
      if (param.kind !== 'text') continue;
      if (!param.textValue?.trim()) {
        this.validationErrors.push(
          `Parameter "${param.name}" (${param.type}) is required`
        );
      }
    }
  }

  private validateBuilderAriParams(): void {
    for (const param of this.getAllParams(this.ariParams)) {
      if (param.kind !== 'ari-list') continue;
      if (!param.wrapInAc && param.selectedAris.length > 1) {
        this.validationErrors.push(
          `Parameter "${param.name}" has multiple values; enable ARI Collection (AC) or select a single value`
        );
      }
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
    this.handleAriInput(event, (v) => { this.manualAriText = v; }, this.textInput$);
  }

  protected onCborHexInput(event: Event): void {
    this.handleAriInput(event, (v) => { this.manualCborHex = v; }, this.cborInput$);
  }

  private handleAriInput(event: Event, setter: (v: string) => void, subject$: Subject<string>): void {
    const value = (event.target as HTMLInputElement).value;
    setter(value);
    this.validationStatus = 'checking';
    this.validationMessage = '';
    this.validationErrors = [];
    subject$.next(value);
  }

  private validateTextMode(): void {
    this.validateTextOrCborMode('text', this.manualAriText?.trim() ?? '');
  }

  private validateCborMode(): void {
    this.validateTextOrCborMode('cbor', this.manualCborHex?.trim() ?? '');
  }

  private validateTextOrCborMode(label: 'text' | 'cbor', value: string): void {
    if (!value) {
      const msg = label === 'text' ? 'ARI text is required' : 'CBOR hex is required';
      this.validationErrors.push(msg);
      this.validationStatus = 'invalid';
      return;
    }
    if (this.validationStatus === 'invalid') {
      this.validationErrors.push(this.validationMessage || `${label === 'text' ? 'ARI' : 'CBOR'} failed backend validation`);
      return;
    }
    if (this.validationStatus === 'checking') {
      this.validationErrors.push(`${label === 'text' ? 'ARI' : 'CBOR'} validation is in progress`);
      return;
    }
    if (this.validationStatus === 'none') {
      this.validationErrors.push(`${label === 'text' ? 'ARI' : 'CBOR'} has not been validated yet`);
      this.validationStatus = 'invalid';
    }
  }

  private getAllParams(params: AriParamState[]): AriParamState[] {
    return params.flatMap(param => [
      param,
      ...param.selectedAris.flatMap(ari => this.getAllParams(ari.parameters ?? [])),
    ]);
  }

  private buildRawAriText(): string {
    if (!this.selectedAri) {
      return '';
    }

    return this.buildParameterizedAriText(this.selectedAri, this.ariParams);
  }

  private buildParameterizedAriText(ari: Ari, params: AriParamState[]): string {
    if (ari.actual || params.length === 0) {
      return ari.display;
    }

    const paramText = params
      .map((param) => this.renderParamValue(param))
      .join(',');

    return (
      `ari://${ari.namespace}` +
      `/${ari.data_model_name}` +
      `/${ari.type_name}` +
      `/${ari.name}` +
      `(${paramText})`
    );
  }

  private wrapExecutionSetIfNeeded(rawAriText: string): string {
    if (!this.executionSet) {
      return rawAriText;
    }

    const noncePart = this.correlatorNonce
      ? `n=${this.correlatorNonce};`
      : 'n=null;';

    return `ari:/EXECSET/${noncePart}(${rawAriText})`;
  }

  protected renderParamValue(param: AriParamState): string {
    if (param.kind === 'ari-list') {
      const values = param.selectedAris.map((ari) =>
        this.buildParameterizedAriText(ari, ari.parameters ?? [])
      );

      if (param.wrapInAc) {
        return `/AC/(${values.join(',')})`;
      }

      return values.join(',');
    }

    return param.textValue ?? '';
  }

  protected displayAri = (ari: Ari | string | null): string => {
    return typeof ari === 'string' ? ari : ari?.display ?? '';
  };

  protected filterParamAris(paramTarget: number | AriParamState): void {
    const param = this.resolveParam(paramTarget);
    const search = param.searchText.toLowerCase();

    param.filteredAris = this.aris.filter(ari => {
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
