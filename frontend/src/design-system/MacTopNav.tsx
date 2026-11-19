import React, { useState } from 'react';
import {
  Compass,
  History,
  ExternalLink,
  ChevronDown,
  BookOpen,
  Share2,
  GitBranch,
  Repeat,
  FlaskConical,
  CheckCircle,
  Database,
  BarChart3,
  Settings,
  Key,
  CreditCard,
  Shield,
  User,
  LogOut,
} from 'lucide-react';
import { MacButton } from './MacButton';
import { MacBadge } from './MacBadge';

export interface MacTopNavProps {
  currentWorkspace: string;
  onSelectWorkspace: (wsId: string) => void;
  onOpenHistory: () => void;
  onGoHome: () => void;
  user?: { email: string; full_name?: string; role?: string } | null;
  onOpenAuth?: () => void;
  onLogout?: () => void;
}

export const MacTopNav: React.FC<MacTopNavProps> = ({
  currentWorkspace,
  onSelectWorkspace,
  onOpenHistory,
  onGoHome,
  user,
  onOpenAuth,
  onLogout,
}) => {
  const [deskDropdownOpen, setDeskDropdownOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const workspaces = [
    { id: 'workspace', label: 'Ask AXION', icon: <Compass className="w-3.5 h-3.5" /> },
    { id: 'library', label: 'Research Library', icon: <BookOpen className="w-3.5 h-3.5" /> },
    { id: 'graph', label: 'Knowledge Graph', icon: <Share2 className="w-3.5 h-3.5" /> },
    { id: 'reasoning', label: 'Reasoning Engine', icon: <GitBranch className="w-3.5 h-3.5" /> },
    { id: 'transfer', label: 'Cross-Domain Solver', icon: <Repeat className="w-3.5 h-3.5" /> },
    { id: 'hypothesis', label: 'Hypothesis Lab', icon: <FlaskConical className="w-3.5 h-3.5" /> },
    { id: 'validation', label: 'Validation Sandbox', icon: <CheckCircle className="w-3.5 h-3.5" /> },
    { id: 'memory', label: 'Validated Memory', icon: <Database className="w-3.5 h-3.5" /> },
    { id: 'benchmarks', label: 'Evaluation & Benchmarks', icon: <BarChart3 className="w-3.5 h-3.5" /> },
    { id: 'apikeys', label: 'Developer API Keys', icon: <Key className="w-3.5 h-3.5" /> },
    { id: 'billing', label: 'Usage & Billing', icon: <CreditCard className="w-3.5 h-3.5" /> },
    { id: 'settings', label: 'User Settings', icon: <Settings className="w-3.5 h-3.5" /> },
  ];

  const currentWsObj = workspaces.find((w) => w.id === currentWorkspace) || workspaces[0];

  return (
    <header className="w-full bg-[#EAE2CF] border-b-2 border-[#252820] px-4 sm:px-6 py-2.5 flex items-center justify-between sticky top-0 z-40 select-none">
      {/* Brand & Stamped Logo matching screenshot */}
      <div className="flex items-center gap-3">
        <button
          onClick={onGoHome}
          className="flex items-center gap-2 text-left focus:outline-none cursor-pointer"
        >
          <span
            className="font-serif font-black text-xl sm:text-2xl tracking-normal text-[#252820] leading-none"
            style={{ fontFamily: 'var(--font-slab)' }}
          >
            AXION
          </span>
          <MacBadge variant="vermilion" isStamp size="sm">
            INTELLIGENCE
          </MacBadge>
        </button>
      </div>

      {/* Right Controls matching screenshot */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Workspace Switcher Pill */}
        <div className="relative">
          <MacButton
            variant="paper"
            size="sm"
            onClick={() => setDeskDropdownOpen(!deskDropdownOpen)}
            leftIcon={currentWsObj.icon}
            rightIcon={<ChevronDown className="w-3 h-3 text-[#777568]" />}
          >
            {currentWsObj.label}
          </MacButton>

          {deskDropdownOpen && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setDeskDropdownOpen(false)}
              />
              <div className="absolute right-0 mt-1.5 w-64 bg-[#FDFBF7] border-2 border-[#252820] shadow-[4px_4px_0px_#252820] py-1 z-50 max-h-[80vh] overflow-y-auto">
                <div className="px-3 py-1 text-[10px] font-mono font-bold uppercase tracking-wider text-[#777568] border-b border-[#252820]/20">
                  SYSTEM DESKS
                </div>
                {workspaces.map((ws) => (
                  <button
                    key={ws.id}
                    onClick={() => {
                      onSelectWorkspace(ws.id);
                      setDeskDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 flex items-center gap-2.5 text-xs font-mono font-semibold hover:bg-[#EAE2CF] transition-none cursor-pointer ${
                      currentWorkspace === ws.id ? 'bg-[#EAE2CF] font-bold text-[#252820]' : 'text-[#5A584D]'
                    }`}
                  >
                    <span>{ws.icon}</span>
                    <span className="truncate">{ws.label}</span>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Investigation History Quick Button */}
        <button
          onClick={onOpenHistory}
          className="p-1.5 bg-[#FDFBF7] border-2 border-[#252820] shadow-[2px_2px_0px_#252820] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none cursor-pointer"
          title="Investigation History"
        >
          <History className="w-4 h-4 text-[#252820]" />
        </button>

        {/* API Link Button */}
        <a
          href="/docs"
          target="_blank"
          rel="noreferrer"
          className="hidden sm:inline-flex items-center gap-1 px-2.5 py-1 text-xs font-mono font-bold uppercase text-[#252820] hover:bg-[#FDFBF7] border-2 border-[#252820] shadow-[2px_2px_0px_#252820] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none"
        >
          <span>API</span>
          <ExternalLink className="w-3 h-3 text-[#252820]" />
        </a>

        {/* User Account / Auth Trigger */}
        {user ? (
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-mono font-bold uppercase bg-[#FDFBF7] border-2 border-[#252820] shadow-[2px_2px_0px_#252820] cursor-pointer"
            >
              <User className="w-3.5 h-3.5 text-[#252820]" />
              <span className="max-w-[100px] truncate hidden md:inline">
                {user.full_name || user.email.split('@')[0]}
              </span>
            </button>

            {userMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setUserMenuOpen(false)}
                />
                <div className="absolute right-0 mt-1.5 w-48 bg-[#FDFBF7] border-2 border-[#252820] shadow-[4px_4px_0px_#252820] py-1 z-50 text-xs font-mono">
                  <div className="px-3 py-1.5 border-b border-[#252820]/20 text-[10px] text-[#777568]">
                    <div className="font-bold text-[#252820] truncate">{user.email}</div>
                    <div className="uppercase">ROLE: {user.role || 'RESEARCHER'}</div>
                  </div>
                  <button
                    onClick={() => {
                      onSelectWorkspace('settings');
                      setUserMenuOpen(false);
                    }}
                    className="w-full text-left px-3 py-1.5 hover:bg-[#EAE2CF] flex items-center gap-2"
                  >
                    <Settings className="w-3.5 h-3.5" />
                    <span>SETTINGS</span>
                  </button>
                  <button
                    onClick={() => {
                      onSelectWorkspace('billing');
                      setUserMenuOpen(false);
                    }}
                    className="w-full text-left px-3 py-1.5 hover:bg-[#EAE2CF] flex items-center gap-2"
                  >
                    <CreditCard className="w-3.5 h-3.5" />
                    <span>BILLING & QUOTA</span>
                  </button>
                  {user.role === 'ADMIN' && (
                    <button
                      onClick={() => {
                        onSelectWorkspace('admin');
                        setUserMenuOpen(false);
                      }}
                      className="w-full text-left px-3 py-1.5 hover:bg-[#EAE2CF] flex items-center gap-2 text-[#C0392B] font-bold"
                    >
                      <Shield className="w-3.5 h-3.5" />
                      <span>ADMIN CONSOLE</span>
                    </button>
                  )}
                  {onLogout && (
                    <button
                      onClick={() => {
                        onLogout();
                        setUserMenuOpen(false);
                      }}
                      className="w-full text-left px-3 py-1.5 border-t border-[#252820]/20 hover:bg-[#FBEBE9] text-[#C0392B] flex items-center gap-2"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      <span>LOG OUT</span>
                    </button>
                  )}
                </div>
              </>
            )}
          </div>
        ) : (
          onOpenAuth && (
            <MacButton variant="ink" size="sm" onClick={onOpenAuth}>
              LOG IN
            </MacButton>
          )
        )}
      </div>
    </header>
  );
};
