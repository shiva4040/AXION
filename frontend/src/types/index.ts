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
