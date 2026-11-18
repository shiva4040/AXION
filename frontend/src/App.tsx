import React, { useState } from 'react';
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
import { ResearchAnswer, WorkspaceId } from './types';
import { X, ArrowRight } from 'lucide-react';

export const App: React.FC = () => {
  const [activeWorkspace, setActiveWorkspace] = useState<WorkspaceId>('ask');
  const [currentAnswer, setCurrentAnswer] = useState<ResearchAnswer | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [historyDrawerOpen, setHistoryDrawerOpen] = useState<boolean>(false);

  const handleAsk = async (query: string, documentId?: string) => {
    setIsLoading(true);
    setActiveWorkspace('ask');
    try {
      const result = await askQuestion(query, documentId);
      setCurrentAnswer(result);
    } catch (err: any) {
      alert(`Investigation failed: ${err.message}`);
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
    <div className="min-h-screen bg-white text-[#202124] flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900">
      {/* Minimal Top Navigation */}
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
      <div className="flex-1 flex flex-col">
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
          <ResearchHistoryWorkspace onSelectAnswer={handleSelectHistoryAnswer} />
        )}
      </div>

      {/* Slide-Over Quick History Drawer */}
      {historyDrawerOpen && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div
            className="fixed inset-0 bg-black/20 backdrop-blur-2xs transition-opacity"
            onClick={() => setHistoryDrawerOpen(false)}
          />
          <div className="relative w-full max-w-md bg-white h-full shadow-2xl p-6 overflow-y-auto border-l border-gray-100 z-10 flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-gray-100 mb-4">
              <h3 className="text-sm font-bold text-gray-900">Investigation History</h3>
              <button
                onClick={() => setHistoryDrawerOpen(false)}
                className="p-1 text-gray-400 hover:text-gray-600 rounded-lg"
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
