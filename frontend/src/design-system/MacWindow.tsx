import React from 'react';

export interface MacWindowProps {
  title?: string;
  onClose?: () => void;
  onZoom?: () => void;
  className?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  shadowSize?: 'sm' | 'md' | 'lg';
}

export const MacWindow: React.FC<MacWindowProps> = ({
  title = 'WINDOW.TXT',
  onClose,
  onZoom,
  className = '',
  children,
  footer,
  shadowSize = 'md',
}) => {
  const shadowClass = {
    sm: 'shadow-[2px_2px_0px_#252820]',
    md: 'shadow-[4px_4px_0px_#252820]',
    lg: 'shadow-[6px_6px_0px_#252820]',
  }[shadowSize];

  return (
    <div
      className={`border-2 border-[#252820] bg-[#FDFBF7] ${shadowClass} flex flex-col overflow-hidden select-text ${className}`}
    >
      {/* Classic Mac System 7 Titlebar */}
      <div className="relative h-7 border-b-2 border-[#252820] bg-[#EAE2CF] flex items-center justify-between px-2 select-none">
        {/* Pinstripe Background Layer */}
        <div
          className="absolute inset-0 pointer-events-none opacity-85"
          style={{
            background:
              'repeating-linear-gradient(to bottom, transparent 0px, transparent 2px, #252820 2px, #252820 3px)',
          }}
        />

        {/* Left Close Box */}
        <div className="relative z-10 flex items-center">
          {onClose ? (
            <button
              onClick={onClose}
              className="w-3.5 h-3.5 border-2 border-[#252820] bg-[#FDFBF7] hover:bg-[#252820] transition-none flex items-center justify-center cursor-pointer active:translate-x-[1px] active:translate-y-[1px]"
              aria-label="Close window"
              title="Close"
            />
          ) : (
            <div className="w-3.5 h-3.5 border-2 border-[#252820] bg-[#FDFBF7]" />
          )}
        </div>

        {/* Center Title Pill */}
        <div className="relative z-10 px-3 py-0.5 bg-[#FDFBF7] border-2 border-[#252820] font-mono text-[11px] font-bold tracking-wider text-[#252820] uppercase shadow-[1px_1px_0px_#252820]">
          {title}
        </div>

        {/* Right Controls (Zoom / Collapse) */}
        <div className="relative z-10 flex items-center gap-1">
          {onZoom && (
            <button
              onClick={onZoom}
              className="w-3.5 h-3.5 border-2 border-[#252820] bg-[#FDFBF7] hover:bg-[#EAE2CF] flex items-center justify-center cursor-pointer active:translate-x-[1px] active:translate-y-[1px]"
              aria-label="Zoom window"
              title="Zoom"
            >
              <span className="w-1.5 h-1.5 border border-[#252820]" />
            </button>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 p-4 sm:p-5 overflow-auto text-[#252820] font-mono">{children}</div>

      {/* Optional Window Footer / Action Bar */}
      {footer && (
        <div className="border-t-2 border-[#252820] bg-[#EAE2CF] p-3 flex items-center justify-between gap-3">
          {footer}
        </div>
      )}
    </div>
  );
};
