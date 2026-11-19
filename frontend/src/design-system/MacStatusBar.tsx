import React from 'react';

export interface MacStatusBarProps {
  statusText?: string;
  statusVariant?: 'ready' | 'busy' | 'error';
  rightText?: string;
  latencyMs?: number;
  className?: string;
}

export const MacStatusBar: React.FC<MacStatusBarProps> = ({
  statusText = 'READY',
  statusVariant = 'ready',
  rightText = 'AXION INTELLIGENCE',
  latencyMs,
  className = '',
}) => {
  const ledColors = {
    ready: 'bg-[#2B7A78]',
    busy: 'bg-[#D9822B] animate-pulse',
    error: 'bg-[#C0392B]',
  }[statusVariant];

  return (
    <footer
      className={`fixed bottom-0 left-0 right-0 h-7 bg-[#EAE2CF] border-t-2 border-[#252820] px-4 flex items-center justify-between text-[11px] font-mono select-none z-30 ${className}`}
    >
      {/* Left Status LED + Label */}
      <div className="flex items-center gap-2">
        <span className={`inline-block w-2.5 h-2.5 border border-[#252820] ${ledColors}`} />
        <span className="font-bold tracking-wider text-[#252820] uppercase">{statusText}</span>
        {latencyMs !== undefined && (
          <span className="text-[#777568] text-[10px] hidden sm:inline">
            // {latencyMs}ms
          </span>
        )}
      </div>

      {/* Right Brand & Platform Tag */}
      <div className="flex items-center gap-3 text-[#5A584D] text-[10px] tracking-widest uppercase">
        <span className="hidden md:inline">SYSTEM 7.5 COGNITIVE CORE</span>
        <span className="text-[#252820] font-bold">{rightText}</span>
      </div>
    </footer>
  );
};
