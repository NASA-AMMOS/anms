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

  beforeEach(async () => {
    Constants.USER_DETAILS = {token: 'test-token'};

    apiSpy = vi.fn().mockImplementation((type: string | undefined) => {
      if (type) {
        return of(allMockAris.filter(a => a.type_name === type));
      }
      return of(allMockAris);
    });

    await TestBed.configureTestingModule({
      imports: [AriCommandBuilder],
      providers: [{provide: ApiService, useValue: {apiQueryForARIs: apiSpy}}],
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
      c(component).filterAris('zzzznotfound');
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

  describe('type filter (server-side)', () => {
    it('defaults to "ALL" — shows every type', () => {
      expect(c(component).selectedTypeFilter).toBe('ALL');
      const types = new Set(c(component).filteredAris.map((a: Ari) => a.type_name));
      expect(types).toContain('CONST');
      expect(types).toContain('CTRL');
      expect(types).toContain('OPER');
    });

    it('calls API with type param when a type is selected', () => {
      c(component).onTypeFilterChange({value: 'CONST'});
      expect(apiSpy).toHaveBeenCalledWith('CONST');
      expect(apiSpy).toHaveBeenCalledTimes(2);
      const types = new Set(c(component).filteredAris.map((a: Ari) => a.type_name));
      expect(types.size).toBe(1);
      expect(types.has('CONST')).toBe(true);
    });

    it('resets to all when "ALL" is re-selected', () => {
      c(component).onTypeFilterChange({value: 'CONST'});
      c(component).onTypeFilterChange({value: 'ALL'});
      expect(apiSpy).toHaveBeenCalledWith(undefined);
      expect(c(component).filteredAris).toHaveLength(allMockAris.length);
    });

    it('combines server type filter with client text search', () => {
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
});
