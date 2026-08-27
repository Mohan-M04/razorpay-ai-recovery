import React from 'react';
import { FailedPaymentEvent } from '../types';
import { auditLogger } from '../services/auditLogger';
import { 
  X, 
  ShieldCheck, 
  Sparkles, 
  Send, 
  ExternalLink, 
  CheckCircle, 
  AlertOctagon, 
  FileText,
  User,
  Building,
  CreditCard
} from 'lucide-react';

interface TransactionModalProps {
  transaction: FailedPaymentEvent | null;
  onClose: () => void;
  onSimulateSingleRecovery: (tx: FailedPaymentEvent) => void;
}

export const TransactionModal: React.FC<TransactionModalProps> = ({
  transaction,
  onClose,
  onSimulateSingleRecovery
}) => {
  if (!transaction) return null;

  const logs = auditLogger.getLogsForTransaction(transaction.id);
  const plan = transaction.recoveryPlan;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
        {/* Header */}
        <div className="p-5 border-b border-[#1E293B] flex items-center justify-between bg-[#080C14]/60">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400">
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-100 font-mono">{transaction.id}</h3>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  transaction.status === 'RECOVERED'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : transaction.status === 'IN_RECOVERY'
                    ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                    : 'bg-slate-800 text-slate-400'
                }`}>
                  {transaction.status}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Failed on {new Date(transaction.timestamp).toLocaleString()}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {transaction.status === 'IN_RECOVERY' && (
              <button
                onClick={() => onSimulateSingleRecovery(transaction)}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 transition-all"
              >
                <CheckCircle className="w-3.5 h-3.5" />
                Simulate Customer Payment
              </button>
            )}

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scrollable Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Metadata Cards Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Customer Info */}
            <div className="bg-[#080C14] border border-[#1E293B] rounded-xl p-3.5">
              <div className="flex items-center gap-2 text-slate-400 text-xs font-medium mb-2">
                <User className="w-3.5 h-3.5 text-blue-400" />
                Customer Profile
              </div>
              <div className="font-semibold text-slate-200 text-sm">{transaction.customer.name}</div>
              <div className="text-xs text-slate-400 font-mono mt-0.5">{transaction.customer.phone}</div>
              <div className="mt-2 flex items-center gap-2 text-[11px]">
                <span className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">
                  {transaction.customer.loyaltyTier}
                </span>
                <span className="text-slate-500">
                  {transaction.customer.pastSuccessfulTransactions} past orders
                </span>
              </div>
            </div>

            {/* Merchant Info */}
            <div className="bg-[#080C14] border border-[#1E293B] rounded-xl p-3.5">
              <div className="flex items-center gap-2 text-slate-400 text-xs font-medium mb-2">
                <Building className="w-3.5 h-3.5 text-blue-400" />
                Merchant & Order
              </div>
              <div className="font-semibold text-slate-200 text-sm">{transaction.merchantName}</div>
              <div className="text-xs text-slate-400 mt-0.5">{transaction.merchantCategory}</div>
              <div className="mt-2 text-xs font-mono font-bold text-slate-200">
                ₹{transaction.amount.toLocaleString('en-IN')}{' '}
                <span className="text-[10px] font-normal text-slate-500">({transaction.paymentMethod})</span>
              </div>
            </div>

            {/* Raw Gateway Error */}
            <div className="bg-[#080C14] border border-rose-950/40 rounded-xl p-3.5">
              <div className="flex items-center gap-2 text-rose-400 text-xs font-medium mb-2">
                <AlertOctagon className="w-3.5 h-3.5" />
                Gateway Error Code
              </div>
              <div className="font-mono text-xs text-rose-400 font-bold">{transaction.failureCode}</div>
              <p className="text-[11px] text-slate-400 mt-1 line-clamp-2" title={transaction.rawFailureMessage}>
                {transaction.rawFailureMessage}
              </p>
            </div>
          </div>

          {/* AI Diagnostic Plan Section */}
          {plan ? (
            <div className="bg-gradient-to-r from-blue-950/20 to-slate-900 border border-blue-500/30 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-blue-400" />
                  <span className="text-xs font-bold uppercase tracking-wider text-blue-400">
                    AI Diagnostic & Intervention Strategy
                  </span>
                </div>
                <span className="text-xs font-mono bg-blue-500/10 text-blue-300 border border-blue-500/20 px-2 py-0.5 rounded-full">
                  Confidence: {Math.round(plan.confidenceScore * 100)}%
                </span>
              </div>

              <div className="mt-3">
                <h4 className="text-sm font-semibold text-slate-200">{plan.strategy}</h4>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed">{plan.diagnosis}</p>
                <div className="mt-2 text-xs text-blue-300 bg-blue-950/40 p-2.5 rounded-lg border border-blue-800/40 font-mono">
                  {plan.actionSummary}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-6 text-slate-500 text-sm">
              No recovery plan formulated yet. Click "Run AI Diagnosis" on the dashboard.
            </div>
          )}

          {/* Dual Grid: WhatsApp Mockup & Guardrail Matrix */}
          {plan && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* WhatsApp Message Preview */}
              <div className="bg-[#080C14] border border-[#1E293B] rounded-xl p-4 flex flex-col">
                <div className="flex items-center justify-between text-xs text-slate-400 pb-3 border-b border-[#1E293B] mb-3">
                  <span className="flex items-center gap-1.5 font-medium text-emerald-400">
                    <Send className="w-3.5 h-3.5" />
                    Simulated WhatsApp / SMS Nudge
                  </span>
                  <span className="font-mono text-[10px] text-slate-500">Channel: {plan.channel}</span>
                </div>

                <div className="bg-slate-900/90 rounded-lg p-3.5 text-xs text-slate-200 border border-slate-800 flex-1 space-y-2">
                  <p className="font-medium text-slate-100">{plan.messageTemplate?.greeting},</p>
                  <p className="text-slate-300 leading-relaxed">{plan.messageTemplate?.body}</p>

                  {plan.messageTemplate?.paymentLinkUrl && (
                    <div className="pt-2">
                      <a
                        href={plan.messageTemplate.paymentLinkUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs transition-colors"
                      >
                        {plan.messageTemplate.ctaText}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                      <p className="text-[10px] text-slate-500 font-mono mt-1">
                        Link: {plan.messageTemplate.paymentLinkUrl}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Guardrails Matrix */}
              <div className="bg-[#080C14] border border-[#1E293B] rounded-xl p-4">
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-300 pb-3 border-b border-[#1E293B] mb-3">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  Policy Guardrails & Bounded Limits
                </div>

                <div className="space-y-2.5">
                  {plan.guardrails.map(g => (
                    <div
                      key={g.id}
                      className="flex items-start justify-between gap-3 text-xs p-2 rounded-lg bg-slate-900 border border-slate-800"
                    >
                      <div>
                        <div className="font-medium text-slate-200 flex items-center gap-1.5">
                          {g.passed ? (
                            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <AlertOctagon className="w-3.5 h-3.5 text-rose-400" />
                          )}
                          {g.ruleName}
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5">{g.details}</p>
                      </div>
                      <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${
                        g.passed ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                      }`}>
                        {g.passed ? 'PASSED' : 'HALTED'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Audit Trail Timeline */}
          <div className="bg-[#080C14] border border-[#1E293B] rounded-xl p-4">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-300 pb-3 border-b border-[#1E293B] mb-3">
              <FileText className="w-4 h-4 text-blue-400" />
              Immutable Audit Trail ({logs.length} events logged)
            </div>

            <div className="space-y-3 relative pl-4 border-l-2 border-slate-800">
              {logs.map(log => (
                <div key={log.id} className="relative group">
                  <div className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-blue-500 ring-4 ring-[#080C14]" />
                  <div className="text-xs">
                    <div className="flex items-center gap-2 text-slate-400">
                      <span className="font-mono text-[10px]">{new Date(log.timestamp).toLocaleTimeString()}</span>
                      <span className="text-slate-600">•</span>
                      <span className="font-mono font-semibold text-blue-400">{log.actor}</span>
                      <span className="text-slate-600">•</span>
                      <span className="text-[10px] bg-slate-800 px-1 rounded text-slate-300 font-mono">
                        {log.stateFrom} → {log.stateTo}
                      </span>
                    </div>
                    <div className="font-semibold text-slate-200 mt-0.5">{log.action}</div>
                    <p className="text-slate-400 text-xs mt-0.5">{log.details}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
