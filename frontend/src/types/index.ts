// Type definitions for AXION Frontend and API Integrations

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
  | 'history';

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

export interface ResearchAnswer {
  investigation_id: string;
  query: string;
  answer: string;
  epistemic_tier: string;
  domains_involved: string[];
  evidence_snippets: EvidenceSnippet[];
  reasoning_steps: ReasoningStep[];
  transfers: TransferInfo[];
  hypotheses: any[];
  experiments: any[];
  validated_findings: any[];
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
