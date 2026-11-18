import React, { useEffect, useState } from 'react';
import { Cpu, Send, BookOpen, Sparkles } from 'lucide-react';
import { getDocuments } from '../../api/client';
import { DocumentSummary } from '../../types';

interface Props {
  onRunInvestigation: (query: string, documentId?: string) => void;
  isLoading: boolean;
}

export const ResearchAssistant: React.FC<Props> = ({ onRunInvestigation, isLoading }) => {
  const [query, setQuery] = useState('');
  const [docs, setDocs] = useState<DocumentSummary[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string>('');

  useEffect(() => {
    getDocuments().then(setDocs).catch(() => {});
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onRunInvestigation(query.trim(), selectedDocId || undefined);
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center gap-2 mb-2">
        <Cpu className="w-5 h-5 text-sky-600" />
        <h1 className="text-xl font-bold text-gray-900">Research Assistant</h1>
      </div>
      <p className="text-xs text-gray-500 mb-6">
        Formulate complex scientific investigations with document-grounded context and cross-domain reasoning constraints.
      </p>

      <form onSubmit={handleSubmit} className="p-5 bg-white border border-gray-200 rounded-2xl shadow-xs space-y-4">
        <div>
          <label className="text-xs font-bold uppercase tracking-wider text-gray-500 block mb-1.5">
            Scientific Question or Hypothesis Inquiry
          </label>
          <textarea
            rows={3}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., Can we transfer hydraulic pipe flow equations to analyze electron transport in graphene conductors?"
            className="w-full text-xs border border-gray-200 rounded-xl p-3 focus:outline-none focus:border-blue-500 leading-relaxed"
            required
          />
        </div>

        <div>
          <label className="text-xs font-bold uppercase tracking-wider text-gray-500 block mb-1.5 flex items-center gap-1.5">
            <BookOpen className="w-3.5 h-3.5 text-gray-400" />
            Grounding Source Document (Optional)
          </label>
          <select
            value={selectedDocId}
            onChange={(e) => setSelectedDocId(e.target.value)}
            className="w-full text-xs border border-gray-200 rounded-xl px-3 py-2 bg-white"
          >
            <option value="">No document grounding (Direct Cross-Domain Knowledge Base)</option>
            {docs.map((d) => (
              <option key={d.id} value={d.id}>
                {d.title} ({d.trust_tier})
              </option>
            ))}
          </select>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="text-xs font-semibold px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Launch Investigation</span>
          </button>
        </div>
      </form>
    </div>
  );
};
