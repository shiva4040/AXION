import React, { useEffect, useState } from 'react';
import { Search, Compass, BookOpen, Share2, GitBranch, Repeat, FlaskConical, CheckCircle, Database, BarChart3, Key, CreditCard, Settings } from 'lucide-react';
import { MacDialog } from './MacDialog';

export interface CommandItem {
  id: string;
  title: string;
  category: string;
  shortcut?: string;
  icon?: React.ReactNode;
  action: () => void;
}

export interface MacCommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectWorkspace: (wsId: string) => void;
  onNewQuestion: () => void;
}

export const MacCommandPalette: React.FC<MacCommandPaletteProps> = ({
  isOpen,
  onClose,
  onSelectWorkspace,
  onNewQuestion,
}) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  const commands: CommandItem[] = [
    {
      id: 'new_query',
      title: 'Formulate New Research Query',
      category: 'ACTIONS',
      shortcut: '↵',
      icon: <Compass className="w-3.5 h-3.5 text-[#C0392B]" />,
      action: () => {
        onNewQuestion();
        onClose();
      },
    },
    {
      id: 'ws_ask',
      title: 'Desk 01: Query Workspace',
      category: 'DESKS',
      shortcut: 'G 1',
      icon: <Compass className="w-3.5 h-3.5" />,
      action: () => {
        onSelectWorkspace('workspace');
        onClose();
      },
    },
    {
      id: 'ws_library',
      title: 'Desk 02: Research Library',
      category: 'DESKS',
      shortcut: 'G 2',
      icon: <BookOpen className="w-3.5 h-3.5" />,
      action: () => {
        onSelectWorkspace('library');
        onClose();
      },
    },
    {
      id: 'ws_graph',
      title: 'Desk 03: Knowledge Graph Explorer',
      category: 'DESKS',
      shortcut: 'G 3',
      icon: <Share2 className="w-3.5 h-3.5" />,
      action: () => {
        onSelectWorkspace('graph');
        onClose();
      },
    },
    {
      id: 'ws_reasoning',
      title: 'Desk 04: Reasoning DAG & Proofs',
      category: 'DESKS',
      shortcut: 'G 4',
      icon: <GitBranch className="w-3.5 h-3.5" />,
      action: () => {
        onSelectWorkspace('reasoning');
        onClose();
      },
    },
    {
      id: 'ws_transfer',
      title: 'Desk 05: Cross-Domain Transfer Engine',
      category: 'DESKS',
      shortcut: 'G 5',
      icon: <Repeat className="w-3.5 h-3.5" />,
      action: () => {
        onSelectWorkspace('transfer');
        onClose();
      },
    },
    {
      id: 'ws_hypothesis',
      title: 'Desk 06: Hypothesis Lab',
      category: 'DESKS',
      shortcut: 'G 6',
      icon: <FlaskConical className="w-3.5 h-3.5" />,
      action: () => {
        onSelectWorkspace('hypothesis');
        onClose();
      },
    },
    {
      id: 'ws_validation',
      title: 'Desk 07: Validation Sandbox',
      category: 'DESKS',
      shortcut: 'G 7',
      icon: <CheckCircle className="w-3.5 h-3.5" />,
      action: () => {
        onSelectWorkspace('validation');
        onClose();
      },
    },
    {
      id: 'ws_memory',
      title: 'Desk 08: Validated Memory Registry',
      category: 'DESKS',
      shortcut: 'G 8',
      icon: <Database className="w-3.5 h-3.5" />,
      action: () => {
        onSelectWorkspace('memory');
        onClose();
      },
    },
    {
      id: 'ws_benchmarks',
      title: 'Desk 09: Evaluation & RAG Benchmarks',
      category: 'DESKS',
      shortcut: 'G 9',
      icon: <BarChart3 className="w-3.5 h-3.5" />,
      action: () => {
        onSelectWorkspace('benchmarks');
        onClose();
      },
    },
    {
      id: 'ws_apikeys',
      title: 'Desk 10: API Keys & Endpoints',
      category: 'DEVELOPER',
      icon: <Key className="w-3.5 h-3.5" />,
      action: () => {
        onSelectWorkspace('apikeys');
        onClose();
      },
    },
    {
      id: 'ws_billing',
      title: 'Desk 11: Usage Quota & Billing',
      category: 'SETTINGS',
      icon: <CreditCard className="w-3.5 h-3.5" />,
      action: () => {
        onSelectWorkspace('billing');
        onClose();
      },
    },
    {
      id: 'ws_settings',
      title: 'Desk 12: Profile & Preferences',
      category: 'SETTINGS',
      icon: <Settings className="w-3.5 h-3.5" />,
      action: () => {
        onSelectWorkspace('settings');
        onClose();
      },
    },
  ];

  const filteredCommands = commands.filter((cmd) =>
    cmd.title.toLowerCase().includes(query.toLowerCase()) ||
    cmd.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % (filteredCommands.length || 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredCommands.length) % (filteredCommands.length || 1));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          filteredCommands[selectedIndex].action();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, filteredCommands]);

  return (
    <MacDialog isOpen={isOpen} onClose={onClose} title="COMMAND_PALETTE.DA" maxWidth="max-w-lg">
      <div className="space-y-3 font-mono">
        {/* Search bar inside dialog */}
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-[#777568] absolute left-3 pointer-events-none" />
          <input
            autoFocus
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a command or jump to desk..."
            className="w-full text-xs sm:text-sm bg-[#FDFBF7] border-2 border-[#252820] pl-9 pr-3 py-2 text-[#252820] focus:outline-none shadow-[2px_2px_0px_#252820]"
          />
        </div>

        {/* Results list */}
        <div className="max-h-64 overflow-y-auto border-2 border-[#252820] divide-y divide-[#252820]/20 bg-[#FDFBF7]">
          {filteredCommands.length === 0 ? (
            <div className="p-4 text-center text-xs text-[#777568]">
              NO MATCHING COMMANDS FOUND.
            </div>
          ) : (
            filteredCommands.map((cmd, idx) => (
              <div
                key={cmd.id}
                onClick={cmd.action}
                onMouseEnter={() => setSelectedIndex(idx)}
                className={`p-2.5 flex items-center justify-between text-xs cursor-pointer select-none ${
                  selectedIndex === idx
                    ? 'bg-[#EAE2CF] font-bold text-[#252820] border-l-4 border-[#252820]'
                    : 'text-[#5A584D]'
                }`}
              >
                <div className="flex items-center gap-2.5 truncate">
                  <span>{cmd.icon}</span>
                  <span className="truncate">{cmd.title}</span>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-[9px] uppercase font-bold text-[#777568] px-1 py-0.5 border border-[#252820]/20 bg-[#EAE2CF]">
                    {cmd.category}
                  </span>
                  {cmd.shortcut && (
                    <span className="text-[10px] text-[#252820] font-bold">
                      {cmd.shortcut}
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="flex items-center justify-between text-[10px] text-[#777568] pt-1 border-t border-[#252820]/20">
          <span>NAVIGATION: [↑/↓] TO SELECT &bull; [ENTER] TO EXECUTE</span>
          <span>[ESC] TO CLOSE</span>
        </div>
      </div>
    </MacDialog>
  );
};
