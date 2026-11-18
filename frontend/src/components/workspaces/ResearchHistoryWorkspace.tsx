import React, { useEffect, useState } from 'react';
import { History, ArrowRight, ShieldCheck, FileCheck, HelpCircle } from 'lucide-react';
import { getInvestigationHistory } from '../../api/client';
import { ResearchAnswer } from '../../types';

interface Props {
  onSelectAnswer: (ans: ResearchAnswer) => void;
}

export const ResearchHistoryWorkspace: React.FC<Props> = ({ onSelectAnswer }) => {
  const [history, setHistory] = useState<ResearchAnswer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await getInvestigationHistory();
      setHistory(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center gap-2 mb-2">
        <History className="w-5 h-5 text-gray-600" />
        <h1 className="text-xl font-bold text-gray-900">Research History</h1>
      </div>
      <p className="text-xs text-gray-500 mb-6">
        Review past investigations, cross-domain transfers, and cognitive reasoning outcomes.
      </p>

      {loading ? (
        <div className="text-xs text-gray-400 py-8 text-center">Loading history...</div>
      ) : history.length === 0 ? (
        <div className="p-8 bg-gray-50 border border-gray-200 rounded-xl text-center text-xs text-gray-500">
          No previous investigations recorded. Ask a question to begin.
        </div>
      ) : (
        <div className="space-y-3">
          {history.map((item) => (
            <div
              key={item.investigation_id}
              onClick={() => onSelectAnswer(item)}
              className="p-4 bg-white border border-gray-200 rounded-2xl shadow-xs hover:border-blue-400 cursor-pointer transition-all flex items-center justify-between"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-100 uppercase tracking-wider">
                    {item.epistemic_tier}
                  </span>
                  <span className="text-xs text-gray-400 font-mono">
                    ID: {item.investigation_id.substring(0, 8)}...
                  </span>
                </div>
                <h3 className="text-sm font-semibold text-gray-900">{item.query}</h3>
                <p className="text-xs text-gray-500 line-clamp-1">{item.answer}</p>
              </div>

              <div className="flex items-center gap-1 text-xs text-blue-600 font-medium shrink-0 ml-4">
                <span>Inspect</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
