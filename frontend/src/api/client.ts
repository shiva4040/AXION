// Real API Client connecting to the FastAPI backend at /api/v1
import { DocumentSummary, ResearchAnswer, SubgraphData, ValidatedFinding } from '../types';

const API_BASE = '/api/v1';

export async function askQuestion(query: string, document_id?: string): Promise<ResearchAnswer> {
  const res = await fetch(`${API_BASE}/investigation/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, document_id }),
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Investigation failed (${res.status}): ${errorText}`);
  }
  return res.json();
}

export async function getInvestigationHistory(): Promise<ResearchAnswer[]> {
  const res = await fetch(`${API_BASE}/investigation/history`);
  if (!res.ok) return [];
  return res.json();
}

export async function getDocuments(): Promise<DocumentSummary[]> {
  const res = await fetch(`${API_BASE}/sources/documents`);
  if (!res.ok) return [];
  return res.json();
}

export async function ingestText(
  title: string,
  text_content: string,
  source_uri: string = 'manual://upload',
  trust_tier: string = 'PEER_REVIEWED'
): Promise<DocumentSummary> {
  const res = await fetch(`${API_BASE}/sources/ingest-text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, text_content, source_uri, trust_tier }),
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Document ingestion failed: ${errorText}`);
  }
  return res.json();
}

export async function getSubgraph(domain?: string): Promise<SubgraphData> {
  const url = domain ? `${API_BASE}/graph/subgraph?domain=${encodeURIComponent(domain)}` : `${API_BASE}/graph/subgraph`;
  const res = await fetch(url);
  if (!res.ok) return { nodes: [], edges: [] };
  return res.json();
}

export async function findPaths(source: string, target: string, max_hops: number = 4) {
  const url = `${API_BASE}/graph/paths?source=${encodeURIComponent(source)}&target=${encodeURIComponent(target)}&max_hops=${max_hops}`;
  const res = await fetch(url);
  if (!res.ok) return { source, target, paths: [] };
  return res.json();
}

export async function decomposeGoal(goal: string, variable_values?: Record<string, number>) {
  const res = await fetch(`${API_BASE}/reasoning/decompose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ goal, variable_values }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function solveGoal(goal: string, variable_values?: Record<string, number>) {
  const res = await fetch(`${API_BASE}/reasoning/solve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ goal, variable_values }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getContradictions(domain?: string) {
  const url = domain ? `${API_BASE}/reasoning/contradictions?domain=${encodeURIComponent(domain)}` : `${API_BASE}/reasoning/contradictions`;
  const res = await fetch(url);
  if (!res.ok) return [];
  return res.json();
}

export async function evaluateTransfer(source_bundle: any, target_bundle: any, method: string = 'STRUCTURE_MAPPING') {
  const res = await fetch(`${API_BASE}/transfer/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source_bundle, target_bundle, method }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function generateHypotheses(transfer_record: any, include_conditional: boolean = true) {
  const res = await fetch(`${API_BASE}/hypothesis/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transfer_record, include_conditional }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function runExperiment(req: any) {
  const res = await fetch(`${API_BASE}/validation/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getValidatedFindings(domain?: string, status?: string): Promise<ValidatedFinding[]> {
  const params = new URLSearchParams();
  if (domain) params.append('domain', domain);
  if (status) params.append('status', status);
  const res = await fetch(`${API_BASE}/memory/findings?${params.toString()}`);
  if (!res.ok) return [];
  return res.json();
}

export async function invalidateFinding(finding_id: string, reason: string) {
  const res = await fetch(`${API_BASE}/memory/findings/${finding_id}/invalidate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
