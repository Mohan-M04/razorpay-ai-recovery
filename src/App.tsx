import React, { useState, useEffect, useMemo } from 'react';
import { FailedPaymentEvent, BatchMetrics } from './types';
import { generateSyntheticFailedBatch } from './data/syntheticGenerator';
import { recoveryAgent } from './engine/recoveryAgent';
import { auditLogger } from './services/auditLogger';
import { MetricCards } from './components/MetricCards';
import { BatchRunner } from './components/BatchRunner';
import { TransactionTable } from './components/TransactionTable';
import { TransactionModal } from './components/TransactionModal';
import { ShieldCheck, Download, Zap, Radio } from 'lucide-react';

export const App: React.FC = () => {
  const [transactions, setTransactions] = useState<FailedPaymentEvent[]>([]);
  const [selectedTx, setSelectedTx] = useState<FailedPaymentEvent | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [progressPercent, setProgressPercent] = useState<number>(0);

  // Initialize initial 60-transaction synthetic batch on mount
  useEffect(() => {
    handleGenerateBatch();
  }, []);

  const handleGenerateBatch = () => {
    auditLogger.clear();
    const batch = generateSyntheticFailedBatch(60);

    // Initial audit log for ingestion
    batch.forEach(tx => {
      auditLogger.log({
        transactionId: tx.id,
        action: 'WEBHOOK_FAILED_PAYMENT_INGESTED',
        actor: 'SYSTEM_EVENT',
        details: `Ingested Razorpay failed payment webhook: ${tx.failureCode} for ₹${tx.amount.toLocaleString('en-IN')}`,
        stateFrom: 'FAILED',
        stateTo: 'FAILED',
        metadata: {
          merchant: tx.merchantName,
          customer: tx.customer.name,
          paymentMethod: tx.paymentMethod
        }
      });
    });

    setTransactions(batch);
    setSelectedTx(null);
    setProgressPercent(0);
  };

  // Run autonomous AI diagnosis across the batch
  const handleRunDiagnosis = async () => {
    setIsProcessing(true);
    setProgressPercent(0);

    const updatedList = [...transactions];
    const total = updatedList.length;

    for (let i = 0; i < total; i++) {
      const tx = updatedList[i];
      const plan = await recoveryAgent.formulateRecoveryPlan(tx);

      let newStatus = tx.status;
      if (plan.strategy === 'ESCALATE_TO_HUMAN') {
        newStatus = 'ESCALATED';
      } else {
        newStatus = 'IN_RECOVERY';
      }

      updatedList[i] = {
        ...tx,
        status: newStatus,
        recoveryPlan: plan
      };

      setProgressPercent(((i + 1) / total) * 100);
      // Small artificial delay for visual feedback
      if (i % 5 === 0) {
        await new Promise(r => setTimeout(r, 40));
      }
    }

    setTransactions(updatedList);
    setIsProcessing(false);
  };

  // Simulate customer payment follow-through across high-probability opportunities
  const handleSimulateRecoveries = async () => {
    setIsProcessing(true);
    const updatedList = [...transactions];

    for (let i = 0; i < updatedList.length; i++) {
      const tx = updatedList[i];
      // Only recover transactions that are in recovery and not escalated
      if (tx.status === 'IN_RECOVERY') {
        // High recovery probability (approx 65% conversion)
        const willRecover = Math.random() < 0.65;
        if (willRecover) {
          updatedList[i] = recoveryAgent.executeRecoverySuccess(tx);
        } else {
          // Stopped after attempt
          updatedList[i] = {
            ...tx,
            status: 'STOPPED'
          };
          auditLogger.log({
            transactionId: tx.id,
            action: 'SEQUENCE_EXPIRED',
            actor: 'SYSTEM_EVENT',
            details: 'Recovery payment link expired without customer completion. Sequence closed gracefully.',
            stateFrom: 'IN_RECOVERY',
            stateTo: 'STOPPED'
          });
        }
      }
    }

    setTransactions(updatedList);
    setIsProcessing(false);
  };

  // Simulate single customer payment from modal
  const handleSimulateSingleRecovery = (tx: FailedPaymentEvent) => {
    const updated = recoveryAgent.executeRecoverySuccess(tx);
    setTransactions(prev => prev.map(t => t.id === updated.id ? updated : t));
    setSelectedTx(updated);
  };

  // Export audit log
  const handleExportAuditLogs = () => {
    const json = auditLogger.exportJSON();
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `razorrecover_audit_trail_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Compute live metrics
  const metrics: BatchMetrics = useMemo(() => {
    const totalTransactions = transactions.length;
    const totalAtRiskINR = transactions.reduce((sum, t) => sum + t.amount, 0);
    const recoveredTxs = transactions.filter(t => t.status === 'RECOVERED');
    const totalRecoveredINR = recoveredTxs.reduce((sum, t) => sum + t.amount, 0);
    const recoveryRatePercent = totalAtRiskINR > 0 ? (totalRecoveredINR / totalAtRiskINR) * 100 : 0;
    const interventionsActive = transactions.filter(t => t.status === 'IN_RECOVERY').length;
    const stoppedByGuardrails = transactions.filter(t => t.status === 'STOPPED').length;
    const escalatedToHuman = transactions.filter(t => t.status === 'ESCALATED').length;

    const byCategory: Record<string, { atRisk: number; recovered: number }> = {};
    const byFailureCode: Record<string, { count: number; recovered: number }> = {};

    transactions.forEach(t => {
      if (!byCategory[t.merchantCategory]) {
        byCategory[t.merchantCategory] = { atRisk: 0, recovered: 0 };
      }
      byCategory[t.merchantCategory].atRisk += t.amount;
      if (t.status === 'RECOVERED') {
        byCategory[t.merchantCategory].recovered += t.amount;
      }

      if (!byFailureCode[t.failureCode]) {
        byFailureCode[t.failureCode] = { count: 0, recovered: 0 };
      }
      byFailureCode[t.failureCode].count++;
      if (t.status === 'RECOVERED') {
        byFailureCode[t.failureCode].recovered++;
      }
    });

    return {
      totalTransactions,
      totalAtRiskINR,
      totalRecoveredINR,
      recoveryRatePercent,
      interventionsActive,
      stoppedByGuardrails,
      escalatedToHuman,
      byCategory,
      byFailureCode
    };
  }, [transactions]);

  const diagnosedCount = transactions.filter(t => t.recoveryPlan).length;
  const recoveredCount = transactions.filter(t => t.status === 'RECOVERED').length;

  return (
    <div className="min-h-screen bg-[#080C14] text-slate-100 p-4 md:p-8 flex flex-col justify-between">
      <div className="max-w-7xl mx-auto w-full space-y-6">
        {/* Navigation Bar */}
        <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-[#1E293B]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-extrabold tracking-tight text-white">RazorRecover AI</h1>
                <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[11px] font-mono font-semibold px-2 py-0.5 rounded">
                  Track 03
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Autonomous Payment Degradation & Revenue Recovery Engine • Built for Razorpay AI Buildathon
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#0F172A] border border-[#1E293B] text-xs font-mono text-emerald-400">
              <Radio className="w-3.5 h-3.5 animate-pulse text-emerald-400" />
              <span>Razorpay Test Rail: Active</span>
            </div>

            <button
              onClick={handleExportAuditLogs}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-all"
            >
              <Download className="w-3.5 h-3.5" />
              Export Audit Trail
            </button>
          </div>
        </header>

        {/* Top KPI Metrics Cards */}
        <MetricCards metrics={metrics} />

        {/* Batch Processing Controls */}
        <BatchRunner
          onGenerateBatch={handleGenerateBatch}
          onRunDiagnosis={handleRunDiagnosis}
          onSimulateRecoveries={handleSimulateRecoveries}
          isProcessing={isProcessing}
          progressPercent={progressPercent}
          totalLoaded={transactions.length}
          diagnosedCount={diagnosedCount}
          recoveredCount={recoveredCount}
        />

        {/* Main Transactions Table */}
        <TransactionTable
          transactions={transactions}
          onSelectTransaction={setSelectedTx}
        />
      </div>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto w-full pt-8 pb-4 text-center text-xs text-slate-500 border-t border-[#1E293B]/60 mt-12 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Every recovery intervention is bounded, explainable, and logged. Strictly defense-only.</span>
        </div>
        <div className="font-mono text-[11px] text-slate-400">
          Razorpay AI Buildathon 2026 Submission
        </div>
      </footer>

      {/* Drill-down Detail Modal */}
      <TransactionModal
        transaction={selectedTx}
        onClose={() => setSelectedTx(null)}
        onSimulateSingleRecovery={handleSimulateSingleRecovery}
      />
    </div>
  );
};

export default App;
