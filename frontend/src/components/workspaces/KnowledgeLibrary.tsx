import React, { useEffect, useState } from 'react';
import {
  BookOpen, Upload, FileText, CheckCircle2, Shield, AlertCircle,
  Search, Database, Network, ArrowRight, Layers, Sparkles, RefreshCw,
  ExternalLink, Key, Check, Info, GitBranch, Cpu
} from 'lucide-react';
import {
  getDocuments, ingestText, getAcquisitionSources, getAcquisitionStatistics,
  getResearchCollection, getKnowledgeAccumulation, getAcquisitionHistory, searchAcquisition
} from '../../api/client';
import { DocumentSummary } from '../../types';

interface SourceHealth {
  source_name: string;
  source_type: string;
  is_available: boolean;
  status_message: string;
  requires_auth?: boolean;
  is_authenticated?: boolean;
  supported_doc_types?: string[];
}

interface AccumulationStats {
  total_documents_retrieved: number;
  total_claims: number;
  total_equations: number;
  total_assumptions: number;
  total_boundary_conditions: number;
  total_knowledge_items: number;
  total_cross_domain_connections: number;
  total_contradictions_detected: number;
  total_searches_executed?: number;
  total_discovered_across_queries?: number;
  total_deduplicated_across_queries?: number;
  domain_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
}

interface AccumulatedItem {
  id: string;
  source_name: string;
  source_title: string;
  domain: string;
  item_type: string;
  content: string;
  canonical_symbol?: string;
  variables?: Record<string, string>;
  assumptions?: string[];
  boundary_conditions?: string[];
  confidence: number;
  is_contradicted: boolean;
  contradiction_notes?: string;
  doi?: string;
  created_at?: string;
}

interface CrossDomainBridge {
  id: string;
  source_item_id: string;
  target_item_id: string;
  source_domain: string;
  target_domain: string;
  bridge_type: string;
  shared_concept: string;
  confidence: number;
  description?: string;
}

export const KnowledgeLibrary: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'sources' | 'collection' | 'accumulation' | 'history' | 'discovery'>('overview');

  // Data states
  const [sources, setSources] = useState<SourceHealth[]>([]);
  const [stats, setStats] = useState<AccumulationStats | null>(null);
  const [collection, setCollection] = useState<any[]>([]);
  const [accumItems, setAccumItems] = useState<AccumulatedItem[]>([]);
  const [bridges, setBridges] = useState<CrossDomainBridge[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Ingestion form states
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadText, setUploadText] = useState('');
  const [uploadTrust, setUploadTrust] = useState('PEER_REVIEWED');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  // Live discovery search states
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);

  // Filtering for accumulation
  const [filterDomain, setFilterDomain] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');

  useEffect(() => {
    refreshAllData();
  }, []);

  const refreshAllData = async () => {
    setLoading(true);
    try {
      const [srcs, st, coll, accum, hist] = await Promise.all([
        getAcquisitionSources(),
        getAcquisitionStatistics(),
        getResearchCollection(),
        getKnowledgeAccumulation(),
        getAcquisitionHistory()
      ]);
      setSources(srcs || []);
      setStats(st);
      setCollection(coll || []);
      setAccumItems(accum?.items || []);
      setBridges(accum?.bridges || []);
      setHistory(hist || []);
    } catch (e) {
      console.error('Error refreshing knowledge dashboard data:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadTitle.trim() || !uploadText.trim()) return;
    setUploading(true);
    setMessage(null);
    try {
      await ingestText(uploadTitle, uploadText, `manual://${uploadTitle.replace(/\s+/g, '_')}`, uploadTrust);
      setUploadTitle('');
      setUploadText('');
      setMessage('Document successfully ingested, chunked, and accumulated into Knowledge Graph.');
      await refreshAllData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleLiveSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await searchAcquisition(searchQuery);
      setSearchResults(res?.documents || []);
      await refreshAllData();
    } catch (err: any) {
      alert(`Search failed: ${err.message}`);
    } finally {
      setSearching(false);
    }
  };

  const filteredItems = accumItems.filter(item => {
    if (filterDomain !== 'all' && item.domain !== filterDomain) return false;
    if (filterType !== 'all' && item.item_type !== filterType) return false;
    return true;
  });

  return (
    <div className="w-full max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <BookOpen className="w-6 h-6 text-emerald-600" />
            <h1 className="text-2xl font-bold text-gray-900">Knowledge Source Dashboard & Library</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
              Stage 02 Certified
            </span>
          </div>
          <p className="text-xs text-gray-500">
            Real-time scientific knowledge acquisition, multi-source discovery, structured accumulation, and cross-domain relational transfer.
          </p>
        </div>
        <button
          onClick={refreshAllData}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors shadow-2xs self-start md:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-blue-600' : ''}`} />
          Refresh Metrics
        </button>
      </div>

      {/* Information Flow Architecture Diagram */}
      <div className="p-4 bg-linear-to-r from-blue-50/70 via-indigo-50/70 to-purple-50/70 border border-blue-200/60 rounded-2xl mb-8 shadow-xs">
        <div className="flex items-center gap-2 mb-2 text-xs font-bold text-indigo-900 uppercase tracking-wider">
          <Cpu className="w-4 h-4 text-indigo-600" />
          AXION Information Flow & Inter-Stage Knowledge Integration
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-6 gap-2 text-center text-xs">
          <div className="p-2.5 bg-white/80 rounded-xl border border-blue-200 shadow-2xs">
            <span className="font-bold text-blue-900 block text-[11px]">User Question</span>
            <span className="text-[10px] text-gray-500">Problem formulation</span>
          </div>
          <div className="p-2.5 bg-white/80 rounded-xl border border-indigo-200 shadow-2xs">
            <span className="font-bold text-indigo-900 block text-[11px]">Stage 01</span>
            <span className="text-[10px] text-gray-500">Structured Parsing & Ambiguity Detection</span>
          </div>
          <div className="p-2.5 bg-indigo-600 text-white rounded-xl shadow-xs ring-2 ring-indigo-400/40">
            <span className="font-bold block text-[11px]">Stage 02 Active</span>
            <span className="text-[10px] text-indigo-100">Knowledge Acquisition Engine</span>
          </div>
          <div className="p-2.5 bg-white/80 rounded-xl border border-purple-200 shadow-2xs">
            <span className="font-bold text-purple-900 block text-[11px]">16 Scholarly Sources</span>
            <span className="text-[10px] text-gray-500">arXiv, ADS, INSPIRE, WoS, AJP</span>
          </div>
          <div className="p-2.5 bg-white/80 rounded-xl border border-emerald-200 shadow-2xs">
            <span className="font-bold text-emerald-900 block text-[11px]">Accumulator</span>
            <span className="text-[10px] text-gray-500">Claims, Equations, Bridges</span>
          </div>
          <div className="p-2.5 bg-white/80 rounded-xl border border-amber-200 shadow-2xs">
            <span className="font-bold text-amber-900 block text-[11px]">Stages 03–08</span>
            <span className="text-[10px] text-gray-500">Composition, Transfer, Memory</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-6 border-b border-gray-200 pb-2">
        {[
          { id: 'overview', label: 'Dashboard Overview', icon: Layers },
          { id: 'sources', label: `Research Sources (${sources.length || 16})`, icon: Database },
          { id: 'collection', label: `Research Collection (${collection.length})`, icon: FileText },
          { id: 'accumulation', label: `Knowledge Accumulation (${accumItems.length})`, icon: Network },
          { id: 'history', label: `Retrieval History (${history.length})`, icon: RefreshCw },
          { id: 'discovery', label: 'Live Discovery & Ingest', icon: Search }
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* TAB 1: OVERVIEW & SECTION B: STATISTICS */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Section B: Acquisition Statistics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 bg-white border border-gray-200 rounded-2xl shadow-xs">
              <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider block">Indexed Papers</span>
              <span className="text-2xl font-black text-gray-900 mt-1 block">
                {stats?.total_documents_retrieved ?? collection.length}
              </span>
              <span className="text-[10px] text-emerald-600 font-medium">In SQLite & Vector Index</span>
            </div>

            <div className="p-4 bg-white border border-gray-200 rounded-2xl shadow-xs">
              <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider block">Governing Equations</span>
              <span className="text-2xl font-black text-blue-600 mt-1 block">
                {stats?.total_equations ?? 0}
              </span>
              <span className="text-[10px] text-gray-500">With variable mappings</span>
            </div>

            <div className="p-4 bg-white border border-gray-200 rounded-2xl shadow-xs">
              <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider block">Empirical Claims</span>
              <span className="text-2xl font-black text-purple-600 mt-1 block">
                {stats?.total_claims ?? 0}
              </span>
              <span className="text-[10px] text-gray-500">Extracted & Provenanced</span>
            </div>

            <div className="p-4 bg-white border border-gray-200 rounded-2xl shadow-xs">
              <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider block">Cross-Domain Bridges</span>
              <span className="text-2xl font-black text-amber-600 mt-1 block">
                {stats?.total_cross_domain_connections ?? bridges.length}
              </span>
              <span className="text-[10px] text-amber-700 font-medium">Interdisciplinary transfers</span>
            </div>
          </div>

          {/* Secondary stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-white border border-gray-200 rounded-2xl shadow-xs">
              <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-2">Assumptions & Limits</h3>
              <div className="flex justify-between items-center text-xs py-1 border-b border-gray-100">
                <span className="text-gray-500">Assumptions Extracted:</span>
                <span className="font-bold text-gray-800">{stats?.total_assumptions ?? 0}</span>
              </div>
              <div className="flex justify-between items-center text-xs py-1 border-b border-gray-100">
                <span className="text-gray-500">Boundary Conditions:</span>
                <span className="font-bold text-gray-800">{stats?.total_boundary_conditions ?? 0}</span>
              </div>
              <div className="flex justify-between items-center text-xs py-1">
                <span className="text-gray-500">Contradictions Flagged:</span>
                <span className={`font-bold ${stats?.total_contradictions_detected ? 'text-red-600' : 'text-emerald-600'}`}>
                  {stats?.total_contradictions_detected ?? 0}
                </span>
              </div>
            </div>

            <div className="p-4 bg-white border border-gray-200 rounded-2xl shadow-xs">
              <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-2">Domain Distribution</h3>
              {stats?.domain_distribution && Object.keys(stats.domain_distribution).length > 0 ? (
                <div className="space-y-1.5">
                  {Object.entries(stats.domain_distribution).map(([dom, count]) => (
                    <div key={dom} className="flex justify-between items-center text-xs">
                      <span className="text-gray-600 capitalize">{dom.replace('_', ' ')}</span>
                      <span className="font-mono text-gray-900 font-semibold">{count}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-gray-400 py-3">No domain distribution records yet.</div>
              )}
            </div>

            <div className="p-4 bg-white border border-gray-200 rounded-2xl shadow-xs">
              <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-2">Source Distribution</h3>
              {stats?.source_distribution && Object.keys(stats.source_distribution).length > 0 ? (
                <div className="space-y-1.5">
                  {Object.entries(stats.source_distribution).map(([src, count]) => (
                    <div key={src} className="flex justify-between items-center text-xs">
                      <span className="text-gray-600 uppercase">{src}</span>
                      <span className="font-mono text-gray-900 font-semibold">{count}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-gray-400 py-3">No source distribution records yet.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: SECTION A: RESEARCH SOURCES */}
      {activeTab === 'sources' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Configured Scholarly Sources & Preprints (16 Sources)
            </h2>
            <span className="text-xs text-gray-400">Verified & Monitored</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3.5">
            {sources.map(src => {
              const isOk = src.is_available;
              return (
                <div
                  key={src.source_name}
                  className="p-3.5 bg-white border border-gray-200 rounded-xl shadow-2xs hover:border-gray-300 transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <h4 className="font-bold text-xs text-gray-900 uppercase tracking-wider">
                        {src.source_name.replace('_', ' ')}
                      </h4>
                      <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[9px] font-bold ${
                        isOk ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
                      }`}>
                        {isOk ? <CheckCircle2 className="w-2.5 h-2.5" /> : <AlertCircle className="w-2.5 h-2.5" />}
                        {isOk ? 'Active' : 'Offline'}
                      </span>
                    </div>
                    <p className="text-[11px] text-gray-500 line-clamp-2 mb-2">
                      {src.status_message}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-gray-100 flex items-center justify-between text-[10px]">
                    <span className="text-gray-400">
                      {src.requires_auth ? (
                        <span className="inline-flex items-center gap-0.5 text-amber-600 font-medium">
                          <Key className="w-2.5 h-2.5" /> {src.is_authenticated ? 'Key Verified' : 'Token Required'}
                        </span>
                      ) : (
                        <span className="text-emerald-600 font-medium">Open Access</span>
                      )}
                    </span>
                    <span className="px-1.5 py-0.2 rounded bg-gray-100 text-gray-600 font-mono">
                      {src.source_type}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 3: SECTION C: RESEARCH COLLECTION */}
      {activeTab === 'collection' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Acquired Documents Collection ({collection.length} Publications)
            </h2>
          </div>

          {collection.length === 0 ? (
            <div className="p-8 bg-gray-50 border border-gray-200 rounded-2xl text-center text-xs text-gray-500">
              No research papers in the collection yet. Ingest documents using the Live Discovery or Ingest tabs.
            </div>
          ) : (
            <div className="space-y-2.5">
              {collection.map(doc => (
                <div
                  key={doc.id}
                  className="p-4 bg-white border border-gray-200 rounded-xl flex items-start justify-between text-xs shadow-2xs hover:border-gray-300 transition-colors"
                >
                  <div className="space-y-1">
                    <h4 className="font-bold text-gray-900 text-sm">{doc.title}</h4>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-gray-500">
                      <span>Source: <strong className="text-gray-700">{doc.source_type}</strong></span>
                      {doc.metadata?.doi && <span>DOI: <code className="text-blue-600">{doc.metadata.doi}</code></span>}
                      {doc.metadata?.authors && (
                        <span>Authors: <em>{Array.isArray(doc.metadata.authors) ? doc.metadata.authors.slice(0, 3).join(', ') : doc.metadata.authors}</em></span>
                      )}
                      {doc.page_count && <span>Pages: {doc.page_count}</span>}
                    </div>
                    {doc.source_uri && (
                      <div className="text-[10px] text-gray-400 font-mono truncate max-w-xl">
                        URI: {doc.source_uri}
                      </div>
                    )}
                  </div>
                  <span className="px-2.5 py-1 rounded-md text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-100 uppercase tracking-wider shrink-0">
                    {doc.trust_tier}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: SECTION D: KNOWLEDGE ACCUMULATION */}
      {activeTab === 'accumulation' && (
        <div className="space-y-6">
          {/* Filters */}
          <div className="flex flex-wrap items-center gap-3 p-3 bg-white border border-gray-200 rounded-xl shadow-2xs">
            <span className="text-xs font-bold text-gray-500">Filter By:</span>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="text-xs border border-gray-200 rounded-lg px-2.5 py-1.5 bg-white text-gray-700 focus:outline-none"
            >
              <option value="all">All Item Types</option>
              <option value="equation">Governing Equations</option>
              <option value="claim">Empirical Claims</option>
              <option value="assumption">Assumptions</option>
              <option value="boundary_condition">Boundary Conditions</option>
            </select>

            <select
              value={filterDomain}
              onChange={(e) => setFilterDomain(e.target.value)}
              className="text-xs border border-gray-200 rounded-lg px-2.5 py-1.5 bg-white text-gray-700 focus:outline-none"
            >
              <option value="all">All Domains</option>
              <option value="aerodynamics">Aerodynamics</option>
              <option value="photovoltaics">Photovoltaics</option>
              <option value="electromagnetism">Electromagnetism</option>
              <option value="thermodynamics">Thermodynamics</option>
              <option value="high_energy_physics">High-Energy Physics</option>
              <option value="astrophysics">Astrophysics</option>
              <option value="general_science">General Science</option>
            </select>
          </div>

          {/* Cross Domain Bridges Section */}
          {bridges.length > 0 && (
            <div className="p-4 bg-amber-50/60 border border-amber-200 rounded-2xl shadow-2xs">
              <h3 className="text-xs font-bold text-amber-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <GitBranch className="w-3.5 h-3.5 text-amber-700" />
                Interdisciplinary Cross-Domain Bridges ({bridges.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {bridges.map(br => (
                  <div key={br.id} className="p-3 bg-white rounded-xl border border-amber-200 shadow-2xs text-xs">
                    <div className="flex items-center justify-between font-bold text-amber-900 mb-1">
                      <span>{br.source_domain.toUpperCase()} &rarr; {br.target_domain.toUpperCase()}</span>
                      <span className="text-[10px] text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded">
                        {Math.round(br.confidence * 100)}% Match
                      </span>
                    </div>
                    <p className="text-gray-600 text-[11px] mb-1">{br.description}</p>
                    <span className="font-semibold text-indigo-700 text-[10px]">
                      Concept: {br.shared_concept}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Accumulated Items List */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Extracted Knowledge Elements ({filteredItems.length})
            </h3>

            {filteredItems.length === 0 ? (
              <div className="p-8 bg-gray-50 border border-gray-200 rounded-2xl text-center text-xs text-gray-500">
                No accumulated knowledge items match the current filter.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {filteredItems.map(item => (
                  <div
                    key={item.id}
                    className={`p-4 bg-white border rounded-xl shadow-2xs transition-all ${
                      item.is_contradicted ? 'border-red-300 bg-red-50/20' : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700">
                        {item.item_type}
                      </span>
                      <span className="text-[10px] text-gray-500 font-medium capitalize">
                        {item.domain.replace('_', ' ')}
                      </span>
                    </div>

                    <p className={`font-mono text-xs ${item.item_type === 'equation' ? 'font-bold text-blue-900' : 'text-gray-900'}`}>
                      {item.content}
                    </p>

                    {item.variables && Object.keys(item.variables).length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-100 flex flex-wrap gap-1.5">
                        {Object.entries(item.variables).map(([k, v]) => (
                          <span key={k} className="px-1.5 py-0.5 rounded text-[10px] bg-gray-100 text-gray-700 font-mono">
                            <strong>{k}</strong>: {v}
                          </span>
                        ))}
                      </div>
                    )}

                    {item.is_contradicted && (
                      <div className="mt-2 p-2 bg-red-100/70 border border-red-200 rounded text-[10px] text-red-800">
                        <strong>Contradiction Warning:</strong> {item.contradiction_notes}
                      </div>
                    )}

                    <div className="mt-2 text-[10px] text-gray-400 truncate">
                      Source: {item.source_title} ({item.source_name})
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 5: SECTION E: RETRIEVAL HISTORY */}
      {activeTab === 'history' && (
        <div className="space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-gray-500">
            Discovery & Retrieval Operations Log ({history.length} Queries)
          </h2>

          {history.length === 0 ? (
            <div className="p-8 bg-gray-50 border border-gray-200 rounded-2xl text-center text-xs text-gray-500">
              No search operations recorded yet in this session.
            </div>
          ) : (
            <div className="space-y-3">
              {history.map((h, i) => (
                <div key={i} className="p-4 bg-white border border-gray-200 rounded-xl shadow-2xs text-xs space-y-2">
                  <div className="flex items-center justify-between font-bold text-gray-900">
                    <span className="text-blue-700">"{h.query}"</span>
                    <span className="font-mono text-[11px] text-gray-500">{h.execution_time_ms} ms</span>
                  </div>
                  <div className="flex flex-wrap gap-3 text-[11px] text-gray-600">
                    <span>Discovered: <strong>{h.total_discovered}</strong></span>
                    <span>Deduplicated: <strong>{h.total_deduplicated}</strong></span>
                    <span>Sources Queried: <code>{h.sources_queried?.join(', ')}</code></span>
                  </div>
                  {h.identified_terms && (
                    <div className="flex flex-wrap gap-1 text-[10px]">
                      <span className="text-gray-400">Identified Terms:</span>
                      {h.identified_terms.map((t: string) => (
                        <span key={t} className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600">{t}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 6: LIVE DISCOVERY & INGEST */}
      {activeTab === 'discovery' && (
        <div className="space-y-8">
          {/* Live Search */}
          <div className="p-5 bg-white border border-gray-200 rounded-2xl shadow-xs">
            <h2 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3 flex items-center gap-1.5">
              <Search className="w-3.5 h-3.5 text-blue-600" />
              Live Discovery Across All 16 Scientific Repositories
            </h2>
            <form onSubmit={handleLiveSearch} className="flex gap-2">
              <input
                type="text"
                placeholder="Search across arXiv, NASA ADS, INSPIRE-HEP, Crossref, AJP, OpenAlex..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 text-xs border border-gray-200 rounded-lg px-3 py-2.5 focus:outline-none focus:border-blue-500"
                required
              />
              <button
                type="submit"
                disabled={searching}
                className="px-4 py-2.5 bg-blue-600 text-white text-xs font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-1.5"
              >
                {searching ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
                {searching ? 'Discovering...' : 'Discover'}
              </button>
            </form>

            {searchResults.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
                <span className="text-xs font-bold text-gray-700">
                  Discovered Papers ({searchResults.length})
                </span>
                <div className="space-y-2">
                  {searchResults.map((res, idx) => (
                    <div key={idx} className="p-3 bg-gray-50 border border-gray-200 rounded-xl text-xs flex justify-between items-start">
                      <div>
                        <h5 className="font-bold text-gray-900">{res.title}</h5>
                        <p className="text-[11px] text-gray-500 line-clamp-2 mt-1">{res.content}</p>
                        <div className="mt-1 text-[10px] text-gray-400">
                          Source: <strong>{res.source_name}</strong> &bull; DOI: {res.doi || 'N/A'}
                        </div>
                      </div>
                      <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-[10px] font-bold rounded">
                        {Math.round(res.relevance_score * 100)}% Rel
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Manual Ingestion Form */}
          <div className="p-5 bg-white border border-gray-200 rounded-2xl shadow-xs">
            <h2 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3 flex items-center gap-1.5">
              <Upload className="w-3.5 h-3.5 text-emerald-600" />
              Manual Paper or Scientific Text Ingestion
            </h2>
            <form onSubmit={handleIngest} className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <input
                  type="text"
                  placeholder="Document Title (e.g. Navier-Stokes Continuum Transport)"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  className="sm:col-span-2 text-xs border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
                  required
                />
                <select
                  value={uploadTrust}
                  onChange={(e) => setUploadTrust(e.target.value)}
                  className="text-xs border border-gray-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:border-blue-500"
                >
                  <option value="PEER_REVIEWED">Peer-Reviewed Journal</option>
                  <option value="PREPRINT">Preprint (arXiv/bioRxiv)</option>
                  <option value="TEXTBOOK">Authoritative Textbook</option>
                  <option value="UNVERIFIED">Unverified / Working Draft</option>
                </select>
              </div>
              <textarea
                rows={4}
                placeholder="Paste raw paper text, governing equations, claims, or abstract..."
                value={uploadText}
                onChange={(e) => setUploadText(e.target.value)}
                className="w-full text-xs border border-gray-200 rounded-lg p-3 focus:outline-none focus:border-blue-500 font-mono"
                required
              />
              <div className="flex items-center justify-between">
                {message && (
                  <span className={`text-xs ${message.startsWith('Error') ? 'text-red-600' : 'text-emerald-600'}`}>
                    {message}
                  </span>
                )}
                <button
                  type="submit"
                  disabled={uploading}
                  className="ml-auto text-xs font-semibold px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50"
                >
                  {uploading ? 'Ingesting...' : 'Ingest & Accumulate'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
