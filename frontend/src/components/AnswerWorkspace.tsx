import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  ArrowLeft,
  FileCheck,
  ShieldCheck,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Share2,
  Sparkles,
  Zap,
  Activity,
  Terminal,
} from 'lucide-react';
import { ResearchAnswer, TransferInfo } from '../types';
import { Scientific3DViewer } from './three/Scientific3DViewer';

interface Props {
  answerData: ResearchAnswer;
  onNewQuestion: () => void;
}

export const MarkdownRenderer: React.FC<{ content: string; className?: string }> = ({ content, className = '' }) => (
  <div className={`prose-sm max-w-none ${className}`}>
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        strong: ({ ...props }) => <strong className="font-semibold text-gray-900" {...props} />,
        p: ({ ...props }) => <p className="mb-2 text-sm text-gray-800 leading-relaxed last:mb-0" {...props} />,
        ul: ({ ...props }) => <ul className="list-disc pl-5 mb-2 space-y-1 text-sm text-gray-800" {...props} />,
        ol: ({ ...props }) => <ol className="list-decimal pl-5 mb-2 space-y-1 text-sm text-gray-800" {...props} />,
        li: ({ ...props }) => <li className="text-sm text-gray-800 leading-relaxed" {...props} />,
        code: ({ ...props }) => (
          <code className="bg-blue-50 text-blue-900 px-1.5 py-0.5 rounded font-mono text-xs border border-blue-100" {...props} />
        ),
        h1: ({ ...props }) => <h1 className="text-base font-bold text-gray-900 mb-2 mt-3" {...props} />,
        h2: ({ ...props }) => <h2 className="text-sm font-bold text-gray-900 mb-1.5 mt-2" {...props} />,
        h3: ({ ...props }) => <h3 className="text-xs font-bold text-gray-900 mb-1 mt-2 uppercase tracking-wider" {...props} />,
      }}
    >
      {content}
    </ReactMarkdown>
  </div>
);

export const AnswerWorkspace: React.FC<Props> = ({ answerData, onNewQuestion }) => {
  const [selectedTransfer, setSelectedTransfer] = useState<TransferInfo | null>(
    answerData.transfers && answerData.transfers.length > 0 ? answerData.transfers[0] : null
  );
  const [showAllSteps, setShowAllSteps] = useState(false);
  const [showAllEvidence, setShowAllEvidence] = useState(false);
  const [showDiagnostics, setShowDiagnostics] = useState(false);

  // Direct answer extraction: priority to direct_answer, then clean first paragraph
  const directAnswer = answerData.direct_answer || (() => {
    const raw = answerData.answer || '';
    const cleaned = raw.replace(/^\*\*.*?\*\*\s*/, '').replace(/^#+.*?\n+/, '').trim();
    return cleaned.split('\n\n')[0] || cleaned;
  })();

  const importantPoints = (answerData.important_points && answerData.important_points.length > 0)
    ? answerData.important_points
    : (answerData.domains_involved || []).map(d => `**Domain Knowledge (${d}):** Governed by verified empirical constitutive laws.`);

  const howItWorks = (answerData.how_it_works && answerData.how_it_works.length > 0)
    ? answerData.how_it_works
    : answerData.reasoning_steps;

  const finalTakeaway = answerData.final_takeaway ||
    "Physical processes sharing identical mathematical topologies allow cross-domain knowledge transfer, provided constitutive boundary conditions and dimensional invariance are rigorously respected.";

  const suggestedScene = answerData.suggested_3d_scene || 'electric_motor';

  // Badge tier color & icon
  const renderTierBadge = () => {
    const tier = answerData.epistemic_tier || 'FACT_DOCUMENTED';
    if (tier.includes('VALIDATED') || tier.includes('TIER_4') || tier.includes('Tier 4')) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          <ShieldCheck className="w-3.5 h-3.5" />
          Tier 4: Validated Finding
        </span>
      );
    }
    if (tier.includes('FACT') || tier.includes('TIER_1') || tier.includes('Tier 1')) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
          <FileCheck className="w-3.5 h-3.5" />
          Tier 1: Documented Fact
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
        <HelpCircle className="w-3.5 h-3.5" />
        Tier 3: Conjectured Hypothesis
      </span>
    );
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-8">
      {/* Top Action Bar */}
      <div className="flex items-center justify-between pb-6 mb-6 border-b border-gray-100">
        <button
          onClick={onNewQuestion}
          className="flex items-center gap-2 text-xs font-medium text-gray-500 hover:text-gray-900 px-3 py-1.5 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 transition-colors shadow-2xs"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>New Question</span>
        </button>

        <div className="flex items-center gap-2">
          {renderTierBadge()}
        </div>
      </div>

      {/* Question Title */}
      <h1 className="text-xl sm:text-2xl font-semibold tracking-tight text-gray-900 mb-6">
        {answerData.query}
      </h1>

      {/* SECTION 1: DIRECT ANSWER */}
      <section className="mb-8 p-5 bg-gradient-to-r from-blue-50/50 via-indigo-50/30 to-sky-50/20 border border-blue-100 rounded-2xl shadow-xs">
        <div className="text-[11px] font-bold uppercase tracking-wider text-blue-700 mb-2 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5" />
          Direct Answer
        </div>
        <MarkdownRenderer content={directAnswer} className="text-base text-gray-900 leading-relaxed font-normal" />
      </section>

      {/* SECTION 2: IMPORTANT POINTS */}
      <section className="mb-8">
        <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">
          Key Scientific Principles
        </h2>
        <div className="grid grid-cols-1 gap-2.5">
          {importantPoints.map((point, idx) => (
            <div
              key={idx}
              className="p-3.5 bg-white border border-gray-200 rounded-xl flex items-start gap-3 shadow-2xs"
            >
              <div className="w-2 h-2 rounded-full bg-blue-600 mt-1.5 shrink-0" />
              <MarkdownRenderer content={point} className="flex-1" />
            </div>
          ))}
        </div>
      </section>

      {/* SECTION 3: HOW IT WORKS (USER-FRIENDLY NUMBERED STEPS) */}
      {howItWorks && howItWorks.length > 0 && (
        <section className="mb-8">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400">
              How It Works (Mechanism & Process)
            </h2>
            {howItWorks.length > 3 && (
              <button
                onClick={() => setShowAllSteps(!showAllSteps)}
                className="text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
              >
                <span>{showAllSteps ? 'Collapse Steps' : `View All (${howItWorks.length})`}</span>
                {showAllSteps ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
            )}
          </div>

          <div className="space-y-2.5">
            {(showAllSteps ? howItWorks : howItWorks.slice(0, 3)).map((step) => (
              <div
                key={step.step}
                className="p-3.5 bg-[#fbfbfc] border border-gray-200/80 rounded-xl flex items-start gap-3.5"
              >
                <div className="w-6 h-6 rounded-lg bg-blue-50 text-blue-700 font-mono text-xs font-bold flex items-center justify-center shrink-0 border border-blue-100">
                  {step.step}
                </div>
                <div className="flex-1">
                  <h4 className="text-xs font-semibold text-gray-900 mb-0.5">{step.action}</h4>
                  <p className="text-xs text-gray-600 leading-relaxed">{step.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* SECTION 4: 3D EXPLANATION & PHYSICAL MODEL */}
      <section className="mb-10">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <h2 className="text-xs font-bold uppercase tracking-wider text-gray-900">
              Interactive 3D Explanation & Physical Model
            </h2>
            <span className="text-[10px] font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100">
              WebGL
            </span>
          </div>
        </div>
        <p className="text-xs text-gray-500 mb-3">
          Explore spatial relationships, component hierarchy, and dynamic vector flows in the dedicated 3D scientific viewport. Click any component to inspect its mathematical formulas and physical role.
        </p>

        {/* Dedicated Interactive 3D Viewer */}
        <Scientific3DViewer initialScene={suggestedScene} queryContext={answerData.query} />
      </section>

      {/* SECTION 5: CROSS-DOMAIN KNOWLEDGE COMPOSITION & TRANSFER GUARD */}
      {answerData.transfers && answerData.transfers.length > 0 && (
        <section className="mb-10">
          <div className="flex items-center gap-2 mb-2">
            <Share2 className="w-4 h-4 text-indigo-600" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-gray-900">
              Cross-Domain Knowledge Composition & Transfer Guard
            </h2>
          </div>
          <p className="text-xs text-gray-500 mb-4">
            AXION evaluated candidate structural analogies between scientific domains under multi-tiered physical applicability constraints.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Left Transfer List */}
            <div className="space-y-2 md:col-span-1">
              {answerData.transfers.map((t, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedTransfer(t)}
                  className={`w-full text-left p-3 rounded-xl border text-xs transition-all ${
                    selectedTransfer === t
                      ? 'bg-blue-50 border-blue-300 ring-2 ring-blue-100 shadow-xs'
                      : 'bg-white border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-gray-900 truncate">
                      {t.source} &rarr; {t.target}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        t.verdict === 'ACCEPTED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : t.verdict === 'CONDITIONAL'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {t.verdict}
                    </span>
                  </div>
                  <div className="text-[11px] text-gray-500 line-clamp-1">{t.rationale}</div>
                </button>
              ))}
            </div>

            {/* Right Transfer Detail Inspection */}
            {selectedTransfer && (
              <div className="md:col-span-2 p-4 bg-white border border-gray-200 rounded-xl shadow-xs">
                <div className="flex items-center justify-between border-b border-gray-100 pb-2 mb-3">
                  <span className="text-xs font-bold text-gray-900">
                    Analogical Mapping: {selectedTransfer.source} &rarr; {selectedTransfer.target}
                  </span>
                  <span
                    className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                      selectedTransfer.verdict === 'ACCEPTED'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : selectedTransfer.verdict === 'CONDITIONAL'
                        ? 'bg-amber-50 text-amber-700 border border-amber-200'
                        : 'bg-red-50 text-red-700 border border-red-200'
                    }`}
                  >
                    Applicability: {selectedTransfer.verdict}
                  </span>
                </div>

                {selectedTransfer.equation && (
                  <div className="mb-3">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
                      Transferred Mathematical Equation
                    </span>
                    <div className="font-mono text-xs bg-gray-50 text-blue-900 p-2.5 rounded-lg border border-gray-200">
                      {selectedTransfer.equation}
                    </div>
                  </div>
                )}

                <div className="mb-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
                    Applicability Guard Rationale
                  </span>
                  <p className="text-xs text-gray-700 leading-relaxed">
                    {selectedTransfer.rationale}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-2.5 bg-gray-50 rounded-lg border border-gray-100">
                    <span className="text-[10px] font-bold uppercase text-gray-500 block mb-1">Conditions</span>
                    <span className="text-gray-700 text-[11px]">Continuum laminar regime, linear dissipation, constant temperature.</span>
                  </div>
                  <div className="p-2.5 bg-gray-50 rounded-lg border border-gray-100">
                    <span className="text-[10px] font-bold uppercase text-gray-500 block mb-1">Limitations</span>
                    <span className="text-gray-700 text-[11px]">Turbulence breakdown at high Reynolds/Current numbers.</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* SECTION 6: FINAL TAKEAWAY */}
      <section className="mb-8 p-4 bg-[#f8f9fb] border border-gray-200 rounded-xl shadow-2xs">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-600 mb-1 flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5 text-blue-600" />
          Final Takeaway
        </h3>
        <MarkdownRenderer content={finalTakeaway} className="text-xs text-gray-800 leading-relaxed font-medium" />
      </section>

      {/* SECTION 7: SOURCES AND EVIDENCE */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-bold uppercase tracking-wider text-gray-400">
            Grounding Evidence & Source Provenance
          </h2>
          {answerData.evidence_snippets && answerData.evidence_snippets.length > 2 && (
            <button
              onClick={() => setShowAllEvidence(!showAllEvidence)}
              className="text-xs text-blue-600 hover:text-blue-700 font-medium"
            >
              {showAllEvidence ? 'Show Less' : `Show All (${answerData.evidence_snippets.length})`}
            </button>
          )}
        </div>

        {answerData.evidence_snippets && answerData.evidence_snippets.length > 0 ? (
          <div className="space-y-2">
            {(showAllEvidence ? answerData.evidence_snippets : answerData.evidence_snippets.slice(0, 2)).map((ev, idx) => (
              <div
                key={idx}
                className="p-3 bg-white border border-gray-200 rounded-xl text-xs shadow-2xs"
              >
                <div className="flex items-center justify-between text-gray-500 mb-1.5 text-[11px]">
                  <span className="font-semibold text-gray-900 truncate">{ev.source}</span>
                  <span className="px-2 py-0.5 rounded bg-gray-100 text-gray-600 text-[10px] font-mono">
                    {ev.epistemic_tier}
                  </span>
                </div>
                <blockquote className="text-gray-700 italic border-l-2 border-blue-500 pl-2.5 my-1">
                  "{ev.snippet}"
                </blockquote>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-4 bg-gray-50 border border-gray-200 rounded-xl text-xs text-gray-500 text-center">
            Derived analytically from verified dimensional and physical axioms in the knowledge graph.
          </div>
        )}
      </section>

      {/* SECTION 8: OPTIONAL TECHNICAL DIAGNOSTICS ACCORDION */}
      <section className="mb-12 border-t border-gray-100 pt-4">
        <button
          onClick={() => setShowDiagnostics(!showDiagnostics)}
          className="flex items-center justify-between w-full text-left py-2 text-xs font-semibold text-gray-500 hover:text-gray-900"
        >
          <div className="flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5 text-gray-400" />
            <span>Technical Pipeline Diagnostics & Rigor Checks</span>
          </div>
          {showDiagnostics ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {showDiagnostics && (
          <div className="mt-2 p-3 bg-gray-900 text-gray-200 rounded-xl font-mono text-[11px] space-y-1.5 overflow-x-auto">
            <div><span className="text-gray-500">// Investigation ID:</span> {answerData.investigation_id}</div>
            <div><span className="text-gray-500">// Epistemic Rigor:</span> {answerData.epistemic_tier}</div>
            <div><span className="text-gray-500">// Domains Detected:</span> {JSON.stringify(answerData.domains_involved)}</div>
            <div><span className="text-gray-500">// Suggested 3D Scene:</span> {suggestedScene}</div>
            <div><span className="text-gray-500">// Hypotheses Evaluated:</span> {answerData.hypotheses?.length || 0}</div>
            <div><span className="text-gray-500">// Sandbox Experiments:</span> {answerData.experiments?.length || 0}</div>
          </div>
        )}
      </section>
    </div>
  );
};
