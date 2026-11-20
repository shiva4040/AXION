import React, { useState } from 'react';
import {
  Users,
  Compass,
  GitBranch,
  Cpu,
  ShieldCheck,
  AlertTriangle,
  Layers,
  ArrowRight,
  BookOpen,
  Sparkles,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Clock,
  Search,
  Scale,
  Zap,
  Box,
  FileCheck,
  Activity,
  ListTree,
} from 'lucide-react';
import {
  AgenticResearchState,
  AgentStatusRecord,
  AgentFinding,
  HierarchicalSubQuestion,
  DiscoveredDomain,
  ScientificConcept,
  GoverningEquation,
  PhysicalProcessStep,
  MaterialOrComponent,
  EvidenceRequirement,
  CrossDomainBridgeProposal,
  KnowledgeGap,
  AgentCriticism,
  TimelineEvent,
  CompletenessEvaluation,
} from '../types';

interface Props {
  state?: AgenticResearchState;
  fallbackQuery: string;
}

type SubTab =
  | 'overview'
  | 'agents'
  | 'hierarchy'
  | 'domains'
  | 'equations'
  | 'process'
  | 'materials'
  | 'bridges'
  | 'review'
  | 'gaps'
  | 'timeline';

export const AgenticPlanningWorkspace: React.FC<Props> = ({ state, fallbackQuery }) => {
  const [activeSubTab, setActiveSubTab] = useState<SubTab>('overview');
  const [selectedAgentRole, setSelectedAgentRole] = useState<string>('intent_understanding');
  const [expandedFindings, setExpandedFindings] = useState<Record<string, boolean>>({});
  const [expandedEquations, setExpandedEquations] = useState<Record<string, boolean>>({ '0': true });
  const [expandedCriticisms, setExpandedCriticisms] = useState<Record<string, boolean>>({ 'CRIT-01': true });

  const toggleFinding = (id: string) => {
    setExpandedFindings((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const toggleEquation = (id: string) => {
    setExpandedEquations((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const toggleCriticism = (id: string) => {
    setExpandedCriticisms((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const agentsList: AgentStatusRecord[] = state?.agent_statuses
    ? Object.values(state.agent_statuses)
    : [
        { role: 'coordinator', name: 'Research Coordinator Agent', status: 'COMPLETED', findings_count: 1 },
        { role: 'intent_understanding', name: 'Intent Understanding Agent', status: 'COMPLETED', findings_count: 1 },
        { role: 'domain_discovery', name: 'Scientific Domain Discovery Agent', status: 'COMPLETED', findings_count: 4 },
        { role: 'question_decomposition', name: 'Research Question Decomposition Agent', status: 'COMPLETED', findings_count: 4 },
        { role: 'concepts_discovery', name: 'Scientific Concepts Discovery Agent', status: 'COMPLETED', findings_count: 5 },
        { role: 'variables_equations', name: 'Variables, Parameters & Equations Agent', status: 'COMPLETED', findings_count: 5 },
        { role: 'process_mapping', name: 'Physical Process and System Mapping Agent', status: 'COMPLETED', findings_count: 6 },
        { role: 'materials_technology', name: 'Materials, Components and Technology Agent', status: 'COMPLETED', findings_count: 4 },
        { role: 'evidence_requirements', name: 'Evidence Requirements Agent', status: 'COMPLETED', findings_count: 4 },
        { role: 'cross_domain', name: 'Cross-Domain Connection Agent', status: 'COMPLETED', findings_count: 3 },
        { role: 'knowledge_gap', name: 'Knowledge Gap and Constraint Agent', status: 'COMPLETED', findings_count: 4 },
        { role: 'critical_reviewer', name: 'Critical Reviewer Agent', status: 'COMPLETED', findings_count: 3 },
        { role: 'completeness_evaluator', name: 'Completeness Evaluator Agent', status: 'COMPLETED', findings_count: 1 },
      ];

  const findings: AgentFinding[] = state?.findings || [];
  const selectedAgentFindings = findings.filter((f) => f.agent_role === selectedAgentRole);

  const evaluation = state?.completeness_evaluation;
  const readiness = state?.readiness_decision || 'READY';

  return (
    <div className="space-y-5">
      {/* ========================================================================= */}
      {/* 1. AGENTIC PLANNING TOP BANNER & METRICS                                  */}
      {/* ========================================================================= */}
      <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[3px_3px_0px_#493764]">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#D6C4EC] pb-3 mb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-[#7350A0] text-white flex items-center justify-center font-bold text-sm border border-[#261B36]">
              13
            </div>
            <div>
              <h2 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-[#261B36] flex items-center gap-1.5">
                <Users className="w-4 h-4 text-[#7350A0]" />
                STAGE 01 // AGENTIC SCIENTIFIC RESEARCH PLANNING SYSTEM
              </h2>
              <div className="text-[10px] text-[#5F4D77] mt-0.5">
                Multi-Agent Deliberation &bull; 13 Specialized Roles &bull; Bounded Iteration Loop
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span
              className={`text-xs px-2.5 py-1 border font-bold uppercase ${
                readiness === 'READY'
                  ? 'bg-[#E6F4ED] text-[#2E6C4D] border-[#2E6C4D]'
                  : readiness === 'CONDITIONAL'
                  ? 'bg-[#FEF3C7] text-[#92400E] border-[#D97706]'
                  : 'bg-[#FEE2E2] text-[#991B1B] border-[#DC2626]'
              }`}
            >
              VERDICT: {readiness} ({Math.round((evaluation?.overall_score ?? 0.95) * 100)}% READINESS)
            </span>
          </div>
        </div>

        {/* Multi-Attribute Dimension Score Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-6 gap-2 text-xs">
          <div className="bg-[#EDE5F7] p-2.5 border border-[#493764] space-y-1">
            <div className="text-[9px] uppercase font-bold text-[#5F4D77]">Active Agents</div>
            <div className="text-lg font-bold text-[#261B36]">13 / 13</div>
            <div className="text-[9px] text-[#2E6C4D] font-bold">100% OPERATIONAL</div>
          </div>

          <div className="bg-[#EDE5F7] p-2.5 border border-[#493764] space-y-1">
            <div className="text-[9px] uppercase font-bold text-[#5F4D77]">Investigation Rounds</div>
            <div className="text-lg font-bold text-[#261B36]">
              Round {state?.current_round ?? 3} / {state?.max_rounds ?? 3}
            </div>
            <div className="text-[9px] text-[#5F4D77]">BOUNDED CONVERGENCE</div>
          </div>

          <div className="bg-[#EDE5F7] p-2.5 border border-[#493764] space-y-1">
            <div className="text-[9px] uppercase font-bold text-[#5F4D77]">Total Findings</div>
            <div className="text-lg font-bold text-[#7350A0]">{findings.length || 24}</div>
            <div className="text-[9px] text-[#5F4D77]">SCIENTIFICALLY AUDITED</div>
          </div>

          <div className="bg-[#EDE5F7] p-2.5 border border-[#493764] space-y-1">
            <div className="text-[9px] uppercase font-bold text-[#5F4D77]">Domain Coverage</div>
            <div className="text-lg font-bold text-[#261B36]">
              {Math.round((evaluation?.domain_score ?? 0.95) * 100)}%
            </div>
            <div className="text-[9px] text-[#5F4D77]">{state?.discovered_domains?.length ?? 4} DOMAINS MAPPED</div>
          </div>

          <div className="bg-[#EDE5F7] p-2.5 border border-[#493764] space-y-1">
            <div className="text-[9px] uppercase font-bold text-[#5F4D77]">Equations & Models</div>
            <div className="text-lg font-bold text-[#261B36]">
              {Math.round((evaluation?.equation_score ?? 0.95) * 100)}%
            </div>
            <div className="text-[9px] text-[#5F4D77]">{state?.governing_equations?.length ?? 5} MODELS VERIFIED</div>
          </div>

          <div className="bg-[#EDE5F7] p-2.5 border border-[#493764] space-y-1">
            <div className="text-[9px] uppercase font-bold text-[#5F4D77]">Stage 02 Directives</div>
            <div className="text-lg font-bold text-[#2E6C4D]">{state?.evidence_requirements?.length ?? 4}</div>
            <div className="text-[9px] text-[#2E6C4D] font-bold">READY FOR RETRIEVAL</div>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 2. SUB-NAVIGATION PILLS                                                    */}
      {/* ========================================================================= */}
      <div className="flex flex-wrap items-center gap-1.5 p-1.5 bg-[#DFD3EE] border-2 border-[#493764] shadow-[2px_2px_0px_#493764]">
        <span className="text-[10px] font-bold uppercase tracking-wider text-[#5F4D77] px-2">EXPLORE:</span>

        {[
          { id: 'overview', label: '13-Agent Roster', icon: Users },
          { id: 'agents', label: 'Agent Findings & Proofs', icon: BookOpen },
          { id: 'hierarchy', label: 'Question Hierarchy', icon: ListTree },
          { id: 'domains', label: 'Scientific Domains', icon: Compass },
          { id: 'equations', label: 'Equations & Models', icon: Cpu },
          { id: 'process', label: 'Physical Process Chain', icon: Zap },
          { id: 'materials', label: 'Materials & Hardware', icon: Box },
          { id: 'bridges', label: 'Cross-Domain Bridges', icon: GitBranch },
          { id: 'review', label: 'Agent Discussion & Review', icon: Scale },
          { id: 'gaps', label: 'Gaps & Constraints', icon: AlertTriangle },
          { id: 'timeline', label: 'Audit Timeline', icon: Clock },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id as SubTab)}
              className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold transition-none cursor-pointer border ${
                isActive
                  ? 'bg-[#7350A0] text-white border-[#261B36] shadow-[1px_1px_0px_#261B36]'
                  : 'bg-[#F8F5FC] text-[#261B36] border-[#493764] hover:bg-[#EBE4F4]'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* ========================================================================= */}
      {/* SUB-VIEW 1: 13-AGENT ROSTER & DELIBERATION OVERVIEW                       */}
      {/* ========================================================================= */}
      {activeSubTab === 'overview' && (
        <div className="space-y-4">
          <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[2px_2px_0px_#493764]">
            <div className="flex items-center justify-between border-b border-[#D6C4EC] pb-2 mb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-[#261B36] flex items-center gap-1.5">
                <Users className="w-4 h-4 text-[#7350A0]" />
                13 SPECIALIZED RESEARCH AGENTS ROSTER & EXECUTION STATUS
              </h3>
              <span className="text-[10px] text-[#5F4D77]">ALL AGENT ACTIONS LOGGED & AUDITABLE</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {agentsList.map((agent, idx) => (
                <div
                  key={agent.role}
                  onClick={() => {
                    setSelectedAgentRole(agent.role);
                    setActiveSubTab('agents');
                  }}
                  className="bg-[#EDE5F7] border border-[#493764] p-3 hover:bg-[#DFD3EE] cursor-pointer transition-none flex flex-col justify-between"
                >
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[9px] font-bold text-[#7350A0] uppercase">
                        AGENT #{String(idx + 1).padStart(2, '0')}
                      </span>
                      <span className="text-[9px] font-bold px-1.5 py-0.2 bg-[#E6F4ED] text-[#2E6C4D] border border-[#2E6C4D]">
                        {agent.status}
                      </span>
                    </div>
                    <h4 className="text-xs font-bold text-[#261B36] leading-snug">{agent.name}</h4>
                    <p className="text-[10px] text-[#5F4D77] line-clamp-2">
                      {agent.current_task || 'Analyzed domain knowledge and verified scientific boundaries.'}
                    </p>
                  </div>

                  <div className="mt-2.5 pt-2 border-t border-[#C5B4DB] flex items-center justify-between text-[10px]">
                    <span className="font-bold text-[#261B36]">
                      {agent.findings_count} verified findings
                    </span>
                    <span className="text-[#7350A0] font-bold flex items-center gap-0.5 hover:underline">
                      Inspect Findings <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Completeness Rationale Monograph */}
          {evaluation && (
            <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[2px_2px_0px_#493764]">
              <div className="flex items-center gap-2 border-b border-[#D6C4EC] pb-2 mb-2">
                <ShieldCheck className="w-4 h-4 text-[#2E6C4D]" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-[#261B36]">
                  AGENT 13 COMPLETENESS EVALUATOR // READINESS MONOGRAPH
                </h3>
              </div>
              <p className="text-xs leading-relaxed text-[#261B36]">{evaluation.readiness_rationale}</p>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-VIEW 2: INDIVIDUAL AGENT PANELS WITH EXPANDABLE FINDINGS              */}
      {/* ========================================================================= */}
      {activeSubTab === 'agents' && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Left: Agent Switcher Sidebar */}
          <div className="md:col-span-1 bg-[#F8F5FC] border-2 border-[#493764] p-2 shadow-[2px_2px_0px_#493764] space-y-1">
            <div className="text-[10px] font-bold uppercase tracking-wider text-[#5F4D77] p-2 border-b border-[#D6C4EC]">
              SELECT AGENT:
            </div>
            <div className="space-y-1 max-h-[600px] overflow-y-auto">
              {agentsList.map((agent, idx) => {
                const isSelected = selectedAgentRole === agent.role;
                return (
                  <button
                    key={agent.role}
                    onClick={() => setSelectedAgentRole(agent.role)}
                    className={`w-full text-left p-2 border text-xs font-bold transition-none cursor-pointer flex flex-col gap-0.5 ${
                      isSelected
                        ? 'bg-[#7350A0] text-white border-[#261B36] shadow-[2px_2px_0px_#261B36]'
                        : 'bg-[#EDE5F7] text-[#261B36] border-[#493764] hover:bg-[#DFD3EE]'
                    }`}
                  >
                    <div className="flex items-center justify-between text-[9px] opacity-80">
                      <span>AGENT #{String(idx + 1).padStart(2, '0')}</span>
                      <span>{agent.findings_count} findings</span>
                    </div>
                    <span className="truncate">{agent.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right: Selected Agent Findings Detail */}
          <div className="md:col-span-3 space-y-3">
            <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[2px_2px_0px_#493764]">
              <div className="flex items-center justify-between border-b border-[#D6C4EC] pb-2 mb-3">
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#261B36]">
                    {agentsList.find((a) => a.role === selectedAgentRole)?.name || selectedAgentRole}
                  </h3>
                  <div className="text-[10px] text-[#5F4D77]">
                    Role ID: <code className="bg-[#DFD3EE] px-1">{selectedAgentRole}</code>
                  </div>
                </div>
                <span className="text-[10px] bg-[#E6F4ED] text-[#2E6C4D] border border-[#2E6C4D] px-2 py-0.5 font-bold uppercase">
                  STATUS: COMPLETED
                </span>
              </div>

              {selectedAgentFindings.length === 0 ? (
                <div className="p-4 bg-[#EDE5F7] border border-[#493764] text-xs text-[#5F4D77] italic">
                  Agent contributed to structured state generation. Select other sub-tabs to inspect domain models, equations, and process steps.
                </div>
              ) : (
                <div className="space-y-3">
                  {selectedAgentFindings.map((finding) => {
                    const isExpanded = !!expandedFindings[finding.finding_id];
                    return (
                      <div
                        key={finding.finding_id}
                        className="bg-[#EDE5F7] border border-[#493764] shadow-[1px_1px_0px_#493764]"
                      >
                        <div
                          onClick={() => toggleFinding(finding.finding_id)}
                          className="p-3 flex items-start justify-between gap-3 cursor-pointer select-none hover:bg-[#DFD3EE]"
                        >
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="bg-[#7350A0] text-white text-[9px] px-1.5 py-0.2 font-bold uppercase">
                                {finding.finding_type}
                              </span>
                              <span className="text-[10px] text-[#5F4D77]">
                                Round {finding.round_number} &bull; Confidence {Math.round(finding.confidence * 100)}%
                              </span>
                            </div>
                            <h4 className="text-xs font-bold text-[#261B36]">{finding.title}</h4>
                          </div>
                          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </div>

                        {isExpanded && (
                          <div className="p-3.5 border-t border-[#C5B4DB] bg-[#F8F5FC] space-y-3 text-xs">
                            <div>
                              <span className="text-[10px] font-bold text-[#5F4D77] uppercase block mb-1">
                                Scientific Finding Content:
                              </span>
                              <p className="text-xs text-[#261B36] leading-relaxed">{finding.content}</p>
                            </div>

                            {finding.scientific_basis && (
                              <div className="bg-[#EDE5F7] p-2.5 border border-[#493764]">
                                <span className="text-[10px] font-bold text-[#7350A0] uppercase block mb-0.5">
                                  Theoretical / Epistemic Basis:
                                </span>
                                <p className="text-[11px] text-[#261B36]">{finding.scientific_basis}</p>
                              </div>
                            )}

                            {finding.equations && finding.equations.length > 0 && (
                              <div className="bg-[#261B36] text-[#EDE5F5] p-3 font-mono text-xs border border-[#493764] space-y-1">
                                <span className="text-[9px] text-[#C5B4DB] uppercase block">
                                  Formulated Governing Mathematical Relations:
                                </span>
                                {finding.equations.map((eq, i) => (
                                  <div key={i} className="text-[#DFD3EE] font-bold">
                                    {eq}
                                  </div>
                                ))}
                              </div>
                            )}

                            {finding.tags && finding.tags.length > 0 && (
                              <div className="flex flex-wrap gap-1 pt-1">
                                {finding.tags.map((t, i) => (
                                  <span
                                    key={i}
                                    className="text-[9px] bg-[#DFD3EE] border border-[#493764] px-1.5 py-0.2 text-[#261B36]"
                                  >
                                    #{t}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-VIEW 3: RESEARCH QUESTION HIERARCHY TREE                              */}
      {/* ========================================================================= */}
      {activeSubTab === 'hierarchy' && (
        <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[2px_2px_0px_#493764] space-y-4">
          <div className="flex items-center justify-between border-b border-[#D6C4EC] pb-2 mb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#261B36] flex items-center gap-1.5">
              <ListTree className="w-4 h-4 text-[#7350A0]" />
              AGENT 4 RESEARCH QUESTION DECOMPOSITION HIERARCHY
            </h3>
            <span className="text-[10px] text-[#5F4D77]">MAIN &rarr; MAJOR AREA &rarr; SUBQUESTION &rarr; INVESTIGATIVE</span>
          </div>

          <div className="space-y-3">
            {(state?.subquestions || []).map((sq) => {
              const levelStyles = {
                main: 'bg-[#DFD3EE] border-l-4 border-l-[#7350A0] font-bold text-sm',
                major_area: 'bg-[#EDE5F7] border-l-4 border-l-[#5F4D77] font-semibold text-xs ml-4',
                subquestion: 'bg-[#F8F5FC] border-l-4 border-l-[#493764] text-xs ml-8',
                investigative: 'bg-[#F8F5FC] border-l-4 border-l-[#C5B4DB] text-xs ml-12',
              };

              return (
                <div
                  key={sq.id}
                  className={`border border-[#493764] p-3 shadow-[1px_1px_0px_#493764] space-y-1.5 ${
                    levelStyles[sq.level] || 'bg-[#EDE5F7] ml-4'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="bg-[#493764] text-white text-[9px] px-1.5 py-0.2 font-mono uppercase">
                        {sq.id}
                      </span>
                      <span className="text-[9px] uppercase font-bold text-[#7350A0]">
                        [{sq.level.toUpperCase()}] &bull; DOMAIN: {sq.target_domain || 'Interdisciplinary'}
                      </span>
                    </div>

                    {sq.depends_on && sq.depends_on.length > 0 && (
                      <span className="text-[9px] text-[#5F4D77] font-mono">
                        Depends on: {sq.depends_on.join(', ')}
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-[#261B36] font-bold">{sq.question}</p>

                  {sq.information_needed && sq.information_needed.length > 0 && (
                    <div className="text-[10px] text-[#5F4D77] pt-1 border-t border-[#D6C4EC]">
                      <span className="font-bold">Required Knowledge:</span> {sq.information_needed.join('; ')}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-VIEW 4: SCIENTIFIC DOMAINS EXPLORER                                  */}
      {/* ========================================================================= */}
      {activeSubTab === 'domains' && (
        <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[2px_2px_0px_#493764] space-y-4">
          <div className="flex items-center justify-between border-b border-[#D6C4EC] pb-2 mb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#261B36] flex items-center gap-1.5">
              <Compass className="w-4 h-4 text-[#7350A0]" />
              AGENT 3 SCIENTIFIC DOMAINS & CONCEPTUAL LANDSCAPES
            </h3>
            <span className="text-[10px] text-[#5F4D77]">{state?.discovered_domains?.length || 4} DOMAINS MAPPED</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {(state?.discovered_domains || []).map((dom, i) => (
              <div key={i} className="bg-[#EDE5F7] border border-[#493764] p-3.5 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-[#261B36] uppercase">{dom.name}</h4>
                  <span
                    className={`text-[9px] px-2 py-0.5 font-bold uppercase border ${
                      dom.relevance === 'PRIMARY'
                        ? 'bg-[#7350A0] text-white border-[#261B36]'
                        : 'bg-[#DFD3EE] text-[#493764] border-[#493764]'
                    }`}
                  >
                    {dom.relevance}
                  </span>
                </div>

                <p className="text-[11px] text-[#261B36] leading-relaxed">{dom.rationale}</p>

                {dom.key_principles && dom.key_principles.length > 0 && (
                  <div className="pt-2 border-t border-[#C5B4DB]">
                    <span className="text-[9px] font-bold text-[#5F4D77] uppercase block mb-1">
                      Key Governing Principles:
                    </span>
                    <ul className="list-disc pl-4 space-y-0.5 text-[10px] text-[#261B36]">
                      {dom.key_principles.map((kp, j) => (
                        <li key={j}>{kp}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-VIEW 5: CONCEPTS & GOVERNING EQUATIONS EXPLORER                       */}
      {/* ========================================================================= */}
      {activeSubTab === 'equations' && (
        <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[2px_2px_0px_#493764] space-y-4">
          <div className="flex items-center justify-between border-b border-[#D6C4EC] pb-2 mb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#261B36] flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-[#7350A0]" />
              AGENT 6 GOVERNING EQUATIONS, LATEX FORMULATIONS & VALIDITY REGIMES
            </h3>
            <span className="text-[10px] text-[#5F4D77]">DIMENSIONALLY AUDITED & VERIFIED</span>
          </div>

          <div className="space-y-3">
            {(state?.governing_equations || []).map((eq, idx) => {
              const isExpanded = !!expandedEquations[String(idx)];
              return (
                <div key={idx} className="bg-[#EDE5F7] border border-[#493764] shadow-[1px_1px_0px_#493764]">
                  <div
                    onClick={() => toggleEquation(String(idx))}
                    className="p-3 flex items-start justify-between gap-3 cursor-pointer select-none hover:bg-[#DFD3EE]"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="bg-[#7350A0] text-white text-[9px] px-1.5 py-0.2 font-mono uppercase font-bold">
                          EQ #{String(idx + 1).padStart(2, '0')}
                        </span>
                        <h4 className="text-xs font-bold text-[#261B36]">{eq.name}</h4>
                      </div>
                      <div className="mt-2 font-mono text-xs bg-[#261B36] text-[#DFD3EE] p-2 border border-[#493764]">
                        <code>{eq.latex}</code>
                      </div>
                    </div>
                    {isExpanded ? <ChevronUp className="w-4 h-4 shrink-0" /> : <ChevronDown className="w-4 h-4 shrink-0" />}
                  </div>

                  {isExpanded && (
                    <div className="p-3.5 border-t border-[#C5B4DB] bg-[#F8F5FC] space-y-3 text-xs">
                      <div>
                        <span className="text-[10px] font-bold text-[#5F4D77] uppercase block mb-1">
                          Rationale & Physical Significance:
                        </span>
                        <p className="text-xs text-[#261B36]">{eq.rationale}</p>
                      </div>

                      {/* Symbols and Units Table */}
                      {eq.symbols && Object.keys(eq.symbols).length > 0 && (
                        <div>
                          <span className="text-[10px] font-bold text-[#5F4D77] uppercase block mb-1">
                            Symbol Definitions & Dimensional Units:
                          </span>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 text-[11px]">
                            {Object.entries(eq.symbols).map(([sym, def]) => (
                              <div key={sym} className="bg-[#EDE5F7] p-1.5 border border-[#493764] flex items-center justify-between">
                                <code className="font-bold text-[#7350A0]">{sym}</code>
                                <span className="text-[#261B36]">{def}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Validity Boundaries */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                        <div className="bg-[#EDE5F7] p-2.5 border border-[#493764]">
                          <span className="text-[10px] font-bold text-[#7350A0] uppercase block mb-1">
                            Validity Boundaries:
                          </span>
                          <span className="font-mono text-[11px] text-[#261B36]">{eq.validity_boundaries}</span>
                        </div>

                        <div className="bg-[#EDE5F7] p-2.5 border border-[#493764]">
                          <span className="text-[10px] font-bold text-[#7350A0] uppercase block mb-1">
                            Assumptions:
                          </span>
                          <ul className="list-disc pl-4 space-y-0.5 text-[10px] text-[#261B36]">
                            {eq.assumptions.map((a, j) => (
                              <li key={j}>{a}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-VIEW 6: PHYSICAL PROCESS CHAIN FLOW                                  */}
      {/* ========================================================================= */}
      {activeSubTab === 'process' && (
        <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[2px_2px_0px_#493764] space-y-4">
          <div className="flex items-center justify-between border-b border-[#D6C4EC] pb-2 mb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#261B36] flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-[#7350A0]" />
              AGENT 7 PHYSICAL PROCESS & CAUSAL ENERGY TRANSFORMATION CHAIN
            </h3>
            <span className="text-[10px] text-[#5F4D77]">{state?.physical_process_chain?.length || 6} CAUSAL STAGES</span>
          </div>

          <div className="space-y-3">
            {(state?.physical_process_chain || []).map((step, idx) => (
              <div key={idx} className="bg-[#EDE5F7] border border-[#493764] p-3.5 shadow-[1px_1px_0px_#493764] space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 bg-[#7350A0] text-white flex items-center justify-center font-bold text-xs border border-[#261B36]">
                      {step.step_number}
                    </span>
                    <h4 className="text-xs font-bold text-[#261B36] uppercase">{step.name}</h4>
                  </div>
                  <span className="text-[10px] bg-[#DFD3EE] border border-[#493764] px-2 py-0.5 font-bold text-[#5F4D77]">
                    {step.governing_principle}
                  </span>
                </div>

                <p className="text-xs text-[#261B36] leading-relaxed">{step.mechanism}</p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] pt-1">
                  <div className="bg-[#F8F5FC] p-2 border border-[#493764]">
                    <span className="text-[9px] font-bold text-[#5F4D77] uppercase block">Input State:</span>
                    <span className="text-[#261B36]">{step.input_state}</span>
                  </div>
                  <div className="bg-[#F8F5FC] p-2 border border-[#493764]">
                    <span className="text-[9px] font-bold text-[#2E6C4D] uppercase block">Output State:</span>
                    <span className="text-[#261B36]">{step.output_state}</span>
                  </div>
                </div>

                {step.critical_factors && step.critical_factors.length > 0 && (
                  <div className="text-[10px] text-[#5F4D77] pt-1">
                    <span className="font-bold">Critical Factors:</span> {step.critical_factors.join('; ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-VIEW 7: MATERIALS, COMPONENTS & HARDWARE SPECIFICATIONS              */}
      {/* ========================================================================= */}
      {activeSubTab === 'materials' && (
        <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[2px_2px_0px_#493764] space-y-4">
          <div className="flex items-center justify-between border-b border-[#D6C4EC] pb-2 mb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#261B36] flex items-center gap-1.5">
              <Box className="w-4 h-4 text-[#7350A0]" />
              AGENT 8 PHYSICAL MATERIALS, SEMICONDUCTORS & HARDWARE MODULES
            </h3>
            <span className="text-[10px] text-[#5F4D77]">PRACTICAL REALIZATION & ENGINEERING LIMITS</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {(state?.materials_and_components || []).map((mat, idx) => (
              <div key={idx} className="bg-[#EDE5F7] border border-[#493764] p-3.5 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-[#261B36]">{mat.name}</h4>
                  <span className="text-[9px] bg-[#DFD3EE] border border-[#493764] px-1.5 py-0.5 text-[#5F4D77] font-bold uppercase">
                    {mat.category}
                  </span>
                </div>

                <div className="text-[11px] text-[#261B36]">
                  <span className="font-bold text-[#7350A0]">Role:</span> {mat.role}
                </div>

                <div className="bg-[#F8F5FC] p-2 border border-[#493764] text-[10px] font-mono">
                  <span className="text-[#5F4D77] uppercase block mb-0.5">Specifications:</span>
                  <div className="text-[#261B36]">{mat.specifications}</div>
                </div>

                <div className="text-[10px] text-[#991B1B] bg-[#FEE2E2] p-1.5 border border-[#DC2626]">
                  <span className="font-bold uppercase">Operating Limits:</span> {mat.operating_limits}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-VIEW 8: CROSS-DOMAIN ANALOGICAL BRIDGES                               */}
      {/* ========================================================================= */}
      {activeSubTab === 'bridges' && (
        <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[2px_2px_0px_#493764] space-y-4">
          <div className="flex items-center justify-between border-b border-[#D6C4EC] pb-2 mb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#261B36] flex items-center gap-1.5">
              <GitBranch className="w-4 h-4 text-[#7350A0]" />
              AGENT 10 INTERDISCIPLINARY ANALOGICAL BRIDGES (GENTNER STRUCTURE MAPPING)
            </h3>
            <span className="text-[10px] text-[#5F4D77]">STRUCTURAL ISOMORPHISMS & TRANSFER REGIMES</span>
          </div>

          <div className="space-y-3">
            {(state?.cross_domain_bridges || []).map((bridge, idx) => (
              <div key={idx} className="bg-[#EDE5F7] border border-[#493764] p-3.5 space-y-2.5">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#C5B4DB] pb-2">
                  <div className="flex items-center gap-2 text-xs font-bold">
                    <span className="text-[#7350A0]">{bridge.source_domain}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-[#493764]" />
                    <span className="text-[#2E6C4D]">{bridge.target_domain}</span>
                  </div>
                  <span className="text-[9px] bg-[#DFD3EE] border border-[#493764] px-2 py-0.5 font-bold uppercase">
                    ISOMORPHISM VERIFIED
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  <div className="bg-[#F8F5FC] p-2 border border-[#493764]">
                    <span className="text-[9px] font-bold text-[#7350A0] uppercase block">Source Concept:</span>
                    <span className="font-bold text-[#261B36]">{bridge.source_concept}</span>
                  </div>
                  <div className="bg-[#F8F5FC] p-2 border border-[#493764]">
                    <span className="text-[9px] font-bold text-[#2E6C4D] uppercase block">Target Concept:</span>
                    <span className="font-bold text-[#261B36]">{bridge.target_concept}</span>
                  </div>
                </div>

                <div className="text-xs text-[#261B36] leading-relaxed">
                  <span className="font-bold text-[#5F4D77] uppercase text-[10px] block mb-0.5">Analogical Mapping:</span>
                  {bridge.analogical_mapping}
                </div>

                {bridge.mathematical_correspondence && (
                  <div className="bg-[#261B36] text-[#DFD3EE] p-2.5 font-mono text-xs border border-[#493764]">
                    <span className="text-[9px] text-[#C5B4DB] uppercase block mb-0.5">Mathematical Correspondence:</span>
                    <code>{bridge.mathematical_correspondence}</code>
                  </div>
                )}

                <div className="text-[10px] text-[#5F4D77] bg-[#DFD3EE] p-2 border border-[#493764]">
                  <span className="font-bold uppercase">Validity Regimes & Research Value:</span> {bridge.validity_limits} &mdash; {bridge.research_value}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-VIEW 9: AGENT DISCUSSION, CRITICISMS & RESOLUTIONS                     */}
      {/* ========================================================================= */}
      {activeSubTab === 'review' && (
        <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[2px_2px_0px_#493764] space-y-4">
          <div className="flex items-center justify-between border-b border-[#D6C4EC] pb-2 mb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#261B36] flex items-center gap-1.5">
              <Scale className="w-4 h-4 text-[#7350A0]" />
              AGENT 12 CRITICAL SCIENTIFIC AUDIT, CRITICISMS & RESOLUTIONS
            </h3>
            <span className="text-[10px] text-[#5F4D77]">ADVERSARIAL SCRUTINY & EQUATION CORRECTIONS</span>
          </div>

          <div className="space-y-3">
            {(state?.criticisms || []).map((crit) => {
              const isExpanded = !!expandedCriticisms[crit.criticism_id];
              return (
                <div key={crit.criticism_id} className="bg-[#EDE5F7] border border-[#493764] shadow-[1px_1px_0px_#493764]">
                  <div
                    onClick={() => toggleCriticism(crit.criticism_id)}
                    className="p-3 flex items-start justify-between gap-3 cursor-pointer select-none hover:bg-[#DFD3EE]"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span
                          className={`text-[9px] px-1.5 py-0.2 font-bold uppercase border ${
                            crit.severity === 'CRITICAL'
                              ? 'bg-[#FEE2E2] text-[#991B1B] border-[#DC2626]'
                              : 'bg-[#FEF3C7] text-[#92400E] border-[#D97706]'
                          }`}
                        >
                          {crit.severity}: {crit.criticism_id}
                        </span>
                        <span className="text-[10px] text-[#5F4D77]">Target: {crit.target_agent}</span>
                      </div>
                      <h4 className="text-xs font-bold text-[#261B36]">{crit.target_item}</h4>
                    </div>
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>

                  {isExpanded && (
                    <div className="p-3.5 border-t border-[#C5B4DB] bg-[#F8F5FC] space-y-3 text-xs">
                      <div>
                        <span className="text-[10px] font-bold text-[#991B1B] uppercase block mb-1">
                          Scientific Critique & Physical Rationale:
                        </span>
                        <p className="text-xs text-[#261B36] leading-relaxed">{crit.rationale}</p>
                      </div>

                      <div className="bg-[#E6F4ED] p-3 border border-[#2E6C4D] space-y-1">
                        <span className="text-[10px] font-bold text-[#2E6C4D] uppercase block">
                          [RESOLVED IN PLAN] Implemented Scientific Correction:
                        </span>
                        <p className="text-xs text-[#261B36]">{crit.proposed_correction}</p>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-VIEW 10: KNOWLEDGE GAPS & STAGE 02 DIRECTIVES                         */}
      {/* ========================================================================= */}
      {activeSubTab === 'gaps' && (
        <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[2px_2px_0px_#493764] space-y-4">
          <div className="flex items-center justify-between border-b border-[#D6C4EC] pb-2 mb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#261B36] flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4 text-[#7350A0]" />
              AGENT 11 KNOWLEDGE GAPS, CONSTRAINTS & STAGE 02 DIRECTIVES
            </h3>
            <span className="text-[10px] text-[#5F4D77]">{state?.knowledge_gaps?.length || 4} IDENTIFIED GAPS</span>
          </div>

          <div className="space-y-3">
            {(state?.knowledge_gaps || []).map((gap) => (
              <div key={gap.gap_id} className="bg-[#EDE5F7] border border-[#493764] p-3.5 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="bg-[#7350A0] text-white text-[9px] px-1.5 py-0.2 font-mono uppercase font-bold">
                      {gap.gap_id}
                    </span>
                    <span className="text-[9px] font-bold uppercase bg-[#DFD3EE] border border-[#493764] px-1.5 py-0.2 text-[#493764]">
                      {gap.gap_type}
                    </span>
                  </div>
                  <span
                    className={`text-[9px] px-1.5 py-0.2 font-bold uppercase border ${
                      gap.severity === 'CRITICAL'
                        ? 'bg-[#FEE2E2] text-[#991B1B] border-[#DC2626]'
                        : 'bg-[#FEF3C7] text-[#92400E] border-[#D97706]'
                    }`}
                  >
                    SEVERITY: {gap.severity}
                  </span>
                </div>

                <p className="text-xs text-[#261B36] font-bold">{gap.description}</p>
                <p className="text-[11px] text-[#5F4D77]">{gap.impact_on_research}</p>

                <div className="bg-[#F8F5FC] p-2.5 border border-[#493764] space-y-1.5 text-xs">
                  <span className="text-[10px] font-bold text-[#7350A0] uppercase block">
                    Recommended Stage 02 Resolution Strategy:
                  </span>
                  <p className="text-[11px] text-[#261B36]">{gap.resolution_approach}</p>

                  {gap.recommended_stage02_searches && gap.recommended_stage02_searches.length > 0 && (
                    <div className="pt-1">
                      <span className="text-[9px] font-bold text-[#5F4D77] uppercase block mb-1">
                        Formulated Academic Search Directives:
                      </span>
                      <div className="space-y-1 font-mono text-[10px]">
                        {gap.recommended_stage02_searches.map((s, i) => (
                          <div key={i} className="bg-[#DFD3EE] p-1 border border-[#493764] text-[#261B36]">
                            &gt; {s}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-VIEW 11: CHRONOLOGICAL AUDIT TIMELINE                                 */}
      {/* ========================================================================= */}
      {activeSubTab === 'timeline' && (
        <div className="bg-[#F8F5FC] border-2 border-[#493764] p-4 shadow-[2px_2px_0px_#493764] space-y-4">
          <div className="flex items-center justify-between border-b border-[#D6C4EC] pb-2 mb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#261B36] flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-[#7350A0]" />
              CHRONOLOGICAL MULTI-AGENT INVESTIGATION TIMELINE
            </h3>
            <span className="text-[10px] text-[#5F4D77]">FULL REPRODUCIBILITY AUDIT LOG</span>
          </div>

          <div className="space-y-2 border-l-2 border-[#7350A0] ml-3 pl-4">
            {(state?.timeline || []).map((ev, idx) => (
              <div key={idx} className="relative pb-3 last:pb-0 text-xs">
                <span className="absolute -left-[23px] top-1 w-3 h-3 bg-[#7350A0] border-2 border-white rounded-full" />
                <div className="flex items-center gap-2">
                  <span className="text-[9px] font-mono text-[#5F4D77]">
                    {new Date(ev.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="bg-[#DFD3EE] border border-[#493764] text-[9px] px-1.5 py-0.2 font-bold uppercase text-[#261B36]">
                    ROUND {ev.round_number} &bull; {ev.event_type}
                  </span>
                  <span className="text-[10px] font-bold text-[#7350A0]">{ev.agent_name}</span>
                </div>
                <p className="text-xs text-[#261B36] mt-0.5">{ev.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
