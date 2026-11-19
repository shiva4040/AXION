import React, { useEffect, useState } from 'react';
import { Compass, Cpu, GitBranch, Repeat, ShieldCheck } from 'lucide-react';

const pipelineStages = [
  {
    step: 'STAGE 01',
    name: 'DOMAIN DISCOVERY & EVIDENCE RETRIEVAL',
    desc: 'Querying vector index & parsing verified literature chunks...',
    icon: <Compass className="w-3.5 h-3.5" />,
  },
  {
    step: 'STAGE 02',
    name: 'ONTOLOGY & DIMENSIONAL TRAVERSAL',
    desc: 'Verifying SI dimensional consistency across concept relations...',
    icon: <Cpu className="w-3.5 h-3.5" />,
  },
  {
    step: 'STAGE 03',
    name: 'REASONING DAG & CONTRADICTION AUDIT',
    desc: 'Formulating step-by-step dependency graph & scanning conflicts...',
    icon: <GitBranch className="w-3.5 h-3.5" />,
  },
  {
    step: 'STAGE 04',
    name: 'STRUCTURAL ANALOGICAL MAPPING',
    desc: 'Projecting relational schema under Gentner constraints & applicability guard...',
    icon: <Repeat className="w-3.5 h-3.5" />,
  },
  {
    step: 'STAGE 05',
    name: 'EMPIRICAL CONVERGENCE & TIER PROMOTION',
    desc: 'Executing sandbox equations and synthesizing research monograph...',
    icon: <ShieldCheck className="w-3.5 h-3.5" />,
  },
];

export const LoadingView: React.FC = () => {
  const [activeStage, setActiveStage] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStage((prev) => (prev + 1) % pipelineStages.length);
    }, 850);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex-1 flex flex-col justify-center items-center p-6 sm:p-12 w-full max-w-2xl mx-auto my-auto select-none">
      {/* Retro Terminal Window */}
      <div className="w-full bg-[#F9F3E6] border-2 border-[#29251F] shadow-[4px_4px_0px_#29251F] flex flex-col overflow-hidden">
        {/* Pinstripe Titlebar */}
        <div className="relative h-[29px] bg-[#F3EBD8] border-b-[1.5px] border-[#29251F] flex items-center justify-between px-2.5">
          <div
            className="absolute inset-0 pointer-events-none opacity-85"
            style={{
              background:
                'repeating-linear-gradient(to bottom, transparent 0px, transparent 2px, #29251F 2px, #29251F 3px)',
            }}
          />
          <div className="relative z-10 w-[14px] h-[14px] bg-[#F9F3E6] border-[1.5px] border-[#29251F] flex items-center justify-center">
            <span className="w-2 h-[1px] bg-[#29251F]" />
          </div>
          <div className="relative z-10 px-3 py-0.5 bg-[#F9F3E6] border-[1.5px] border-[#29251F] font-mono text-[11px] font-bold tracking-wider text-[#211E19] uppercase">
            CALIBRATING_PIPELINE.EXE
          </div>
          <div className="relative z-10 w-[14px] h-[14px] opacity-0" />
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-5">
          <div className="space-y-1">
            <div className="font-mono text-[11px] font-bold text-[#70695D] uppercase tracking-wider">
              AXION INFERENCE IN PROGRESS
            </div>
            <h2 className="font-mono text-lg font-bold text-[#211E19]">
              Synthesizing Cross-Domain Solution...
            </h2>
          </div>

          {/* Sequential Stage Ledger */}
          <div className="border border-[#29251F] bg-[#F3EBD8] divide-y divide-[#29251F] text-xs font-mono">
            {pipelineStages.map((stage, idx) => {
              const isCurrent = idx === activeStage;
              const isDone = idx < activeStage;

              return (
                <div
                  key={stage.step}
                  className={`p-3 flex items-start gap-3 transition-none ${
                    isCurrent
                      ? 'bg-[#F9F3E6] text-[#211E19] font-bold'
                      : isDone
                      ? 'text-[#70695D] bg-[#DFD4B8]/40'
                      : 'text-[#70695D]/50'
                  }`}
                >
                  <div
                    className={`mt-0.5 p-1 border ${
                      isCurrent
                        ? 'border-[#29251F] text-[#211E19] bg-[#F3EBD8]'
                        : isDone
                        ? 'border-[#347C70] text-[#347C70] bg-[#EAF4F3]'
                        : 'border-[#29251F]/40 text-[#70695D]'
                    }`}
                  >
                    {stage.icon}
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] tracking-wider uppercase">
                        {stage.step}: {stage.name}
                      </span>
                      <span className="text-[9px] font-bold">
                        {isCurrent ? '[EXECUTING]' : isDone ? '[VERIFIED]' : '[QUEUED]'}
                      </span>
                    </div>
                    <div className="text-[11px] text-[#70695D] mt-0.5 font-normal">
                      {stage.desc}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex items-center justify-between text-[10px] font-mono text-[#70695D] pt-1">
            <span>DETERMINISTIC REASONING (T=0.0)</span>
            <span>TIMEOUT: 15.0s</span>
          </div>
        </div>
      </div>
    </div>
  );
};
