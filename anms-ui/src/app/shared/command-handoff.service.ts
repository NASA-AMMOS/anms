import {Injectable, signal} from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class CommandHandoffService {
  private cborCommandsSignal = signal<string[]>([]);

  cborCommands = this.cborCommandsSignal.asReadonly();

  setCborCommands(commands: string[]): void {
    this.cborCommandsSignal.set(commands);
  }

  clear(): void {
    this.cborCommandsSignal.set([]);
  }

  hasCommands(): boolean {
    return this.cborCommandsSignal().length > 0;
  }
}
