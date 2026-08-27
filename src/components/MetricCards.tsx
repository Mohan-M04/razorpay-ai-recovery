import React from 'react';
import { BatchMetrics } from '../types';
import { TrendingUp, AlertTriangle, ShieldCheck, CheckCircle2, ArrowUpRight } from 'lucide-react';

interface MetricCardsProps {
  metrics: BatchMetrics;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ metrics }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* Total Revenue At Risk */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 relative overflow-hidden group hover:border-blue-500/50 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total at Risk</span>
          <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3">
          <h3 className="text-2xl font-bold text-slate-100 font-mono">
            ₹{metrics.totalAtRiskINR.toLocaleString('en-IN')}
          </h3>
          <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
            Across <span className="text-slate-200 font-medium">{metrics.totalTransactions}</span> failed transactions
          </p>
        </div>
        <div className="absolute -right-4 -bottom-4 w-16 h-16 bg-rose-500/5 rounded-full blur-xl group-hover:bg-rose-500/10 transition-all" />
      </div>

      {/* Total Revenue Recovered */}
      <div className="bg-[#0F172A] border border-emerald-500/30 rounded-xl p-5 relative overflow-hidden group hover:border-emerald-500/60 transition-all bg-gradient-to-br from-[#0F172A] to-emerald-950/20">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">Total Recovered</span>
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3">
          <h3 className="text-2xl font-bold text-emerald-400 font-mono">
            ₹{metrics.totalRecoveredINR.toLocaleString('en-IN')}
          </h3>
          <p className="text-xs text-emerald-400/80 mt-1 flex items-center gap-1">
            <ArrowUpRight className="w-3.5 h-3.5" />
            Direct money saved for merchants
          </p>
        </div>
        <div className="absolute -right-4 -bottom-4 w-16 h-16 bg-emerald-500/10 rounded-full blur-xl group-hover:bg-emerald-500/20 transition-all" />
      </div>

      {/* Recovery Conversion Rate */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 relative overflow-hidden group hover:border-blue-500/50 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Recovery Rate</span>
          <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3">
          <h3 className="text-2xl font-bold text-blue-400 font-mono">
            {metrics.recoveryRatePercent.toFixed(1)}%
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Target benchmark: &gt;50%
          </p>
        </div>
        <div className="absolute -right-4 -bottom-4 w-16 h-16 bg-blue-500/5 rounded-full blur-xl group-hover:bg-blue-500/10 transition-all" />
      </div>

      {/* Active Interventions */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 relative overflow-hidden group hover:border-amber-500/50 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">In Recovery</span>
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3">
          <h3 className="text-2xl font-bold text-amber-400 font-mono">
            {metrics.interventionsActive}
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Active workflows in-flight
          </p>
        </div>
        <div className="absolute -right-4 -bottom-4 w-16 h-16 bg-amber-500/5 rounded-full blur-xl group-hover:bg-amber-500/10 transition-all" />
      </div>

      {/* Guardrail Policy Enforcements */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 relative overflow-hidden group hover:border-indigo-500/50 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Guardrail Halts</span>
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3">
          <h3 className="text-2xl font-bold text-indigo-400 font-mono">
            {metrics.stoppedByGuardrails + metrics.escalatedToHuman}
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            {metrics.escalatedToHuman} high-value escalations, {metrics.stoppedByGuardrails} max-attempt limits
          </p>
        </div>
        <div className="absolute -right-4 -bottom-4 w-16 h-16 bg-indigo-500/5 rounded-full blur-xl group-hover:bg-indigo-500/10 transition-all" />
      </div>
    </div>
  );
};
