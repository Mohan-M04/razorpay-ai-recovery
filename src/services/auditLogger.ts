import { AuditLogEntry, TransactionStatus } from '../types';

class AuditLogger {
  private logs: AuditLogEntry[] = [];

  public log(entry: {
    transactionId: string;
    action: string;
    actor: AuditLogEntry['actor'];
    details: string;
    stateFrom: TransactionStatus;
    stateTo: TransactionStatus;
    metadata?: Record<string, any>;
  }): AuditLogEntry {
    const record: AuditLogEntry = {
      id: `aud_${Math.random().toString(36).substring(2, 9)}`,
      timestamp: new Date().toISOString(),
      ...entry
    };
    this.logs.unshift(record);
    return record;
  }

  public getLogsForTransaction(transactionId: string): AuditLogEntry[] {
    return this.logs.filter(l => l.transactionId === transactionId);
  }

  public getAllLogs(): AuditLogEntry[] {
    return [...this.logs];
  }

  public clear(): void {
    this.logs = [];
  }

  public exportJSON(): string {
    return JSON.stringify(this.logs, null, 2);
  }
}

export const auditLogger = new AuditLogger();
