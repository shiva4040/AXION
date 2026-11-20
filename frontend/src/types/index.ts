// Type definitions for AXION Frontend and API Integrations

export const ENGINE_METADATA = {
  engine: "Three.js WebGL Engine",
  showcase_scene: "Solar-Powered Electric Drivetrain",
};

export type EpistemicTier =
  | 'FACT_DOCUMENTED'
  | 'HYPOTHESIS_CONJECTURED'
  | 'FINDING_VALIDATED'
  | 'ASSUMPTION_AXIOMATIC'
  | 'CONTRADICTED';

export type WorkspaceId =
  | 'ask'
  | 'library'
  | 'graph'
  | 'assistant'
  | 'reasoning'
  | 'transfer'
  | 'hypothesis'
  | 'validation'
  | 'memory'
  | 'history'
  | 'showcase';

export interface EvidenceSnippet {
  snippet: string;
  source: string;
  epistemic_tier: string;
}

export interface ReasoningStep {
  step: number;
  action: string;
  detail: string;
}

export interface TransferInfo {
  source: string;
  target: string;
  verdict: 'ACCEPTED' | 'CONDITIONAL' | 'REJECTED';
  equation?: string;
  rationale: string;
  assumptions?: string[];
  conditions?: string[];
}

export interface SubQuestion {
  id: string;
  question: string;
  target_subject: string;
  information_needed: string;
  depends_on: string[];
  status: string;
}

export interface ExtractedEvidenceItem {
  item_id: string;
  item_type: string;
  statement: string;
  canonical_symbol?: string;
  variables: Record<string, string>;
  units?: string;
  relevance_explanation: string;
  relevant_subquestion_ids: string[];
  source_name: string;
  source_uri?: string;
  source_title: string;
  doi?: string;
  epistemic_tier: string;
  confidence: number;
  assumptions: string[];
  conditions: string[];
  is_contradicted: boolean;
  contradiction_notes?: string;
  provenance?: {
    document_id?: string;
    chunk_id?: string;
    page_number?: number;
    extracted_snippet?: string;
  };
}

export interface AcquiredDocumentSummary {
  document_id: string;
  title: string;
  source_name: string;
  source_uri?: string;
  authors: string[];
  year?: number;
  abstract?: string;
  epistemic_tier?: string;
  doi?: string;
}

export interface CrossDomainBridge {
  source_item_id: string;
  target_item_id: string;
  source_domain: string;
  target_domain: string;
  common_concepts: string[];
  bridge_type: string;
  rationale: string;
}

export interface AgentStatusRecord {
  role: string;
  name: string;
  status: 'IDLE' | 'ACTIVE' | 'COMPLETED' | 'BLOCKED' | 'FAILED';
  current_task?: string;
  started_at?: string;
  completed_at?: string;
  findings_count: number;
}

export interface AgentFinding {
  finding_id: string;
  agent_role: string;
  agent_name: string;
  round_number: number;
  finding_type: string;
  title: string;
  content: string;
  scientific_basis?: string;
  confidence: number;
  equations?: string[];
  tags: string[];
  timestamp: string;
}

export interface HierarchicalSubQuestion {
  id: string;
  question: string;
  level: 'main' | 'major_area' | 'subquestion' | 'investigative';
  parent_id?: string;
  target_domain?: string;
  information_needed: string[];
  depends_on: string[];
  rationales?: string;
}

export interface DiscoveredDomain {
  name: string;
  relevance: 'PRIMARY' | 'SECONDARY' | 'SUPPORTING' | 'CONDITIONAL';
  rationale: string;
  key_principles: string[];
}

export interface ScientificConcept {
  name: string;
  domain: string;
  concept_type: 'law' | 'principle' | 'mechanism' | 'model' | 'empirical_effect';
  definition: string;
  relevance_to_question: string;
}

export interface GoverningEquation {
  name: string;
  latex: string;
  symbols: Record<string, string>;
  assumptions: string[];
  validity_boundaries: string;
  rationale: string;
}

export interface PhysicalProcessStep {
  step_number: number;
  name: string;
  mechanism: string;
  input_state: string;
  output_state: string;
  governing_principle: string;
  critical_factors: string[];
}

export interface MaterialOrComponent {
  name: string;
  category: string;
  specifications: string;
  role: string;
  operating_limits: string;
  advantages: string[];
  limitations: string[];
}

export interface EvidenceRequirement {
  requirement_id: string;
  target_subquestion: string;
  information_needed: string;
  target_sources: string[];
  recommended_queries: string[];
  required_data_points: string[];
  verification_criteria: string;
}

export interface CrossDomainBridgeProposal {
  source_domain: string;
  target_domain: string;
  source_concept: string;
  target_concept: string;
  analogical_mapping: string;
  mathematical_correspondence: string;
  validity_limits: string;
  research_value: string;
}

export interface KnowledgeGap {
  gap_id: string;
  description: string;
  gap_type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  impact_on_research: string;
  resolution_approach: string;
  recommended_stage02_searches: string[];
}

export interface AgentCriticism {
  criticism_id: string;
  target_agent: string;
  target_item: string;
  criticism_type: string;
  severity: 'CRITICAL' | 'WARNING' | 'SUGGESTION';
  rationale: string;
  proposed_correction: string;
  status: string;
}

export interface ReviewEvent {
  review_round: number;
  criticisms_raised: number;
  critical_issues: string[];
  resolved_modifications: string[];
  unresolved_disagreements: string[];
  review_summary: string;
}

export interface CompletenessEvaluation {
  overall_score: number;
  intent_score: number;
  domain_score: number;
  subquestion_score: number;
  equation_score: number;
  evidence_score: number;
  decision: 'READY' | 'CONDITIONAL' | 'NEEDS_REVISION';
  unresolved_critical_issues: string[];
  remaining_gaps: string[];
  readiness_rationale: string;
}

export interface TimelineEvent {
  timestamp: string;
  agent_role: string;
  agent_name: string;
  event_type: string;
  description: string;
  round_number: number;
}

export interface AgenticResearchState {
  original_question: string;
  current_round: number;
  max_rounds: number;
  readiness_decision: string;
  primary_domain?: string;
  intent_analysis?: any;
  agent_statuses: Record<string, AgentStatusRecord>;
  findings: AgentFinding[];
  subquestions: HierarchicalSubQuestion[];
  discovered_domains: DiscoveredDomain[];
  scientific_concepts: ScientificConcept[];
  governing_equations: GoverningEquation[];
  physical_process_chain: PhysicalProcessStep[];
  materials_and_components: MaterialOrComponent[];
  evidence_requirements: EvidenceRequirement[];
  cross_domain_bridges: CrossDomainBridgeProposal[];
  knowledge_gaps: KnowledgeGap[];
  criticisms: AgentCriticism[];
  review_events: ReviewEvent[];
  completeness_evaluation?: CompletenessEvaluation;
  timeline: TimelineEvent[];
}

export interface ResearchAnswer {
  investigation_id: string;
  query: string;
  answer: string;
  direct_answer?: string;
  important_points?: string[];
  how_it_works?: ReasoningStep[];
  final_takeaway?: string;
  suggested_3d_scene?: string;
  epistemic_tier: string;
  domains_involved: string[];
  evidence_snippets: EvidenceSnippet[];
  reasoning_steps: ReasoningStep[];
  transfers: TransferInfo[];
  hypotheses: any[];
  experiments: any[];
  validated_findings: any[];
  subquestions?: SubQuestion[];
  research_requirements?: string[];
  subquestion_dependencies?: Record<string, string[]>;
  acquired_sources?: AcquiredDocumentSummary[];
  extracted_evidence?: ExtractedEvidenceItem[];
  cross_domain_bridges?: CrossDomainBridge[];
  missing_information?: string[];
  clarification_needed?: boolean;
  clarification_prompt?: string;
  intended_meaning?: string;
  scientific_subject?: string;
  problem_type?: string;
  extracted_concepts?: string[];
  entities?: string[];
  target_variables?: string[];
  declared_parameters?: Record<string, any>;
  identified_constraints?: Record<string, any>;
  ambiguity_notes?: string[];
  agentic_research_state?: AgenticResearchState;
  acquisition_stats?: {
    total_discovered?: number;
    total_retrieved?: number;
    total_processed?: number;
    failed_count?: number;
    duplicate_count?: number;
    sources_breakdown?: Record<string, number>;
    domain_distribution?: Record<string, number>;
  };
  research_trace?: Record<string, {
    subquestion_id: string;
    question: string;
    target_subject: string;
    information_needed: string[];
    depends_on: string[];
    sources_used: string[];
    evidence_item_ids: string[];
    key_findings: string[];
    relevance_notes: string[];
  }>;
  created_at?: string;
}

export interface DocumentSummary {
  id: string;
  title: string;
  source_type: string;
  source_uri: string;
  page_count: number;
  trust_tier: string;
  file_hash_sha256: string;
}

export interface GraphNode {
  id: string;
  canonical_name: string;
  domain: string;
  category: string;
  symbol?: string;
  si_dimension?: string;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation_type: string;
  epistemic_tier: string;
  confidence: number;
}

export interface SubgraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ValidatedFinding {
  id: string;
  title: string;
  formal_statement: string;
  domain: string;
  epistemic_tier: string;
  status: string;
  confidence_score: number;
  supporting_experiments: string[];
  created_at: string;
  version: number;
}
