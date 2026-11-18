import React, { useState } from 'react';
import {
  Compass,
  BookOpen,
  Share2,
  Cpu,
  GitBranch,
  Repeat,
  FlaskConical,
  CheckCircle,
  Database,
  History,
  ExternalLink,
  ChevronDown,
} from 'lucide-react';
import { WorkspaceId } from '../types';

interface Props {
  activeWorkspace: WorkspaceId;
  onSelectWorkspace: (ws: WorkspaceId) => void;
  onOpenHistory: () => void;
  onGoHome: () => void;
}

export const Navigation: React.FC<Props> = ({
  activeWorkspace,
  onSelectWorkspace,
  onOpenHistory,
  onGoHome,
}) => {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const workspaces: Array<{ id: WorkspaceId; label: string; icon: React.ReactNode; desc: string }> = [
    { id: 'ask', label: 'Ask AXION', icon: <Compass className="w-4 h-4 text-blue-600" />, desc: 'Primary minimal scientific question workspace' },
    { id: 'library', label: 'Knowledge Library', icon: <BookOpen className="w-4 h-4 text-emerald-600" />, desc: 'Ingested documents, papers, and trust tiers' },
    { id: 'graph', label: 'Knowledge Graph', icon: <Share2 className="w-4 h-4 text-indigo-600" />, desc: '3D & 2D entity-relation network & concept paths' },
    { id: 'assistant', label: 'Research Assistant', icon: <Cpu className="w-4 h-4 text-sky-600" />, desc: 'Advanced scientific multi-turn investigations' },
    { id: 'reasoning', label: 'Reasoning Workspace', icon: <GitBranch className="w-4 h-4 text-purple-600" />, desc: 'Goal decomposition DAG & contradiction detection' },
    { id: 'transfer', label: 'Cross-Domain Transfer', icon: <Repeat className="w-4 h-4 text-amber-600" />, desc: 'Structural alignment & applicability guard' },
    { id: 'hypothesis', label: 'Hypothesis Lab', icon: <FlaskConical className="w-4 h-4 text-rose-600" />, desc: 'Tier 3 conjectured formal hypothesis generator' },
    { id: 'validation', label: 'Experiment & Validation', icon: <CheckCircle className="w-4 h-4 text-teal-600" />, desc: 'Sandbox symbolic, numerical, and ODE tests' },
    { id: 'memory', label: 'Validated Knowledge Memory', icon: <Database className="w-4 h-4 text-blue-700" />, desc: 'Tier 4 findings, version audit logs, dependency cascades' },
    { id: 'history', label: 'Research History', icon: <History className="w-4 h-4 text-gray-600" />, desc: 'Timeline and replay of past investigations' },
  ];

  const currentWs = workspaces.find((w) => w.id === activeWorkspace) || workspaces[0];

  return (
    <header className="w-full bg-white border-b border-gray-100 px-6 py-3.5 flex items-center justify-between sticky top-0 z-50">
      {/* Brand Logo */}
      <div className="flex items-center gap-3">
        <button
          onClick={onGoHome}
          className="flex items-center gap-2 text-left group focus:outline-none"
        >
          <span className="font-bold text-lg tracking-wider text-gray-900 group-hover:text-blue-600 transition-colors">
            AXION
          </span>
          <span className="text-[10px] font-semibold tracking-wider uppercase text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100">
            Intelligence
          </span>
        </button>
      </div>

      {/* Center / Right Controls */}
      <div className="flex items-center gap-3">
        {/* Workspace Switcher Pill */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-200 bg-[#fbfbfc] hover:bg-gray-50 text-xs font-medium text-gray-700 transition-colors shadow-2xs"
          >
            {currentWs.icon}
            <span>{currentWs.label}</span>
            <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setDropdownOpen(false)}
              />
              <div className="absolute right-0 mt-1.5 w-72 bg-white rounded-xl border border-gray-200 shadow-lg py-1.5 z-50 max-h-[80vh] overflow-y-auto">
                <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-gray-400 border-b border-gray-100">
                  AXION Workspaces
                </div>
                {workspaces.map((ws) => (
                  <button
                    key={ws.id}
                    onClick={() => {
                      onSelectWorkspace(ws.id);
                      setDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 flex items-start gap-2.5 hover:bg-gray-50 transition-colors ${
                      activeWorkspace === ws.id ? 'bg-blue-50/60' : ''
                    }`}
                  >
                    <div className="mt-0.5">{ws.icon}</div>
                    <div>
                      <div className={`text-xs font-medium ${activeWorkspace === ws.id ? 'text-blue-700' : 'text-gray-900'}`}>
                        {ws.label}
                      </div>
                      <div className="text-[11px] text-gray-500 leading-tight">
                        {ws.desc}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Quick History Button */}
        <button
          onClick={onOpenHistory}
          className="p-1.5 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors text-xs flex items-center gap-1.5"
          title="Investigation History"
        >
          <History className="w-4 h-4" />
        </button>

        {/* API Link */}
        <a
          href="/docs"
          target="_blank"
          rel="noreferrer"
          className="text-xs font-medium text-gray-500 hover:text-gray-900 px-2 py-1 flex items-center gap-1 transition-colors"
          title="Open FastAPI Swagger Documentation"
        >
          <span>API</span>
          <ExternalLink className="w-3 h-3 text-gray-400" />
        </a>
      </div>
    </header>
  );
};
