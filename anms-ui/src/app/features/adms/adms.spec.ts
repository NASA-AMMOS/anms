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
import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { NotificationService } from '../../shared/notification.service';
import { Adms } from './adms';

describe('Adms', () => {
  let component: Adms;
  let fixture: ComponentFixture<Adms>;
  let httpMock: HttpTestingController;
  const notificationService = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Adms, HttpClientTestingModule],
      providers: [
        { provide: NotificationService, useValue: notificationService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Adms);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    // Triggers ngAfterViewInit -> AdmService.getAdms() (hasAdms() is false).
    fixture.detectChanges();
    // Flush the ADM list fetch.
    httpMock.expectOne('/api/core/adms').flush([]);
    await fixture.whenStable();
  });

  afterEach(() => {
    // Fails the test if the component made any request we did not account for.
    httpMock.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
