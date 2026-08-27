import React from 'react';
import { Play, Sparkles, RefreshCw, Layers, CheckCheck } from 'lucide-react';

interface BatchRunnerProps {
  onGenerateBatch: () => void;
  onRunDiagnosis: () => void;
  onSimulateRecoveries: () => void;
  isProcessing: boolean;
  progressPercent: number;
  totalLoaded: number;
  diagnosedCount: number;
  recoveredCount: number;
}

export const BatchRunner: React.FC<BatchRunnerProps> = ({
  onGenerateBatch,
  onRunDiagnosis,
  onSimulateRecoveries,
  isProcessing,
  progressPercent,
  totalLoaded,
  diagnosedCount,
  recoveredCount
}) => {
  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-slate-100">Batch Processing & Benchmark Lab</h2>
            <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs px-2 py-0.5 rounded-full font-mono font-medium">
              Track 03 Benchmark Ready
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Run an end-to-end evaluation cycle across 60+ synthetic failed transactions to prove bounded AI diagnosis and measured money recovered.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={onGenerateBatch}
            disabled={isProcessing}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium border border-slate-700 transition-all disabled:opacity-50"
          >
            <RefreshCw className="w-4 h-4 text-slate-400" />
            New Batch (60 Events)
          </button>

          <button
            onClick={onRunDiagnosis}
            disabled={isProcessing || totalLoaded === 0 || diagnosedCount === totalLoaded}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium shadow-md shadow-blue-600/20 transition-all disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-white" />
            Run AI Diagnosis
          </button>

          <button
            onClick={onSimulateRecoveries}
            disabled={isProcessing || diagnosedCount === 0 || recoveredCount > 0}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium shadow-md shadow-emerald-600/20 transition-all disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            Simulate Customer Recovery
          </button>
        </div>
      </div>

      {/* Progress Bar during active processing */}
      {isProcessing && (
        <div className="mt-4 pt-4 border-t border-[#1E293B]">
          <div className="flex justify-between text-xs text-slate-400 mb-1 font-mono">
            <span>Evaluating failure codes & guardrail constraints...</span>
            <span>{Math.round(progressPercent)}%</span>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-emerald-400 h-2 rounded-full transition-all duration-200"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      )}

      {/* Summary status chip */}
      {!isProcessing && totalLoaded > 0 && (
        <div className="mt-4 pt-3 border-t border-[#1E293B] flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-blue-400"></span>
              Total Loaded: <strong className="text-slate-200 font-mono">{totalLoaded}</strong>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              Diagnosed: <strong className="text-slate-200 font-mono">{diagnosedCount}</strong>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              Recovered: <strong className="text-slate-200 font-mono">{recoveredCount}</strong>
            </span>
          </div>
          <span className="text-slate-500 flex items-center gap-1">
            <CheckCheck className="w-3.5 h-3.5 text-emerald-400" />
            All monetary interventions strictly bounded
          </span>
        </div>
      )}
    </div>
  );
};
