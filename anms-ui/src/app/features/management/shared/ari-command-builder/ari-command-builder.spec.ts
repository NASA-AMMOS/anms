import {ComponentFixture, TestBed} from '@angular/core/testing';
import {of} from 'rxjs';
import {vi} from 'vitest';

import {AriCommandBuilder} from './ari-command-builder';
import {ApiService} from '../../../../shared/api.service';
import {Constants} from '../../../../shared/constants';
import {Ari} from '../../agents/model/ari.model';

function mockAris(): Ari[] {
  return [
    {
      obj_metadata_id: 1, obj_id: 1, name: 'agentId', namespace: './',
      data_model_name: 'Agent', type_name: 'CONST', data_model_id: 1,
      parm_id: null, actual: true, display: 'ari://./Agent/CONST/agentId',
      param_names: [], param_types: [],
    },
    {
      obj_metadata_id: 2, obj_id: 2, name: 'uptime', namespace: './',
      data_model_name: 'Agent', type_name: 'CTRL', data_model_id: 1,
      parm_id: null, actual: true, display: 'ari://./Agent/CTRL/uptime',
      param_names: [], param_types: [],
    },
    {
      obj_metadata_id: 3, obj_id: 3, name: 'setUptime', namespace: './',
      data_model_name: 'Agent', type_name: 'OPER', data_model_id: 1,
      parm_id: null, actual: false, display: 'ari://./Agent/OPER/setUptime',
      param_names: ['duration'], param_types: ['unsignedInt'],
    },
    {
      obj_metadata_id: 4, obj_id: 4, name: 'reportTable', namespace: './',
      data_model_name: 'Agent', type_name: 'EDD', data_model_id: 1,
      parm_id: null, actual: true, display: 'ari://./Agent/EDD/reportTable',
      param_names: [], param_types: [],
    },
    {
      obj_metadata_id: 5, obj_id: 5, name: 'restart', namespace: './',
      data_model_name: 'Device', type_name: 'OPER', data_model_id: 2,
      parm_id: null, actual: false, display: 'ari://./Device/OPER/restart',
      param_names: ['target'], param_types: ['/ARITYPE/AC'],
    },
    {
      obj_metadata_id: 6, obj_id: 6, name: 'configType', namespace: './',
      data_model_name: 'Device', type_name: 'TYPEDEF', data_model_id: 2,
      parm_id: null, actual: true, display: 'ari://./Device/TYPEDEF/configType',
      param_names: [], param_types: [],
    },
  ];
}

const allMockAris = mockAris();

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const c = (cmp: AriCommandBuilder): any => cmp;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let apiSpy: any;

describe('AriCommandBuilder', () => {
  let component: AriCommandBuilder;
  let fixture: ComponentFixture<AriCommandBuilder>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let validateAriSpy: any;

  beforeEach(async () => {
    Constants.USER_DETAILS = {token: 'test-token'};

    apiSpy = vi.fn().mockImplementation((type: string | undefined) => {
      if (type) {
        return of(allMockAris.filter(a => a.type_name === type));
      }
      return of(allMockAris);
    });

    validateAriSpy = vi.fn().mockReturnValue(of({valid: false, error: 'Mock error'}));

    await TestBed.configureTestingModule({
      imports: [AriCommandBuilder],
      providers: [{provide: ApiService, useValue: {apiQueryForARIs: apiSpy, apiValidateAri: validateAriSpy}}],
    }).compileComponents();

    fixture = TestBed.createComponent(AriCommandBuilder);
    component = fixture.componentInstance;
    fixture.detectChanges();

    // Initial load from constructor — no type param
    expect(apiSpy).toHaveBeenCalled();
    await fixture.whenStable();
    fixture.detectChanges();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('ARI loading', () => {
    it('stores all ARIs and uses them as initial filtered list', () => {
      expect(c(component).aris).toEqual(allMockAris);
      expect(c(component).filteredAris).toEqual(allMockAris);
    });
  });

  describe('filterAris (main dropdown text search)', () => {
    it('filters by substring match on display (case-insensitive)', () => {
      c(component).filterAris('const');
      expect(c(component).filteredAris).toHaveLength(1);
      expect(c(component).filteredAris[0].name).toBe('agentId');
    });

    it('returns multiple matches for partial substring', () => {
      c(component).filterAris('agent');
      const names = c(component).filteredAris.map((a: Ari) => a.name);
      expect(names).toContain('agentId');
      expect(names).toContain('uptime');
      expect(names).toContain('reportTable');
      expect(names).toContain('setUptime');
      expect(c(component).filteredAris).toHaveLength(4);
    });

    it('returns empty list for non-matching search', () => {
      c(component).filterAris('notfound');
      expect(c(component).filteredAris).toHaveLength(0);
    });

    it('returns all ARIs for empty search', () => {
      c(component).filterAris('');
      expect(c(component).filteredAris).toHaveLength(allMockAris.length);
    });

    it('handles null value gracefully', () => {
      c(component).filterAris(null);
      expect(c(component).filteredAris).toHaveLength(allMockAris.length);
    });

    it('handles Ari object value gracefully', () => {
      c(component).filterAris(allMockAris[0]);
      expect(c(component).filteredAris.length).toBeGreaterThanOrEqual(1);
    });
  });

  describe('type filter (main dropdown)', () => {
    it('defaults to "ALL" — shows every type', () => {
      expect(c(component).selectedTypeFilter).toBe('ALL');
      const types = new Set(c(component).filteredAris.map((a: Ari) => a.type_name));
      expect(types).toContain('CONST');
      expect(types).toContain('CTRL');
      expect(types).toContain('OPER');
    });

    it('filters the main dropdown while retaining the complete ARI list', () => {
      c(component).onTypeFilterChange({value: 'CONST'});
      expect(apiSpy).toHaveBeenCalledTimes(1);
      expect(c(component).aris).toEqual(allMockAris);
      const types = new Set(c(component).filteredAris.map((a: Ari) => a.type_name));
      expect(types.size).toBe(1);
      expect(types.has('CONST')).toBe(true);
    });

    it('resets to all when "ALL" is re-selected', () => {
      c(component).onTypeFilterChange({value: 'CONST'});
      c(component).onTypeFilterChange({value: 'ALL'});
      expect(apiSpy).toHaveBeenCalledTimes(1);
      expect(c(component).filteredAris).toHaveLength(allMockAris.length);
    });

    it('combines type filter with text search', () => {
      c(component).onTypeFilterChange({value: 'OPER'});
      c(component).filterAris('restart');
      expect(c(component).filteredAris).toHaveLength(1);
      expect(c(component).filteredAris[0].name).toBe('restart');
    });

    it('type filter excludes non-matching types', () => {
      c(component).onTypeFilterChange({value: 'EDD'});
      const types = new Set(c(component).filteredAris.map((a: Ari) => a.type_name));
      expect(types.has('CTRL')).toBe(false);
      expect(types.has('CONST')).toBe(false);
      expect(types.has('EDD')).toBe(true);
    });

    it('returns empty when no ARIs match the selected type', () => {
      c(component).onTypeFilterChange({value: 'IDENT'});
      expect(c(component).filteredAris).toHaveLength(0);
    });
  });

  describe('filterParamAris (param-level ARI search)', () => {
    beforeEach(() => {
      const ari = allMockAris[4]; // OPER with /ARITYPE/AC param
      c(component).onAriSelected(ari);
    });

    it('filters param ARIs by substring match on display', () => {
      const param = c(component).ariParams[0];
      param.searchText = 'const';
      c(component).filterParamAris(0);
      expect(param.filteredAris).toHaveLength(1);
      expect(param.filteredAris[0].name).toBe('agentId');
    });

    it('returns all ARIs for empty param search', () => {
      const param = c(component).ariParams[0];
      param.searchText = '';
      c(component).filterParamAris(0);
      expect(param.filteredAris).toHaveLength(allMockAris.length);
    });

    it('keeps all parameter choices when the main type filter changes before and after selection', () => {
      c(component).onTypeFilterChange({value: 'OPER'});
      c(component).onAriSelected(allMockAris[4]);
      const param = c(component).ariParams[0];
      expect(param.filteredAris).toEqual(allMockAris);

      c(component).onTypeFilterChange({value: 'EDD'});
      param.searchText = 'const';
      c(component).filterParamAris(0);
      expect(param.filteredAris).toEqual([allMockAris[0]]);

      c(component).onParamAriSelected(0, allMockAris[0]);
      expect(param.filteredAris).toEqual(allMockAris);

      c(component).onParamAriSelectedPrim(0, '/INT/1');
      expect(param.filteredAris).toEqual(allMockAris);
    });
  });

  it('adds a typed parameter on Enter, closes its dropdown, and releases focus', async () => {
    c(component).onAriSelected(allMockAris[4]);
    fixture.changeDetectorRef.markForCheck();
    fixture.detectChanges();
    await fixture.whenStable();

    const input: HTMLInputElement = fixture.nativeElement.querySelector('.param-dropdown input');
    input.focus();
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(document.activeElement).toBe(input);
    expect(input.getAttribute('aria-expanded')).toBe('true');

    input.value = allMockAris[0].display;
    input.dispatchEvent(new Event('input', {bubbles: true}));
    fixture.detectChanges();
    await fixture.whenStable();
    expect(input.value).toBe(allMockAris[0].display);

    input.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
    input.dispatchEvent(new KeyboardEvent('keyup', {key: 'Enter', bubbles: true}));
    fixture.detectChanges();
    await fixture.whenStable();

    expect(c(component).ariParams[0].selectedAris[0].display).toBe(allMockAris[0].display);
    expect(document.activeElement).not.toBe(input);
    expect(input.getAttribute('aria-expanded')).toBe('false');
    expect(c(component).ariText).toContain(`/AC/(${allMockAris[0].display})`);
    const emitted = vi.fn();
    component.commandReady.subscribe(emitted);
    c(component).send();
    expect(emitted).toHaveBeenCalledWith({mode: 'builder', value: c(component).ariText});
  });

  it('includes a typed scalar parameter in the generated and submitted command', async () => {
    c(component).onAriSelected(allMockAris[2]);
    fixture.changeDetectorRef.markForCheck();
    fixture.detectChanges();
    await fixture.whenStable();

    const input: HTMLInputElement = fixture.nativeElement.querySelector('.param-dropdown input');
    input.focus();
    input.value = '123';
    input.dispatchEvent(new Event('input', {bubbles: true}));
    fixture.detectChanges();
    await fixture.whenStable();
    input.dispatchEvent(new KeyboardEvent('keyup', {key: 'Enter', bubbles: true}));

    expect(document.activeElement).not.toBe(input);
    expect(c(component).ariText).toContain('/OPER/setUptime(123)');
    const emitted = vi.fn();
    component.commandReady.subscribe(emitted);
    c(component).send();
    expect(emitted).toHaveBeenCalledWith({mode: 'builder', value: c(component).ariText});
  });

  it('ignores empty typed ARI entries', () => {
    c(component).onAriSelected(allMockAris[4]);
    c(component).onParamAriSelectedPrim(0, '   ');
    expect(c(component).ariParams[0].selectedAris).toEqual([]);
  });

  describe('parameter AC checkbox', () => {
    it('toggles the collection wrapper around a generated parameter ARI', async () => {
      c(component).onAriSelected(allMockAris[4]);
      c(component).onParamAriSelected(0, allMockAris[2]);
      c(component).ariParams[0].selectedAris[0].parameters[0].textValue = '123';
      c(component).updateAriText();
      fixture.changeDetectorRef.markForCheck();
      fixture.detectChanges();
      await fixture.whenStable();

      const checkbox: HTMLInputElement = fixture.nativeElement.querySelector('.param-block mat-checkbox input');
      fixture.detectChanges();
      expect(checkbox.checked).toBe(true);
      expect(c(component).ariText).toContain('/AC/(ari://.//Agent/OPER/setUptime(123))');
      checkbox.click();
      fixture.detectChanges();
      await fixture.whenStable();
      expect(c(component).ariParams[0].wrapInAc).toBe(false);
      expect(c(component).ariText).toContain('/OPER/restart(ari://.//Agent/OPER/setUptime(123))');
      checkbox.click();
      fixture.detectChanges();
      await fixture.whenStable();
      expect(c(component).ariText).toContain('/AC/(ari://.//Agent/OPER/setUptime(123))');
      expect(fixture.nativeElement.querySelector('.nested-param-fields mat-checkbox')).toBeNull();
    });

    it('allows TYPEDEF values to be wrapped and generates an empty AC when checked', () => {
      c(component).onAriSelected({...allMockAris[4], param_types: ['CONST/TYPEDEF']});
      const param = c(component).ariParams[0];
      expect(param.wrapInAc).toBe(false);
      c(component).onParamAriSelected(0, allMockAris[5]);
      expect(c(component).renderParamValue(param)).toBe(allMockAris[5].display);
      param.wrapInAc = true;
      expect(c(component).renderParamValue(param)).toBe(`/AC/(${allMockAris[5].display})`);
      c(component).removeParamAri(0, param.selectedAris[0]);
      expect(c(component).renderParamValue(param)).toBe('/AC/()');
    });

    it('requires an AC for multiple values and independently wraps nested parameters', () => {
      c(component).onAriSelected(allMockAris[4]);
      c(component).onParamAriSelected(0, allMockAris[4]);
      const parent = c(component).ariParams[0];
      const nested = parent.selectedAris[0].parameters[0];
      c(component).onParamAriSelected(nested, allMockAris[0]);
      c(component).onParamAriSelected(nested, allMockAris[1]);
      nested.wrapInAc = false;
      expect(c(component).validate()).toBe(false);
      expect(c(component).validationErrors[0]).toContain('enable ARI Collection (AC)');
      nested.wrapInAc = true;
      parent.wrapInAc = false;
      c(component).updateAriText();
      expect(c(component).validate()).toBe(true);
      expect(c(component).ariText).toContain(`/OPER/restart(ari://.//Device/OPER/restart(/AC/(${allMockAris[0].display},${allMockAris[1].display})))`);
    });
  });

  describe('quoted string encoding', () => {
    it.each([
      ['"hello world"', '%22hello%20world%22'],
      ['"a,b/(c)!*"', '%22a%2Cb%2F%28c%29%21%2A%22'],
      ['"hi\\"oh"', '%22hi%5C%22oh%22'],
      ['"café"', '%22caf%C3%A9%22'],
      ['/TEXTSTR/%22already%20encoded%22', '/TEXTSTR/%22already%20encoded%22'],
      ['/TEXTSTR/"hello world"', '/TEXTSTR/%22hello%20world%22'],
    ])('encodes %s in generated and submitted commands', (input, encoded) => {
      c(component).onAriSelected({...allMockAris[2], param_types: ['/ARITYPE/TEXTSTR']});
      c(component).ariParams[0].textValue = input;
      c(component).updateAriText();
      expect(c(component).ariText).toContain(`/OPER/setUptime(${encoded})`);
      expect(c(component).ariParams[0].textValue).toBe(input);

      const emitted = vi.fn();
      component.commandReady.subscribe(emitted);
      c(component).send();
      expect(emitted).toHaveBeenCalledWith({mode: 'builder', value: c(component).ariText});
    });

    it('encodes quoted literals and nested parameter strings without encoding ARI structure', () => {
      c(component).onAriSelected(allMockAris[4]);
      c(component).onParamAriSelectedPrim(0, '"a,b"');
      c(component).onParamAriSelected(0, allMockAris[2]);
      c(component).ariParams[0].selectedAris[1].parameters[0].textValue = '"hello world"';
      c(component).updateAriText();
      expect(c(component).ariText).toContain('/AC/(%22a%2Cb%22,ari://.//Agent/OPER/setUptime(%22hello%20world%22))');
      const command = c(component).ariText;
      c(component).updateAriText();
      expect(c(component).ariText).toBe(command);
    });
  });

  describe('nested parameters', () => {
    it('renders nested inputs and includes their values in the submitted command', async () => {
      c(component).onAriSelected(allMockAris[4]);
      c(component).onParamAriSelected(0, allMockAris[2]);
      fixture.changeDetectorRef.markForCheck();
      fixture.detectChanges();
      await fixture.whenStable();

      expect(c(component).validate()).toBe(false);
      expect(c(component).validationErrors[0]).toContain('duration');
      const input: HTMLInputElement = fixture.nativeElement.querySelector('.nested-param-fields input');
      expect(input).not.toBeNull();
      input.value = '123';
      input.dispatchEvent(new Event('input', {bubbles: true}));
      fixture.detectChanges();
      await fixture.whenStable();

      expect(c(component).ariText).toContain('/AC/(ari://.//Agent/OPER/setUptime(123))');
      const emitted = vi.fn();
      component.commandReady.subscribe(emitted);
      c(component).send();
      expect(emitted).toHaveBeenCalledWith({mode: 'builder', value: c(component).ariText});
    });

    it('keeps nested values independent for separate selections', () => {
      c(component).onAriSelected(allMockAris[4]);
      c(component).onParamAriSelected(0, allMockAris[2]);
      c(component).onParamAriSelected(0, {
        ...allMockAris[2], obj_metadata_id: 101, name: 'otherUptime',
      });
      const selections = c(component).ariParams[0].selectedAris;
      selections[0].parameters[0].textValue = '123';
      expect(selections[1].parameters[0].textValue).toBe('');
      selections[1].parameters[0].textValue = '456';
      c(component).updateAriText();

      expect(c(component).ariText).toContain('/OPER/setUptime(123)');
      expect(c(component).ariText).toContain('/OPER/otherUptime(456)');
      expect(allMockAris[2]).not.toHaveProperty('parameters');
    });

    it('validates ARI type requirements inside nested parameters', () => {
      c(component).onAriSelected(allMockAris[4]);
      c(component).onParamAriSelected(0, {
        ...allMockAris[4], param_types: ['CONST/AC'],
      });
      const nestedParam = c(component).ariParams[0].selectedAris[0].parameters[0];
      expect(nestedParam.filteredAris).toEqual([allMockAris[0]]);
      c(component).onParamAriSelected(nestedParam, allMockAris[1]);
      expect(c(component).validate()).toBe(false);
      expect(c(component).validationErrors[0]).toContain('expects CONST');

      c(component).removeParamAri(0, c(component).ariParams[0].selectedAris[0]);
      expect(c(component).validate()).toBe(true);
    });

    it('supports deeper nesting, nested search, and removal', async () => {
      c(component).onAriSelected(allMockAris[4]);
      c(component).onParamAriSelected(0, allMockAris[4]);
      const nestedParam = c(component).ariParams[0].selectedAris[0].parameters[0];
      expect(nestedParam.filteredAris).toEqual(allMockAris);
      nestedParam.searchText = 'setUptime';
      c(component).filterParamAris(nestedParam);
      expect(nestedParam.filteredAris).toEqual([allMockAris[2]]);
      c(component).onParamAriSelected(nestedParam, allMockAris[2]);
      const nestedSelection = nestedParam.selectedAris[0];
      nestedSelection.parameters[0].textValue = '789';
      c(component).updateAriText();
      fixture.changeDetectorRef.markForCheck();
      fixture.detectChanges();
      await fixture.whenStable();

      expect(fixture.nativeElement.querySelector('.nested-param-fields .nested-param-fields input')).not.toBeNull();
      expect(c(component).ariText).toContain('/OPER/restart(/AC/(ari://.//Agent/OPER/setUptime(789)))');
      expect(c(component).validate()).toBe(true);

      nestedSelection.parameters[0].textValue = '';
      expect(c(component).validate()).toBe(false);
      c(component).removeParamAri(nestedParam, nestedSelection);
      expect(c(component).ariText).not.toContain('setUptime');
      expect(c(component).validate()).toBe(true);
    });
  });

  describe('getParamKind', () => {
    it('returns "ari-list" for /ARITYPE/AC', () => {
      expect(c(component).getParamKind('/ARITYPE/AC')).toBe('ari-list');
    });

    it('returns "ari-list" for /ARITYPE/EXECSET', () => {
      expect(c(component).getParamKind('/ARITYPE/EXECSET')).toBe('ari-list');
    });

    it('returns "ari-list" for types containing TYPEDEF', () => {
      expect(c(component).getParamKind('CONST/TYPEDEF')).toBe('ari-list');
    });

    it('returns "text" for plain types', () => {
      expect(c(component).getParamKind('unsignedInt')).toBe('text');
      expect(c(component).getParamKind('octetStr')).toBe('text');
    });
  });

  describe('onAriSelected', () => {
    it('builds param states for the selected ARI', () => {
      const ari = allMockAris[2]; // setUptime with one param
      c(component).onAriSelected(ari);
      expect(c(component).ariParams).toHaveLength(1);
      expect(c(component).ariParams[0].name).toBe('duration');
      expect(c(component).ariParams[0].kind).toBe('text');
    });

    it('sets ariSearchText to the selected ARI display', () => {
      const ari = allMockAris[0];
      c(component).onAriSelected(ari);
      expect(c(component).ariSearchText).toBe(ari.display);
    });
  });

  describe('buildRawAriText', () => {
    it('returns ARI display for actual ARIs with no params', () => {
      const ari = allMockAris[0];
      c(component).onAriSelected(ari);
      expect(c(component).ariText).toBe(ari.display);
    });
  });

  describe('executionSet wrapping', () => {
    it('wraps ARI in EXECSET when executionSet is true', () => {
      c(component).onAriSelected(allMockAris[0]);
      c(component).executionSet = true;
      c(component).updateAriText();
      expect(c(component).ariText).toMatch(/^ari:\/EXECSET\//);
    });

    it('includes correlator nonce in EXECSET when set', () => {
      c(component).onAriSelected(allMockAris[0]);
      c(component).executionSet = true;
      c(component).correlatorNonce = 'abc123';
      c(component).updateAriText();
      expect(c(component).ariText).toContain('n=abc123;');
    });
  });

  describe('param auto-restriction by type', () => {
    it('extracts requiredAriType from param type like CONST/AC', () => {
      const ariWithConstParam: Ari = {
        obj_metadata_id: 99, obj_id: 99, name: 'setTarget', namespace: './',
        data_model_name: 'Test', type_name: 'OPER', data_model_id: 1,
        parm_id: null, actual: false, display: 'ari://./Test/OPER/setTarget',
        param_names: ['constTarget'], param_types: ['CONST/AC'],
      };
      c(component).onAriSelected(ariWithConstParam);
      const param = c(component).ariParams[0];
      expect(param.requiredAriType).toBe('CONST');
      expect(param.kind).toBe('ari-list');
    });

    it('extracts requiredAriType from CTRL/AC', () => {
      const ariWithCtrlParam: Ari = {
        obj_metadata_id: 100, obj_id: 100, name: 'setCtrl', namespace: './',
        data_model_name: 'Test', type_name: 'OPER', data_model_id: 1,
        parm_id: null, actual: false, display: 'ari://./Test/OPER/setCtrl',
        param_names: ['ctrlTarget'], param_types: ['CTRL/AC'],
      };
      c(component).onAriSelected(ariWithCtrlParam);
      const param = c(component).ariParams[0];
      expect(param.requiredAriType).toBe('CTRL');
    });

    it('does not restrict for bare /ARITYPE/AC (any type allowed)', () => {
      const ariBare = allMockAris[4]; // has /ARITYPE/AC
      c(component).onAriSelected(ariBare);
      expect(c(component).ariParams[0].requiredAriType).toBeNull();
    });

    it('restricts param filteredAris to the required type on select', () => {
      const ariWithCtrlParam: Ari = {
        obj_metadata_id: 101, obj_id: 101, name: 'setCtrl', namespace: './',
        data_model_name: 'Test', type_name: 'OPER', data_model_id: 1,
        parm_id: null, actual: false, display: 'ari://./Test/OPER/setCtrl',
        param_names: ['ctrlTarget'], param_types: ['CTRL/AC'],
      };
      c(component).onAriSelected(ariWithCtrlParam);
      const param = c(component).ariParams[0];
      for (const a of param.filteredAris) {
        expect(a.type_name).toBe('CTRL');
      }
    });

    it('combines type restriction with text search in param filter', () => {
      const ariWithConstParam: Ari = {
        obj_metadata_id: 102, obj_id: 102, name: 'setConst', namespace: './',
        data_model_name: 'Test', type_name: 'OPER', data_model_id: 1,
        parm_id: null, actual: false, display: 'ari://./Test/OPER/setConst',
        param_names: ['constTarget'], param_types: ['CONST/AC'],
      };
      c(component).onAriSelected(ariWithConstParam);
      const param = c(component).ariParams[0];
      param.searchText = 'agent';
      c(component).filterParamAris(0);
      expect(param.filteredAris).toHaveLength(1);
      expect(param.filteredAris[0].type_name).toBe('CONST');
    });
  });

  describe('validation', () => {
    it('passes when no selected ARI', () => {
      expect(c(component).validate()).toBe(true);
      expect(c(component).validationErrors).toHaveLength(0);
    });

    it('passes when all param ARI types match', () => {
      const ariWithConstParam: Ari = {
        obj_metadata_id: 110, obj_id: 110, name: 'setConst', namespace: './',
        data_model_name: 'Test', type_name: 'OPER', data_model_id: 1,
        parm_id: null, actual: false, display: 'ari://./Test/OPER/setConst',
        param_names: ['constTarget'], param_types: ['CONST/AC'],
      };
      c(component).onAriSelected(ariWithConstParam);
      c(component).onParamAriSelected(0, allMockAris[0]); // agentId is CONST
      expect(c(component).validate()).toBe(true);
    });

    it('fails when param ARI type does not match', () => {
      const ariWithConstParam: Ari = {
        obj_metadata_id: 111, obj_id: 111, name: 'setConst', namespace: './',
        data_model_name: 'Test', type_name: 'OPER', data_model_id: 1,
        parm_id: null, actual: false, display: 'ari://./Test/OPER/setConst',
        param_names: ['constTarget'], param_types: ['CONST/AC'],
      };
      c(component).onAriSelected(ariWithConstParam);
      c(component).onParamAriSelected(0, allMockAris[1]); // uptime is CTRL (wrong)
      expect(c(component).validate()).toBe(false);
      expect(c(component).validationErrors.length).toBeGreaterThan(0);
      expect(c(component).validationErrors[0]).toContain('CONST');
      expect(c(component).validationErrors[0]).toContain('CTRL');
    });

    it('passes when param has no type restriction (/ARITYPE/AC)', () => {
      const ariBare = allMockAris[4]; // has /ARITYPE/AC — no type restriction
      c(component).onAriSelected(ariBare);
      c(component).onParamAriSelected(0, allMockAris[1]);
      expect(c(component).validate()).toBe(true);
    });

    it('passes for text params regardless of value', () => {
      const ari = allMockAris[2]; // setUptime with unsignedInt param
      c(component).onAriSelected(ari);
      c(component).ariParams[0].textValue = '123';
      expect(c(component).validate()).toBe(true);
    });
  });

  describe('send() respects validation', () => {
    it('does not emit when validation fails', () => {
      const ariWithConstParam: Ari = {
        obj_metadata_id: 120, obj_id: 120, name: 'setConst', namespace: './',
        data_model_name: 'Test', type_name: 'OPER', data_model_id: 1,
        parm_id: null, actual: false, display: 'ari://./Test/OPER/setConst',
        param_names: ['constTarget'], param_types: ['CONST/AC'],
      };
      c(component).onAriSelected(ariWithConstParam);
      c(component).onParamAriSelected(0, allMockAris[1]); // wrong type

      const emitted: any[] = [];
      component.commandReady.subscribe(e => emitted.push(e));
      c(component).send();
      expect(emitted).toHaveLength(0);
    });

    it('emits when validation passes', () => {
      c(component).onAriSelected(allMockAris[0]);

      const emitted: any[] = [];
      component.commandReady.subscribe(e => emitted.push(e));
      c(component).send();
      expect(emitted).toHaveLength(1);
      expect(emitted[0].mode).toBe('builder');
    });
  });

  describe('builder mode: required text params', () => {
    it('fails when text param is empty', () => {
      const ari = allMockAris[2]; // setUptime with unsignedInt param
      c(component).onAriSelected(ari);
      c(component).ariParams[0].textValue = '';

      expect(c(component).validate()).toBe(false);
      expect(c(component).validationErrors[0]).toContain('duration');
    });

    it('fails when text param is only whitespace', () => {
      const ari = allMockAris[2];
      c(component).onAriSelected(ari);
      c(component).ariParams[0].textValue = '   ';

      expect(c(component).validate()).toBe(false);
    });

    it('passes when text param has a value', () => {
      const ari = allMockAris[2];
      c(component).onAriSelected(ari);
      c(component).ariParams[0].textValue = '42';

      expect(c(component).validate()).toBe(true);
    });

    it('emits when builder validation passes', () => {
      c(component).onAriSelected(allMockAris[0]);

      const emitted: any[] = [];
      component.commandReady.subscribe(e => emitted.push(e));
      c(component).send();
      expect(emitted).toHaveLength(1);
    });

    it('does not emit when builder validation fails', () => {
      const ari = allMockAris[2];
      c(component).onAriSelected(ari);
      c(component).ariParams[0].textValue = '';

      const emitted: any[] = [];
      component.commandReady.subscribe(e => emitted.push(e));
      c(component).send();
      expect(emitted).toHaveLength(0);
    });
  });

  describe('text mode: ARI syntax validation', () => {
    beforeEach(() => {
      (component as any).ariMode = 'text';
    });

    it('fails when text is empty', () => {
      (component as any).manualAriText = '';
      expect(c(component).validate()).toBe(false);
      expect(c(component).validationErrors[0]).toBe('ARI text is required');
    });

    it('passes when backend validation marks ARI as valid', () => {
      (component as any).manualAriText = 'ari://./Agent/CTRL/uptime';
      // Simulate backend validation success
      c(component).validationStatus = 'valid';
      c(component).validationErrors = [];
      expect(c(component).validate()).toBe(true);
    });

    it('fails when backend validation marks ARI as invalid', () => {
      (component as any).manualAriText = 'ari://./Agent/CTRL/uptime';
      c(component).validationStatus = 'invalid';
      c(component).validationMessage = 'ParseError: invalid syntax';
      expect(c(component).validate()).toBe(false);
      expect(c(component).validationErrors[0]).toBe('ParseError: invalid syntax');
    });

    it('fails when ARI has not been validated yet', () => {
      (component as any).manualAriText = 'ari://./Agent/CTRL/uptime';
      c(component).validationStatus = 'none';
      c(component).validationErrors = [];
      expect(c(component).validate()).toBe(false);
      expect(c(component).validationErrors[0]).toBe('ARI has not been validated yet');
    });

    it('emits when text validation passes', () => {
      (component as any).manualAriText = 'ari://./Agent/CTRL/uptime';
      c(component).validationStatus = 'valid';
      c(component).validationErrors = [];

      const emitted: any[] = [];
      component.commandReady.subscribe(e => emitted.push(e));
      c(component).send();
      expect(emitted).toHaveLength(1);
      expect(emitted[0].mode).toBe('text');
    });

    it('does not emit when text validation fails', () => {
      (component as any).manualAriText = 'not-an-ari';
      c(component).validationStatus = 'invalid';
      c(component).validationMessage = 'ParseError: invalid syntax';

      const emitted: any[] = [];
      component.commandReady.subscribe(e => emitted.push(e));
      c(component).send();
      expect(emitted).toHaveLength(0);
    });
  });

  describe('cbor mode: hex validation', () => {
    beforeEach(() => {
      (component as any).ariMode = 'cbor';
    });

    it('fails when hex is empty', () => {
      (component as any).manualCborHex = '';
      expect(c(component).validate()).toBe(false);
      expect(c(component).validationErrors[0]).toBe('CBOR hex is required');
    });

    it('passes when backend validation marks CBOR as valid', () => {
      (component as any).manualCborHex = 'ABC123';
      c(component).validationStatus = 'valid';
      c(component).validationErrors = [];
      expect(c(component).validate()).toBe(true);
    });

    it('fails when backend validation marks CBOR as invalid', () => {
      (component as any).manualCborHex = 'ABC123';
      c(component).validationStatus = 'invalid';
      c(component).validationMessage = 'ParseError: invalid CBOR';
      expect(c(component).validate()).toBe(false);
    });

    it('fails when CBOR has not been validated yet', () => {
      (component as any).manualCborHex = 'ABC123';
      c(component).validationStatus = 'none';
      c(component).validationErrors = [];
      expect(c(component).validate()).toBe(false);
      expect(c(component).validationErrors[0]).toBe('CBOR has not been validated yet');
    });

    it('emits when cbor validation passes', () => {
      (component as any).manualCborHex = 'ABC123';
      c(component).validationStatus = 'valid';
      c(component).validationErrors = [];

      const emitted: any[] = [];
      component.commandReady.subscribe(e => emitted.push(e));
      c(component).send();
      expect(emitted).toHaveLength(1);
      expect(emitted[0].mode).toBe('cbor');
    });

    it('does not emit when cbor validation fails', () => {
      (component as any).manualCborHex = 'GGZZ';
      c(component).validationStatus = 'invalid';
      c(component).validationErrors = ['ParseError: invalid CBOR'];

      const emitted: any[] = [];
      component.commandReady.subscribe(e => emitted.push(e));
      c(component).send();
      expect(emitted).toHaveLength(0);
    });
  });

  describe('builder-generated CBOR handoff', () => {
    it.each([['ABCD'], ['ABCD', '1234']])('allows unchanged handed-off CBOR to be submitted', (...commands) => {
      const handoffFixture = TestBed.createComponent(AriCommandBuilder);
      handoffFixture.componentRef.setInput('initialMode', 'cbor');
      handoffFixture.componentRef.setInput('initialCborCommands', commands);
      handoffFixture.detectChanges();
      const handedOff = handoffFixture.componentInstance;
      const emitted = vi.fn();
      handedOff.commandReady.subscribe(emitted);
      c(handedOff).send();

      expect(c(handedOff).validationStatus).toBe('valid');
      expect(c(handedOff).validationErrors).toEqual([]);
      expect(emitted).toHaveBeenCalledWith({mode: 'cbor', value: `0x${commands.join(',')}`});
      expect(validateAriSpy).not.toHaveBeenCalled();
    });

    it('preserves validation of unchanged handed-off CBOR when switching modes', () => {
      c(component).initialCborCommands = ['ABCD'];
      c(component).manualCborHex = 'ABCD';
      c(component).ariMode = 'text';
      c(component).onModeChange();
      expect(c(component).validationStatus).toBe('none');
      c(component).ariMode = 'cbor';
      c(component).onModeChange();
      expect(c(component).validationStatus).toBe('valid');

      c(component).manualCborHex = '1234';
      c(component).onModeChange();
      expect(c(component).validationStatus).toBe('none');
    });

    it('requires backend validation after handed-off CBOR is edited', async () => {
      c(component).initialCborCommands = ['ABCD'];
      c(component).manualCborHex = 'ABCD';
      c(component).ariMode = 'cbor';
      c(component).onModeChange();
      validateAriSpy.mockReturnValue(of({valid: true}));
      const emitted = vi.fn();
      component.commandReady.subscribe(emitted);
      c(component).onCborHexInput({target: {value: '1234'}} as unknown as Event);
      c(component).send();
      expect(emitted).not.toHaveBeenCalled();
      expect(c(component).validationErrors).toEqual(['CBOR validation is in progress']);

      await vi.waitFor(() => expect(validateAriSpy).toHaveBeenCalledWith('1234', 'cbor'));
      c(component).send();
      expect(emitted).toHaveBeenCalledWith({mode: 'cbor', value: '0x1234'});
    });
  });

  describe('mode change resets validation', () => {
    it('clears validation state when switching from text to builder', () => {
      (component as any).ariMode = 'text';
      c(component).validationStatus = 'invalid';
      c(component).validationErrors = ['Some error'];
      c(component).validationMessage = 'Some error';

      c(component).onModeChange();

      expect(c(component).validationStatus).toBe('none');
      expect(c(component).validationErrors).toEqual([]);
      expect(c(component).validationMessage).toBe('');
    });
  });

  describe('backend validation integration', () => {
    it('onTextAriInput resets state and sets checking status', () => {
      (component as any).ariMode = 'text';
      const mockEvent = {target: {value: 'ari://./Agent/CTRL/uptime'}} as unknown as Event;
      c(component).onTextAriInput(mockEvent);
      expect(c(component).manualAriText).toBe('ari://./Agent/CTRL/uptime');
      expect(c(component).validationStatus).toBe('checking');
      expect(validateAriSpy).not.toHaveBeenCalled(); // debounced
    });

    it('onCborHexInput resets state and sets checking status', () => {
      (component as any).ariMode = 'cbor';
      const mockEvent = {target: {value: 'ABC123'}} as unknown as Event;
      c(component).onCborHexInput(mockEvent);
      expect(c(component).manualCborHex).toBe('ABC123');
      expect(c(component).validationStatus).toBe('checking');
    });
  });
});
