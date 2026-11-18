import React, { useEffect, useState } from 'react';
import { Share2, Search, ArrowRight, Route, Filter, Sparkles } from 'lucide-react';
import { getSubgraph, findPaths } from '../../api/client';
import { SubgraphData, GraphNode, GraphEdge } from '../../types';

export const KnowledgeGraphWorkspace: React.FC = () => {
  const [data, setData] = useState<SubgraphData>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [selectedDomain, setSelectedDomain] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  // Path finder state
  const [sourceConcept, setSourceConcept] = useState('pressure_difference');
  const [targetConcept, setTargetConcept] = useState('electric_current');
  const [foundPaths, setFoundPaths] = useState<string[][]>([]);
  const [findingPaths, setFindingPaths] = useState(false);

  useEffect(() => {
    loadGraph();
  }, [selectedDomain]);

  const loadGraph = async () => {
    setLoading(true);
    try {
      const res = await getSubgraph(selectedDomain === 'all' ? undefined : selectedDomain);
      setData(res);
    } finally {
      setLoading(false);
    }
  };

  const handleFindPaths = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sourceConcept.trim() || !targetConcept.trim()) return;
    setFindingPaths(true);
    try {
      const res = await findPaths(sourceConcept, targetConcept);
      setFoundPaths(res.paths || []);
    } catch {
      setFoundPaths([]);
    } finally {
      setFindingPaths(false);
    }
  };

  const filteredNodes = data.nodes.filter(
    (n) =>
      n.canonical_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      n.domain.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="w-full max-w-5xl mx-auto px-4 py-8">
      <div className="flex items-center gap-2 mb-2">
        <Share2 className="w-5 h-5 text-indigo-600" />
        <h1 className="text-xl font-bold text-gray-900">Knowledge Graph Explorer</h1>
      </div>
      <p className="text-xs text-gray-500 mb-6">
        Traverse the multi-domain ontology, inspect SI dimensional representations, and trace concept paths across scientific disciplines.
      </p>

      {/* Path Discovery Tool */}
      <div className="p-4 bg-white border border-gray-200 rounded-2xl shadow-xs mb-8">
        <h2 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2 flex items-center gap-1.5">
          <Route className="w-3.5 h-3.5 text-blue-600" />
          Cross-Domain Concept Path Discovery
        </h2>
        <form onSubmit={handleFindPaths} className="grid grid-cols-1 sm:grid-cols-5 gap-2.5 items-end">
          <div className="sm:col-span-2">
            <label className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Source Concept</label>
            <input
              type="text"
              value={sourceConcept}
              onChange={(e) => setSourceConcept(e.target.value)}
              className="w-full text-xs border border-gray-200 rounded-lg px-2.5 py-1.5 font-mono"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Target Concept</label>
            <input
              type="text"
              value={targetConcept}
              onChange={(e) => setTargetConcept(e.target.value)}
              className="w-full text-xs border border-gray-200 rounded-lg px-2.5 py-1.5 font-mono"
            />
          </div>
          <button
            type="submit"
            disabled={findingPaths}
            className="text-xs font-semibold px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {findingPaths ? 'Searching...' : 'Find Paths'}
          </button>
        </form>

        {foundPaths.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <span className="text-[11px] font-bold text-gray-700 block mb-1">
              Discovered Multi-Hop Knowledge Paths ({foundPaths.length}):
            </span>
            <div className="space-y-1">
              {foundPaths.map((p, idx) => (
                <div key={idx} className="text-xs font-mono bg-blue-50/60 text-blue-900 px-3 py-1.5 rounded-lg border border-blue-100 flex items-center gap-2">
                  <span>{p.join(' → ')}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Graph Filter & Search */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-gray-400" />
          <select
            value={selectedDomain}
            onChange={(e) => setSelectedDomain(e.target.value)}
            className="text-xs border border-gray-200 rounded-lg px-2.5 py-1.5 bg-white font-medium"
          >
            <option value="all">All Domains ({data.nodes.length} nodes)</option>
            <option value="fluid_mechanics">Fluid Mechanics</option>
            <option value="electrodynamics">Electrodynamics</option>
            <option value="thermodynamics">Thermodynamics</option>
            <option value="general_science">General Science</option>
          </select>
        </div>

        <div className="relative">
          <Search className="w-3.5 h-3.5 text-gray-400 absolute left-2.5 top-2.5" />
          <input
            type="text"
            placeholder="Search concepts or SI units..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="text-xs border border-gray-200 rounded-lg pl-8 pr-3 py-1.5 w-60 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Graph Nodes Grid & Detail Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-2 max-h-[500px] overflow-y-auto pr-1">
          {filteredNodes.map((n) => (
            <div
              key={n.id}
              onClick={() => setSelectedNode(n)}
              className={`p-3 rounded-xl border text-xs cursor-pointer transition-colors ${
                selectedNode?.id === n.id
                  ? 'bg-blue-50 border-blue-300 ring-2 ring-blue-100 shadow-2xs'
                  : 'bg-white border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-gray-900">{n.canonical_name}</span>
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-gray-100 text-gray-600">
                  {n.domain}
                </span>
              </div>
              <div className="flex items-center gap-3 text-[11px] text-gray-500 font-mono">
                {n.symbol && <span>Symbol: {n.symbol}</span>}
                {n.si_dimension && <span>SI: {n.si_dimension}</span>}
                <span>Category: {n.category}</span>
              </div>
            </div>
          ))}
          {filteredNodes.length === 0 && (
            <div className="p-8 text-center text-xs text-gray-400 bg-gray-50 rounded-xl">
              No matching concepts found.
            </div>
          )}
        </div>

        {/* Selected Node Details */}
        <div className="md:col-span-1">
          {selectedNode ? (
            <div className="p-4 bg-white border border-gray-200 rounded-2xl shadow-xs sticky top-20">
              <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                {selectedNode.domain}
              </span>
              <h3 className="text-base font-bold text-gray-900 mt-2">{selectedNode.canonical_name}</h3>

              <div className="mt-4 space-y-2 text-xs">
                <div className="p-2.5 bg-gray-50 rounded-lg">
                  <span className="text-[10px] font-bold uppercase text-gray-400 block mb-0.5">SI Dimension</span>
                  <span className="font-mono text-gray-800">{selectedNode.si_dimension || 'Dimensionless / Abstract'}</span>
                </div>
                <div className="p-2.5 bg-gray-50 rounded-lg">
                  <span className="text-[10px] font-bold uppercase text-gray-400 block mb-0.5">Symbolic Representation</span>
                  <span className="font-mono text-gray-800">{selectedNode.symbol || 'N/A'}</span>
                </div>
                <div className="p-2.5 bg-gray-50 rounded-lg">
                  <span className="text-[10px] font-bold uppercase text-gray-400 block mb-0.5">Category</span>
                  <span className="font-semibold text-gray-800">{selectedNode.category}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-6 bg-gray-50 border border-gray-200 rounded-2xl text-center text-xs text-gray-400">
              Select any concept node to inspect its formal physical definition and dimensional properties.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
