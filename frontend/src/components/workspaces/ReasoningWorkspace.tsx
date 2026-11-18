import React, { useState } from 'react';
import { GitBranch, AlertTriangle, Play, Sparkles, CheckCircle2 } from 'lucide-react';
import { decomposeGoal, solveGoal, getContradictions } from '../../api/client';

export const ReasoningWorkspace: React.FC = () => {
  const [goal, setGoal] = useState('Determine electrical power dissipated in a conductor given current and voltage');
  const [loading, setLoading] = useState(false);
  const [dagResult, setDagResult] = useState<any | null>(null);
  const [solveResult, setSolveResult] = useState<any | null>(null);
  const [contradictions, setContradictions] = useState<any[]>([]);
  const [scanning, setScanning] = useState(false);

  const handleDecompose = async () => {
    setLoading(true);
    try {
      const res = await decomposeGoal(goal);
      setDagResult(res);
      setSolveResult(null);
    } catch (err: any) {
      alert(`Decomposition failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSolve = async () => {
    setLoading(true);
    try {
      const res = await solveGoal(goal);
      setSolveResult(res);
      setDagResult(res.reasoning_dag || null);
    } catch (err: any) {
      alert(`Reasoning solver failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleScanContradictions = async () => {
    setScanning(true);
    try {
      const res = await getContradictions();
      setContradictions(res);
    } catch (err: any) {
      alert(`Contradiction scan failed: ${err.message}`);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center gap-2 mb-2">
        <GitBranch className="w-5 h-5 text-purple-600" />
        <h1 className="text-xl font-bold text-gray-900">Reasoning Workspace</h1>
      </div>
      <p className="text-xs text-gray-500 mb-6">
        Component 5: Inspectable problem decomposition into Directed Acyclic Graphs (DAG), step-by-step mathematical derivation, and literature contradiction detection.
      </p>

      {/* Goal Input Card */}
      <div className="p-4 bg-white border border-gray-200 rounded-2xl shadow-xs mb-8">
        <label className="text-xs font-bold uppercase tracking-wider text-gray-400 block mb-1.5">
          Research or Engineering Goal
        </label>
        <textarea
          rows={2}
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          className="w-full text-xs border border-gray-200 rounded-lg p-2.5 focus:outline-none focus:border-blue-500 mb-3"
        />
        <div className="flex items-center gap-2">
          <button
            onClick={handleDecompose}
            disabled={loading || !goal.trim()}
            className="text-xs font-medium px-3.5 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors disabled:opacity-50"
          >
            Decompose into DAG
          </button>
          <button
            onClick={handleSolve}
            disabled={loading || !goal.trim()}
            className="text-xs font-semibold px-4 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Execute Full Reasoning</span>
          </button>
          <button
            onClick={handleScanContradictions}
            disabled={scanning}
            className="ml-auto text-xs font-medium px-3.5 py-1.5 text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-lg transition-colors flex items-center gap-1.5"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Scan Contradictions</span>
          </button>
        </div>
      </div>

      {/* Contradictions Alert View */}
      {contradictions.length > 0 && (
        <div className="p-4 bg-amber-50/70 border border-amber-200 rounded-2xl mb-8">
          <h3 className="text-xs font-bold uppercase tracking-wider text-amber-800 mb-2 flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            Literature Contradictions Detected ({contradictions.length})
          </h3>
          <div className="space-y-2">
            {contradictions.map((c, idx) => (
              <div key={idx} className="p-3 bg-white/90 rounded-xl border border-amber-200 text-xs">
                <span className="font-semibold text-gray-900">{c.concept_pair?.join(' vs ')}</span>
                <p className="text-gray-600 text-[11px] mt-0.5">{c.conflict_description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Solver Outcome */}
      {solveResult && (
        <div className="p-5 bg-white border border-gray-200 rounded-2xl shadow-xs mb-8">
          <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-3">
            <span className="text-xs font-bold text-gray-900">Reasoning Outcome</span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-200">
              Confidence: {Math.round((solveResult.confidence_score || 0.95) * 100)}%
            </span>
          </div>
          <p className="text-xs text-gray-800 leading-relaxed mb-4 font-mono bg-gray-50 p-3 rounded-lg border border-gray-100">
            {solveResult.synthesized_answer}
          </p>
        </div>
      )}

      {/* DAG Visualization */}
      {dagResult && (
        <div className="p-4 bg-white border border-gray-200 rounded-2xl shadow-xs">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
            Reasoning Dependency DAG: {dagResult.goal_description}
          </h3>
          <div className="space-y-2">
            {dagResult.sub_tasks?.map((task: any) => (
              <div key={task.task_id} className="p-3 bg-[#fbfbfc] rounded-xl border border-gray-200 text-xs">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-gray-900">Task {task.task_id}: {task.description}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gray-100 text-gray-600">
                    {task.operator || 'EVALUATE'}
                  </span>
                </div>
                {task.dependencies && task.dependencies.length > 0 && (
                  <div className="text-[11px] text-gray-500 font-mono mt-1">
                    Dependencies: {task.dependencies.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
