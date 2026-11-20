import React, { useEffect, useState } from 'react';
import {
  Compass,
  Cpu,
  GitBranch,
  Repeat,
  ShieldCheck,
  Search,
  Sparkles,
  Layers,
  Clock,
  Activity,
  Users,
} from 'lucide-react';

const agentRoles = [
  'Research Coordinator',
  'Intent Understanding Agent',
  'Scientific Domain Discovery Agent',
  'Question Decomposition Agent',
  'Concepts Discovery Agent',
  'Variables, Parameters & Equations Agent',
  'Physical Process Mapping Agent',
  'Materials & Components Agent',
  'Evidence Requirements Agent',
  'Cross-Domain Connection Agent',
  'Knowledge Gap & Constraint Agent',
  'Critical Reviewer Agent',
  'Completeness Evaluator Agent',
];

const pipelinePhases = [
  {
    step: 'STAGE 01',
    name: 'AGENTIC RESEARCH PLANNING',
    desc: '13 specialized agents deliberating on intent, domains, equations & evidence needs...',
    icon: <Users className="w-4 h-4" />,
  },
  {
    step: 'STAGE 02',
    name: 'MULTI-SOURCE SCHOLARLY RETRIEVAL',
    desc: 'Targeted academic search across arXiv, Crossref, OpenAlex, NASA ADS & PubMed...',
    icon: <Search className="w-4 h-4" />,
  },
  {
    step: 'STAGE 03',
    name: 'STRUCTURED EVIDENCE EXTRACTION',
    desc: 'Extracting atomic claims, governing equations, parameters & provenance links...',
    icon: <Cpu className="w-4 h-4" />,
  },
  {
    step: 'STAGE 04',
    name: 'CROSS-DOMAIN KNOWLEDGE COMPOSITION',
    desc: 'Harmonizing variables and physical isomorphisms under Gentner alignment...',
    icon: <Repeat className="w-4 h-4" />,
  },
  {
    step: 'STAGE 05',
    name: 'REASONING, VERIFICATION & MEMORY',
    desc: 'Executing numerical bounds, adversarial audit, and synthesizing evidence monograph...',
    icon: <ShieldCheck className="w-4 h-4" />,
  },
];

export const LoadingView: React.FC = () => {
  const [activeStage, setActiveStage] = useState(0);
  const [activeAgentIdx, setActiveAgentIdx] = useState(0);
  const [secondsElapsed, setSecondsElapsed] = useState(0);

  useEffect(() => {
    const stageTimer = setInterval(() => {
      setActiveStage((prev) => (prev + 1) % pipelinePhases.length);
    }, 1800);

    const agentTimer = setInterval(() => {
      setActiveAgentIdx((prev) => (prev + 1) % agentRoles.length);
    }, 700);

    const clockTimer = setInterval(() => {
      setSecondsElapsed((prev) => prev + 1);
    }, 1000);

    return () => {
      clearInterval(stageTimer);
      clearInterval(agentTimer);
      clearInterval(clockTimer);
    };
  }, []);

  return (
    <div className="flex-1 flex flex-col justify-center items-center p-4 sm:p-8 w-full max-w-3xl mx-auto my-auto select-none">
      {/* Solid Lavender Research Terminal Window */}
      <div className="w-full bg-[#F8F5FC] border-2 border-[#493764] shadow-[6px_6px_0px_#493764] flex flex-col overflow-hidden">
        {/* Lavender Titlebar */}
        <div className="relative h-10 bg-[#EDE5F5] border-b-2 border-[#493764] flex items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-[#7350A0] border border-[#493764]" />
            <div className="w-3 h-3 bg-[#DFD3EE] border border-[#493764]" />
            <span className="font-mono text-xs font-bold tracking-wider text-[#261B36] uppercase ml-1">
              AXION // AUTONOMOUS SCIENTIFIC INVESTIGATION
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 font-mono text-[11px] font-bold text-[#5F4D77] bg-[#DFD3EE] px-2 py-0.5 border border-[#493764]">
              <Clock className="w-3 h-3" />
              {secondsElapsed}s elapsed
            </span>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 sm:p-8 space-y-6">
          {/* Header Status */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#DFD3EE] pb-4">
            <div>
              <div className="flex items-center gap-2 font-mono text-xs font-bold text-[#5F4D77] uppercase tracking-wider mb-1">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#7350A0] opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-[#7350A0]"></span>
                </span>
                COGNITIVE PIPELINE ACTIVE &middot; 13-AGENT ROSTER DELIBERATING
              </div>
              <h2 className="font-mono text-lg sm:text-xl font-bold text-[#261B36]">
                Conducting Multi-Source Literature Investigation...
              </h2>
            </div>

            <div className="flex items-center gap-2 self-start sm:self-auto bg-[#EDE5F5] border border-[#493764] px-3 py-1.5 shadow-[2px_2px_0px_#493764]">
              <Activity className="w-4 h-4 text-[#7350A0] animate-pulse" />
              <div className="text-left font-mono">
                <div className="text-[10px] uppercase font-bold text-[#5F4D77]">Active Agent</div>
                <div className="text-xs font-bold text-[#261B36] truncate max-w-[200px]">
                  {agentRoles[activeAgentIdx]}
                </div>
              </div>
            </div>
          </div>

          {/* Sequential Stage Ledger */}
          <div className="border-2 border-[#493764] bg-[#EDE5F5] divide-y-2 divide-[#493764] text-xs font-mono shadow-[3px_3px_0px_#493764]">
            {pipelinePhases.map((stage, idx) => {
              const isCurrent = idx === activeStage;
              const isDone = idx < activeStage;

              return (
                <div
                  key={stage.step}
                  className={`p-3.5 flex items-start gap-3 transition-colors duration-200 ${
                    isCurrent
                      ? 'bg-[#F8F5FC] text-[#261B36] font-bold'
                      : isDone
                      ? 'text-[#5F4D77] bg-[#EFEAF6]'
                      : 'text-[#5F4D77]/60 bg-[#EDE5F5]'
                  }`}
                >
                  <div
                    className={`mt-0.5 p-1.5 border ${
                      isCurrent
                        ? 'border-[#493764] text-[#FFFFFF] bg-[#7350A0] shadow-[1px_1px_0px_#493764]'
                        : isDone
                        ? 'border-[#493764] text-[#493764] bg-[#DFD3EE]'
                        : 'border-[#493764]/40 text-[#5F4D77]'
                    }`}
                  >
                    {stage.icon}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[11px] tracking-wider uppercase font-bold">
                        {stage.step}: {stage.name}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.2 border ${
                          isCurrent
                            ? 'bg-[#7350A0] text-white border-[#493764]'
                            : isDone
                            ? 'bg-[#DFD3EE] text-[#493764] border-[#493764]'
                            : 'text-[#5F4D77]/60 border-transparent'
                        }`}
                      >
                        {isCurrent ? '[EXECUTING]' : isDone ? '[VERIFIED]' : '[QUEUED]'}
                      </span>
                    </div>
                    <div className="text-[11px] text-[#5F4D77] mt-1 font-normal leading-relaxed">
                      {stage.desc}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Reassurance Footer */}
          <div className="flex flex-col sm:flex-row items-center justify-between text-[11px] font-mono text-[#5F4D77] pt-1 gap-2 border-t border-[#DFD3EE]">
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-[#7350A0]" />
              Querying arXiv, OpenAlex, Crossref, NASA ADS & local verified memory
            </span>
            <span className="font-bold text-[#261B36]">
              NO HALLUCINATIONS &middot; TRACEABLE PROVENANCE
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
