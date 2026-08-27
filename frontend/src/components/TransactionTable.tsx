import React, { useState } from 'react';
import { FailedPaymentEvent, TransactionStatus } from '../types';
import { Search, ChevronRight, CheckCircle, Clock, XCircle, AlertCircle, ShieldAlert } from 'lucide-react';

interface TransactionTableProps {
  transactions: FailedPaymentEvent[];
  onSelectTransaction: (tx: FailedPaymentEvent) => void;
}

export const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
  onSelectTransaction
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const filtered = transactions.filter(tx => {
    const matchesSearch = 
      tx.customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tx.merchantName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tx.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tx.failureCode.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'ALL' || tx.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: TransactionStatus) => {
    switch (status) {
      case 'RECOVERED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle className="w-3 h-3" />
            Recovered
          </span>
        );
      case 'IN_RECOVERY':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Clock className="w-3 h-3" />
            In Recovery
          </span>
        );
      case 'ESCALATED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <AlertCircle className="w-3 h-3" />
            Escalated
          </span>
        );
      case 'STOPPED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <ShieldAlert className="w-3 h-3" />
            Guardrail Halt
          </span>
        );
      case 'FAILED':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            <XCircle className="w-3 h-3" />
            Pending Diagnosis
          </span>
        );
    }
  };

  const getStrategyLabel = (tx: FailedPaymentEvent) => {
    if (!tx.recoveryPlan) return <span className="text-slate-500 italic text-xs">—</span>;

    const map: Record<string, { label: string; color: string }> = {
      SMART_RETRY_BACKOFF: { label: 'Automated Retry', color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20' },
      PAYDAY_NUDGE_PAYMENT_LINK: { label: 'Payday Nudge + Link', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
      INSTANT_MANDATE_RENEWAL: { label: 'UPI Autopay Renewal', color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
      WHATSAPP_ASSISTED_CHECKOUT: { label: 'WhatsApp Recovery', color: 'text-green-400 bg-green-500/10 border-green-500/20' },
      GRACEFUL_DEAL_EXPIRY_ALERT: { label: 'Card Expiry Alert', color: 'text-orange-400 bg-orange-500/10 border-orange-500/20' },
      ESCALATE_TO_HUMAN: { label: 'VIP Account Escalation', color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20' }
    };

    const item = map[tx.recoveryPlan.strategy] || { label: tx.recoveryPlan.strategy, color: 'text-slate-400 bg-slate-800' };

    return (
      <span className={`px-2 py-0.5 rounded text-[11px] font-medium border ${item.color}`}>
        {item.label}
      </span>
    );
  };

  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl overflow-hidden shadow-lg">
      {/* Table Header & Search Filter Bar */}
      <div className="p-4 border-b border-[#1E293B] flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by customer, merchant, error..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-[#080C14] border border-[#1E293B] rounded-lg text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition-all"
          />
        </div>

        {/* Status Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
          {['ALL', 'IN_RECOVERY', 'RECOVERED', 'ESCALATED', 'STOPPED', 'FAILED'].map(status => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                statusFilter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Transaction List */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-[#080C14]/70 text-slate-400 text-xs uppercase font-mono tracking-wider border-b border-[#1E293B]">
            <tr>
              <th className="py-3 px-4">Payment ID & Customer</th>
              <th className="py-3 px-4">Merchant & Category</th>
              <th className="py-3 px-4">Amount</th>
              <th className="py-3 px-4">Failure Reason</th>
              <th className="py-3 px-4">AI Recovery Strategy</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1E293B] text-slate-300">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-12 text-slate-500">
                  No transactions match your search or filter criteria.
                </td>
              </tr>
            ) : (
              filtered.map(tx => (
                <tr
                  key={tx.id}
                  onClick={() => onSelectTransaction(tx)}
                  className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                >
                  {/* Payment ID & Customer */}
                  <td className="py-3.5 px-4">
                    <div className="font-mono text-xs text-blue-400 font-semibold">{tx.id}</div>
                    <div className="font-medium text-slate-200 mt-0.5">{tx.customer.name}</div>
                    <div className="text-[11px] text-slate-500">{tx.customer.phone}</div>
                  </td>

                  {/* Merchant */}
                  <td className="py-3.5 px-4">
                    <div className="font-medium text-slate-200">{tx.merchantName}</div>
                    <span className="text-[11px] text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">
                      {tx.merchantCategory}
                    </span>
                  </td>

                  {/* Amount */}
                  <td className="py-3.5 px-4">
                    <div className="font-mono font-bold text-slate-100">
                      ₹{tx.amount.toLocaleString('en-IN')}
                    </div>
                    <span className="text-[10px] uppercase font-mono text-slate-500">
                      via {tx.paymentMethod}
                    </span>
                  </td>

                  {/* Failure Code */}
                  <td className="py-3.5 px-4 max-w-[200px]">
                    <span className="font-mono text-xs text-rose-400 bg-rose-500/10 px-1.5 py-0.5 rounded border border-rose-500/20 block truncate">
                      {tx.failureCode}
                    </span>
                    <p className="text-[11px] text-slate-400 truncate mt-1" title={tx.rawFailureMessage}>
                      {tx.rawFailureMessage}
                    </p>
                  </td>

                  {/* Strategy */}
                  <td className="py-3.5 px-4">
                    {getStrategyLabel(tx)}
                  </td>

                  {/* Status Badge */}
                  <td className="py-3.5 px-4">
                    {getStatusBadge(tx.status)}
                  </td>

                  {/* Action arrow */}
                  <td className="py-3.5 px-4 text-right">
                    <button className="p-1 rounded-lg text-slate-400 group-hover:text-blue-400 group-hover:bg-blue-500/10 transition-all">
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
