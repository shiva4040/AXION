import React, { useEffect, useState } from 'react';
import { Database, ShieldCheck, AlertCircle, History, RefreshCw } from 'lucide-react';
import { getValidatedFindings, invalidateFinding } from '../../api/client';
import { ValidatedFinding } from '../../types';

export const MemoryWorkspace: React.FC = () => {
  const [findings, setFindings] = useState<ValidatedFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string>('ACTIVE');
  const [invalidatingId, setInvalidatingId] = useState<string | null>(null);

  useEffect(() => {
    loadFindings();
  }, [selectedStatus]);

  const loadFindings = async () => {
    setLoading(true);
    try {
      const data = await getValidatedFindings(undefined, selectedStatus);
      setFindings(data);
    } finally {
      setLoading(false);
    }
  };

  const handleInvalidate = async (id: string) => {
    const reason = prompt('Enter scientific reason for invalidating this finding:');
    if (!reason) return;
    setInvalidatingId(id);
    try {
      await invalidateFinding(id, reason);
      await loadFindings();
    } catch (err: any) {
      alert(`Invalidation failed: ${err.message}`);
    } finally {
      setInvalidatingId(null);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center gap-2 mb-2">
        <Database className="w-5 h-5 text-blue-700" />
        <h1 className="text-xl font-bold text-gray-900">Validated Knowledge Memory</h1>
      </div>
      <p className="text-xs text-gray-500 mb-6">
        Component 9: Persistent storage of Tier 4 validated scientific findings, immutable version audit logs, and cascading dependency invalidation.
      </p>

      {/* Filter Bar */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-gray-400">Status Filter:</span>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="text-xs border border-gray-200 rounded-lg px-2.5 py-1.5 bg-white font-medium"
          >
            <option value="ACTIVE">ACTIVE (Verified Valid)</option>
            <option value="SUPERSEDED">SUPERSEDED (Refined by New Model)</option>
            <option value="INVALIDATED">INVALIDATED (Falsified)</option>
          </select>
        </div>

        <button
          onClick={loadFindings}
          className="text-xs text-gray-600 hover:text-blue-600 flex items-center gap-1"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Findings List */}
      {loading ? (
        <div className="text-xs text-gray-400 py-8 text-center">Loading validated memory...</div>
      ) : findings.length === 0 ? (
        <div className="p-8 bg-gray-50 border border-gray-200 rounded-xl text-center text-xs text-gray-500">
          No validated findings matching status "{selectedStatus}".
        </div>
      ) : (
        <div className="space-y-3">
          {findings.map((f) => (
            <div
              key={f.id}
              className="p-5 bg-white border border-gray-200 rounded-2xl shadow-xs"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                      Tier 4 Validated
                    </span>
                    <span className="text-xs font-semibold text-gray-900">{f.title}</span>
                  </div>
                  <div className="text-[11px] text-gray-500 font-mono mt-1">
                    ID: {f.id} &bull; Domain: {f.domain} &bull; v{f.version}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      f.status === 'ACTIVE'
                        ? 'bg-emerald-50 text-emerald-700'
                        : f.status === 'SUPERSEDED'
                        ? 'bg-blue-50 text-blue-700'
                        : 'bg-red-50 text-red-700'
                    }`}
                  >
                    {f.status}
                  </span>
                  {f.status === 'ACTIVE' && (
                    <button
                      onClick={() => handleInvalidate(f.id)}
                      disabled={invalidatingId === f.id}
                      className="text-[11px] text-red-600 hover:text-red-700 px-2 py-1 border border-red-200 rounded-md hover:bg-red-50 transition-colors"
                    >
                      Invalidate
                    </button>
                  )}
                </div>
              </div>

              <div className="p-3 bg-gray-50 rounded-xl font-mono text-xs text-gray-800 my-2">
                {f.formal_statement}
              </div>

              <div className="flex items-center justify-between text-[11px] text-gray-400">
                <span>Confidence: {Math.round(f.confidence_score * 100)}%</span>
                <span>Supporting experiments: {f.supporting_experiments?.length || 1} records</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
