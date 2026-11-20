import React, { useState, useEffect } from 'react';
import { Navigation } from './components/Navigation';
import { Homepage } from './components/Homepage';
import { LoadingView } from './components/LoadingView';
import { AnswerWorkspace } from './components/AnswerWorkspace';
import { KnowledgeLibrary } from './components/workspaces/KnowledgeLibrary';
import { KnowledgeGraphWorkspace } from './components/workspaces/KnowledgeGraphWorkspace';
import { ResearchAssistant } from './components/workspaces/ResearchAssistant';
import { ReasoningWorkspace } from './components/workspaces/ReasoningWorkspace';
import { CrossDomainTransferWorkspace } from './components/workspaces/CrossDomainTransferWorkspace';
import { HypothesisLab } from './components/workspaces/HypothesisLab';
import { ValidationWorkspace } from './components/workspaces/ValidationWorkspace';
import { MemoryWorkspace } from './components/workspaces/MemoryWorkspace';
import { ResearchHistoryWorkspace } from './components/workspaces/ResearchHistoryWorkspace';
import { askQuestion } from './api/client';
import { ResearchAnswer, WorkspaceId, ENGINE_METADATA } from './types';
import { X } from 'lucide-react';
import { initGlobalClickSound } from './utils/sound';

export const App: React.FC = () => {
  const [activeWorkspace, setActiveWorkspace] = useState<WorkspaceId>('ask');
  const [currentAnswer, setCurrentAnswer] = useState<ResearchAnswer | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [historyDrawerOpen, setHistoryDrawerOpen] = useState<boolean>(false);

  useEffect(() => {
    const cleanup = initGlobalClickSound();
    if (typeof window !== 'undefined') {
      (window as any).__AXION_ENGINE__ = ENGINE_METADATA;
    }
    return cleanup;
  }, []);

  const handleAsk = async (query: string, documentId?: string) => {
    setIsLoading(true);
    setActiveWorkspace('ask');
    try {
      const result = await askQuestion(query, documentId);
      setCurrentAnswer(result);
    } catch (err: any) {
      const msg = err?.message || 'Unknown network error';
      alert(msg.startsWith('Investigation failed') ? msg : `Investigation failed: ${msg}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewQuestion = () => {
    setCurrentAnswer(null);
    setActiveWorkspace('ask');
  };

  const handleSelectHistoryAnswer = (ans: ResearchAnswer) => {
    setCurrentAnswer(ans);
    setActiveWorkspace('ask');
    setHistoryDrawerOpen(false);
  };

  return (
    <div className="min-h-screen bg-[#EFE6D2] text-[#211E19] flex flex-col font-mono selection:bg-[#211E19] selection:text-[#FBF5E6] axion-desk-grid">
      {/* 80px Top Navigation Bar matching reference image */}
      <Navigation
        activeWorkspace={activeWorkspace}
        onSelectWorkspace={(ws) => {
          setActiveWorkspace(ws);
          if (ws !== 'ask') setCurrentAnswer(null);
        }}
        onOpenHistory={() => setHistoryDrawerOpen(true)}
        onGoHome={handleNewQuestion}
      />

      {/* Main Workspace Router */}
      <div className="flex-1 flex flex-col justify-center">
        {activeWorkspace === 'ask' && (
          isLoading ? (
            <LoadingView />
          ) : currentAnswer ? (
            <AnswerWorkspace
              answerData={currentAnswer}
              onNewQuestion={handleNewQuestion}
            />
          ) : (
            <Homepage onSubmitQuestion={handleAsk} isLoading={isLoading} />
          )
        )}

        {activeWorkspace === 'library' && <KnowledgeLibrary />}
        {activeWorkspace === 'graph' && <KnowledgeGraphWorkspace />}
        {activeWorkspace === 'assistant' && (
          <ResearchAssistant onRunInvestigation={handleAsk} isLoading={isLoading} />
        )}
        {activeWorkspace === 'reasoning' && <ReasoningWorkspace />}
        {activeWorkspace === 'transfer' && <CrossDomainTransferWorkspace />}
        {activeWorkspace === 'hypothesis' && <HypothesisLab />}
        {activeWorkspace === 'validation' && <ValidationWorkspace />}
        {activeWorkspace === 'memory' && <MemoryWorkspace />}
        {activeWorkspace === 'history' && (
          <div className="w-full max-w-4xl mx-auto px-4 py-8">
            <ResearchHistoryWorkspace onSelectAnswer={handleSelectHistoryAnswer} />
          </div>
        )}
      </div>

      {/* Slide-Over Quick History Drawer */}
      {historyDrawerOpen && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div
            className="fixed inset-0 bg-[#29251F]/40 backdrop-blur-2xs transition-opacity"
            onClick={() => setHistoryDrawerOpen(false)}
          />
          <div className="relative w-full max-w-md bg-[#F9F3E6] h-full shadow-[6px_0px_0px_#29251F] p-6 overflow-y-auto border-l-2 border-[#29251F] z-10 flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b-2 border-[#29251F] mb-4">
              <span className="font-mono text-xs font-bold uppercase tracking-wider text-[#211E19]">
                INVESTIGATION LOG // ARCHIVE
              </span>
              <button
                onClick={() => setHistoryDrawerOpen(false)}
                className="p-1 border border-[#29251F] bg-[#F3EBD8] hover:bg-[#29251F] hover:text-white transition-none"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1">
              <ResearchHistoryWorkspace onSelectAnswer={handleSelectHistoryAnswer} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
