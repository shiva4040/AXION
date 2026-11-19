import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  ArrowLeft,
  ChevronDown,
  ChevronUp,
  Share2,
  Terminal,
  Bookmark,
  ShieldCheck,
  FileCheck,
  HelpCircle,
} from 'lucide-react';
import { ResearchAnswer, TransferInfo } from '../types';
import { Scientific3DViewer } from './three/Scientific3DViewer';

interface Props {
  answerData: ResearchAnswer;
  onNewQuestion: () => void;
}

export const MarkdownRenderer: React.FC<{ content: string; className?: string }> = ({
  content,
  className = '',
}) => (
  <div className={`prose-sm max-w-none font-mono leading-relaxed text-[#211E19] ${className}`}>
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        strong: ({ ...props }) => <strong className="font-bold text-[#211E19]" {...props} />,
        p: ({ ...props }) => <p className="mb-3 text-xs sm:text-sm leading-relaxed text-[#211E19] last:mb-0" {...props} />,
        ul: ({ ...props }) => <ul className="list-disc pl-5 mb-3 space-y-1.5 text-xs sm:text-sm text-[#211E19]" {...props} />,
        ol: ({ ...props }) => <ol className="list-decimal pl-5 mb-3 space-y-1.5 text-xs sm:text-sm text-[#211E19]" {...props} />,
        li: ({ ...props }) => <li className="text-xs sm:text-sm text-[#211E19] leading-relaxed" {...props} />,
        code: ({ ...props }) => (
          <code className="bg-[#E9DFC5] text-[#211E19] px-1.5 py-0.5 font-mono text-xs border border-[#29251F]" {...props} />
        ),
        h1: ({ ...props }) => <h1 className="font-mono text-base font-bold text-[#211E19] mb-2 mt-4 uppercase" {...props} />,
        h2: ({ ...props }) => <h2 className="font-mono text-sm font-bold text-[#211E19] mb-1.5 mt-3 uppercase" {...props} />,
        h3: ({ ...props }) => <h3 className="font-mono text-xs font-bold text-[#70695D] mb-1 mt-2 uppercase tracking-wider" {...props} />,
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

  // Direct answer extraction
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

  const renderTierBadge = () => {
    const tier = (answerData.epistemic_tier || 'FACT_DOCUMENTED').toUpperCase();
    if (tier.includes('VALIDATED') || tier.includes('TIER_4') || tier.includes('TIER 4')) {
      return (
        <span className="inline-flex items-center gap-1 font-mono text-[10px] font-bold uppercase tracking-widest text-[#347C70] border-[1.5px] border-[#347C70] px-2 py-0.5 bg-[#EAF4F3] shadow-[1px_1px_0px_#347C70]">
          <ShieldCheck className="w-3 h-3 stroke-[2.2]" />
          TIER 4 // VALIDATED
        </span>
      );
    }
    if (tier.includes('HYPOTHESIS') || tier.includes('CONJECTURED') || tier.includes('TIER_3') || tier.includes('TIER 3')) {
      return (
        <span className="inline-flex items-center gap-1 font-mono text-[10px] font-bold uppercase tracking-widest text-[#B93620] border-[1.5px] border-[#B93620] px-2 py-0.5 bg-[#FBEBE9] shadow-[1px_1px_0px_#B93620]">
          <HelpCircle className="w-3 h-3 stroke-[2.2]" />
          TIER 3 // CONJECTURE
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 font-mono text-[10px] font-bold uppercase tracking-widest text-[#211E19] border-[1.5px] border-[#29251F] px-2 py-0.5 bg-[#F3EBD8] shadow-[1px_1px_0px_#29251F]">
        <FileCheck className="w-3 h-3 stroke-[2.2]" />
        TIER 1 // FACT
      </span>
    );
  };

  return (
    <div className="w-full max-w-[820px] mx-auto px-4 sm:px-6 pt-8 pb-20 select-text">
      {/* Top Action Bar */}
      <div className="border-b-[1.5px] border-[#29251F] pb-3 mb-6 select-none flex flex-wrap items-center justify-between gap-3">
        <button
          onClick={onNewQuestion}
          className="h-8 px-3 bg-[#F3EBD8] hover:bg-[#E9DFC5] text-[#211E19] border-2 border-[#29251F] shadow-[2px_2px_0px_#29251F] active:translate-x-[1px] active:translate-y-[1px] active:shadow-none flex items-center gap-1.5 font-mono text-xs font-bold uppercase tracking-wider cursor-pointer transition-none"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>RETURN TO QUERY DESK</span>
        </button>

        <div className="flex items-center gap-2">
          {renderTierBadge()}
        </div>
      </div>

      {/* Query Heading Title */}
      <div className="mb-6">
        <span className="font-mono text-[10px] font-bold uppercase tracking-widest text-[#70695D] block mb-1">
          RESEARCH PROBLEM SPECIFICATION // {answerData.investigation_id.substring(0, 8)}
        </span>
        <h1 className="font-mono text-xl sm:text-2xl font-bold tracking-tight text-[#211E19] leading-snug">
          {answerData.query}
        </h1>
      </div>

      {/* SECTION 1: DIRECT ANSWER WINDOW */}
      <section className="mb-8 bg-[#F9F3E6] border-2 border-[#29251F] shadow-[4px_4px_0px_#29251F] overflow-hidden">
        {/* Titlebar */}
        <div className="relative h-[28px] bg-[#F3EBD8] border-b-[1.5px] border-[#29251F] flex items-center justify-between px-2.5 select-none">
          <div
            className="absolute inset-0 pointer-events-none opacity-85"
            style={{
              background:
                'repeating-linear-gradient(to bottom, transparent 0px, transparent 2px, #29251F 2px, #29251F 3px)',
            }}
          />
          <div className="relative z-10 w-[12px] h-[12px] bg-[#F9F3E6] border border-[#29251F]" />
          <div className="relative z-10 px-2 py-0.5 bg-[#F9F3E6] border border-[#29251F] font-mono text-[10px] font-bold tracking-wider text-[#211E19] uppercase">
            DIRECT_SYNTHESIS.TXT
          </div>
          <div className="relative z-10 w-[12px] h-[12px] opacity-0" />
        </div>

        <div className="p-5 sm:p-6">
          <MarkdownRenderer content={directAnswer} className="text-sm sm:text-base leading-relaxed" />
        </div>
      </section>

      {/* SECTION 2: KEY SCIENTIFIC PRINCIPLES */}
      <section className="mb-8">
        <div className="font-mono text-[11px] font-bold uppercase tracking-widest text-[#70695D] mb-2 flex items-center gap-1.5">
          <Bookmark className="w-3.5 h-3.5 text-[#B93620]" />
          <span>GOVERNING CONSTITUTIVE PRINCIPLES</span>
        </div>
        <div className="border-2 border-[#29251F] bg-[#F9F3E6] shadow-[2px_2px_0px_#29251F] divide-y divide-[#29251F]">
          {importantPoints.map((point, idx) => (
            <div key={idx} className="p-3.5 flex items-start gap-3">
              <span className="font-mono text-[10px] font-bold text-[#211E19] mt-0.5 bg-[#F3EBD8] px-1.5 py-0.5 border border-[#29251F] shrink-0">
                P.{idx + 1}
              </span>
              <MarkdownRenderer content={point} className="flex-1 text-xs sm:text-sm" />
            </div>
          ))}
        </div>
      </section>

      {/* SECTION 3: HOW IT WORKS (MECHANISM BREAKDOWN) */}
      {howItWorks && howItWorks.length > 0 && (
        <section className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="font-mono text-[11px] font-bold uppercase tracking-widest text-[#70695D]">
              MECHANISM & DYNAMICAL PROCESS ({howItWorks.length} STEPS)
            </span>
            {howItWorks.length > 3 && (
              <button
                onClick={() => setShowAllSteps(!showAllSteps)}
                className="font-mono text-[11px] text-[#211E19] hover:underline font-bold flex items-center gap-1 uppercase cursor-pointer"
              >
                <span>{showAllSteps ? '[COLLAPSE]' : `[VIEW ALL ${howItWorks.length}]`}</span>
                {showAllSteps ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
            )}
          </div>

          <div className="border-2 border-[#29251F] bg-[#F9F3E6] shadow-[2px_2px_0px_#29251F] divide-y divide-[#29251F]">
            {(showAllSteps ? howItWorks : howItWorks.slice(0, 3)).map((step) => (
              <div key={step.step} className="p-3.5 flex items-start gap-3.5">
                <div className="font-mono text-xs font-bold text-[#211E19] bg-[#F3EBD8] border border-[#29251F] px-2 py-0.5 shrink-0">
                  {step.step.toString().padStart(2, '0')}
                </div>
                <div className="flex-1">
                  <h4 className="font-mono text-xs font-bold uppercase text-[#211E19] mb-0.5">
                    {step.action}
                  </h4>
                  <p className="text-xs text-[#70695D] leading-relaxed font-mono">
                    {step.detail}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* SECTION 4: 3D SCIENTIFIC PHYSICAL MODEL */}
      <section className="mb-8">
        <div className="font-mono text-[11px] font-bold uppercase tracking-widest text-[#70695D] mb-1">
          PHYSICAL APPARATUS & SPATIAL MODEL
        </div>
        <p className="text-xs font-mono text-[#70695D] mb-3">
          Interactive WebGL viewport illustrating governing physical geometry. Drag to rotate, scroll to zoom.
        </p>
        <Scientific3DViewer initialScene={suggestedScene} queryContext={answerData.query} />
      </section>

      {/* SECTION 5: CROSS-DOMAIN TRANSFER GUARD */}
      {answerData.transfers && answerData.transfers.length > 0 && (
        <section className="mb-8">
          <div className="flex items-center gap-2 mb-1">
            <Share2 className="w-4 h-4 text-[#211E19]" />
            <span className="font-mono text-[11px] font-bold uppercase tracking-widest text-[#70695D]">
              CROSS-DOMAIN STRUCTURAL TRANSFER GUARD
            </span>
          </div>
          <p className="text-xs font-mono text-[#70695D] mb-3">
            Gentner structural alignment evaluating relational isomorphism across physical fields.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2 md:col-span-1">
              {answerData.transfers.map((t, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedTransfer(t)}
                  className={`w-full text-left p-3 border-2 border-[#29251F] text-xs transition-none cursor-pointer ${
                    selectedTransfer === t
                      ? 'bg-[#F9F3E6] shadow-[2px_2px_0px_#29251F] font-bold'
                      : 'bg-[#F3EBD8] hover:bg-[#E9DFC5]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1 font-mono text-[10px]">
                    <span className="truncate">{t.source} &rarr; {t.target}</span>
                    <span
                      className={`px-1 py-0.5 border ${
                        t.verdict === 'ACCEPTED'
                          ? 'bg-[#EAF4F3] text-[#347C70] border-[#347C70]'
                          : 'bg-[#FBEBE9] text-[#B93620] border-[#B93620]'
                      }`}
                    >
                      {t.verdict}
                    </span>
                  </div>
                  <div className="text-[11px] text-[#70695D] line-clamp-1">{t.rationale}</div>
                </button>
              ))}
            </div>

            {selectedTransfer && (
              <div className="md:col-span-2 p-4 bg-[#F9F3E6] border-2 border-[#29251F] shadow-[2px_2px_0px_#29251F]">
                <div className="flex items-center justify-between border-b border-[#29251F] pb-2 mb-3 font-mono text-xs">
                  <span className="font-bold text-[#211E19]">
                    {selectedTransfer.source} &rarr; {selectedTransfer.target}
                  </span>
                  <span className="text-[10px] uppercase font-bold text-[#347C70]">
                    GUARD: {selectedTransfer.verdict}
                  </span>
                </div>

                {selectedTransfer.equation && (
                  <div className="mb-3">
                    <span className="text-[9px] font-mono font-bold uppercase tracking-wider text-[#70695D] block mb-1">
                      TRANSFERRED MATHEMATICAL RELATION
                    </span>
                    <div className="font-mono text-xs bg-[#F3EBD8] text-[#211E19] p-2.5 border border-[#29251F]">
                      {selectedTransfer.equation}
                    </div>
                  </div>
                )}

                <div className="mb-3">
                  <span className="text-[9px] font-mono font-bold uppercase tracking-wider text-[#70695D] block mb-1">
                    APPLICABILITY RATIONALE
                  </span>
                  <p className="text-xs text-[#70695D] leading-relaxed font-mono">
                    {selectedTransfer.rationale}
                  </p>
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* SECTION 6: FINAL TAKEAWAY */}
      <section className="mb-8 p-4 bg-[#F3EBD8] border-2 border-[#29251F] shadow-[2px_2px_0px_#29251F]">
        <div className="font-mono text-[10px] font-bold uppercase tracking-widest text-[#211E19] mb-1">
          FINAL RESEARCH TAKEAWAY
        </div>
        <MarkdownRenderer content={finalTakeaway} className="text-xs sm:text-sm text-[#211E19] font-medium" />
      </section>

      {/* SECTION 7: GROUNDING EVIDENCE */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-2 border-b-[1.5px] border-[#29251F] pb-1">
          <span className="font-mono text-[11px] font-bold uppercase tracking-widest text-[#70695D]">
            GROUNDING EVIDENCE & PROVENANCE
          </span>
          {answerData.evidence_snippets && answerData.evidence_snippets.length > 2 && (
            <button
              onClick={() => setShowAllEvidence(!showAllEvidence)}
              className="font-mono text-[10px] text-[#211E19] hover:underline uppercase font-bold cursor-pointer"
            >
              {showAllEvidence ? '[SHOW LESS]' : `[VIEW ALL (${answerData.evidence_snippets.length})]`}
            </button>
          )}
        </div>

        {answerData.evidence_snippets && answerData.evidence_snippets.length > 0 ? (
          <div className="space-y-2.5">
            {(showAllEvidence ? answerData.evidence_snippets : answerData.evidence_snippets.slice(0, 2)).map((ev, idx) => (
              <div
                key={idx}
                className="p-3 bg-[#F9F3E6] border-2 border-[#29251F] text-xs shadow-[2px_2px_0px_#29251F]"
              >
                <div className="flex items-center justify-between text-[#70695D] mb-1 text-[11px] font-mono">
                  <span className="font-bold text-[#211E19] truncate">{ev.source}</span>
                  <span className="px-1.5 py-0.2 border border-[#29251F] bg-[#F3EBD8] text-[9px] uppercase">
                    {ev.epistemic_tier}
                  </span>
                </div>
                <blockquote className="text-[#211E19] font-mono italic border-l-2 border-[#B93620] pl-2.5 my-1 leading-relaxed">
                  "{ev.snippet}"
                </blockquote>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-4 bg-[#F9F3E6] border-2 border-[#29251F] text-xs font-mono text-[#70695D] text-center">
            Derived analytically from verified dimensional and physical axioms in the knowledge graph.
          </div>
        )}
      </section>

      {/* SECTION 8: TECHNICAL DIAGNOSTICS */}
      <section className="mb-8 border-t-[1.5px] border-[#29251F] pt-3 select-none">
        <button
          onClick={() => setShowDiagnostics(!showDiagnostics)}
          className="flex items-center justify-between w-full text-left py-1 text-xs font-mono text-[#70695D] hover:text-[#211E19] cursor-pointer"
        >
          <div className="flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5" />
            <span>TECHNICAL PIPELINE DIAGNOSTICS</span>
          </div>
          {showDiagnostics ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {showDiagnostics && (
          <div className="mt-2 p-3 bg-[#211E19] text-[#F9F3E6] font-mono text-[11px] space-y-1 overflow-x-auto border border-[#29251F]">
            <div>// Investigation ID: {answerData.investigation_id}</div>
            <div>// Epistemic Rigor: {answerData.epistemic_tier}</div>
            <div>// Domains Involved: {JSON.stringify(answerData.domains_involved)}</div>
            <div>// Suggested Scene: {suggestedScene}</div>
            <div>// Hypotheses Evaluated: {answerData.hypotheses?.length || 0}</div>
            <div>// Sandbox Experiments: {answerData.experiments?.length || 0}</div>
          </div>
        )}
      </section>
    </div>
  );
};
