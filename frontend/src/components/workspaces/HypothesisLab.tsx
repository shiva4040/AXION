import React, { useState } from 'react';
import { FlaskConical, Sparkles, CheckCircle2, ArrowRight } from 'lucide-react';
import { generateHypotheses } from '../../api/client';

export const HypothesisLab: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [hypotheses, setHypotheses] = useState<any[]>([]);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const mockTransferRecord = {
        transfer_id: 'TR_DEMO_01',
        source_domain: 'fluid_mechanics',
        target_domain: 'electrodynamics',
        applicability_verdict: 'ACCEPTED',
        projected_relations: [
          {
            relation_id: 'PR_01',
            relation_type: 'PROPORTIONAL_TO',
            source_concept: 'voltage_difference',
            target_concept: 'electric_current',
            equation: 'I = V / R',
            epistemic_tier: 'HYPOTHESIS_CONJECTURED',
          },
        ],
        concept_alignments: {
          pressure_difference: 'voltage_difference',
          volumetric_flow_rate: 'electric_current',
          hydraulic_resistance: 'electrical_resistance',
        },
      };

      const res = await generateHypotheses(mockTransferRecord, true);
      setHypotheses(res);
    } catch (err: any) {
      alert(`Hypothesis synthesis failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center gap-2 mb-2">
        <FlaskConical className="w-5 h-5 text-rose-600" />
        <h1 className="text-xl font-bold text-gray-900">Hypothesis Lab</h1>
      </div>
      <p className="text-xs text-gray-500 mb-6">
        Component 7: Synthesizes formal, testable scientific hypotheses from accepted/conditional cross-domain transfers under Epistemic Tier 3.
      </p>

      <div className="p-5 bg-white border border-gray-200 rounded-2xl shadow-xs mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-600">
              Formulate Conjectured Hypotheses
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Extract formal mathematical assertions and falsification criteria from transfer records.
            </p>
          </div>
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="text-xs font-semibold px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? 'Synthesizing...' : 'Synthesize Formal Hypotheses'}
          </button>
        </div>
      </div>

      {hypotheses.length > 0 && (
        <div className="space-y-4">
          {hypotheses.map((hyp: any, idx: number) => (
            <div key={idx} className="p-5 bg-white border border-gray-200 rounded-2xl shadow-xs">
              <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-3">
                <span className="text-xs font-bold text-gray-900">{hyp.statement || 'Formal Assertion'}</span>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                  {hyp.epistemic_tier || 'Tier 3 (Conjectured)'}
                </span>
              </div>

              {hyp.mathematical_formulation && (
                <div className="mb-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
                    Formal Mathematical Expression
                  </span>
                  <div className="font-mono text-xs bg-gray-50 text-blue-900 p-2.5 rounded-lg border border-gray-200">
                    {hyp.mathematical_formulation}
                  </div>
                </div>
              )}

              {hyp.falsification_criteria && (
                <div className="text-xs text-gray-600">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
                    Falsification Criteria
                  </span>
                  <p>{hyp.falsification_criteria}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
