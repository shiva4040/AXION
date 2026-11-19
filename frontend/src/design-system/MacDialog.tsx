import React, { useEffect } from 'react';
import { MacWindow } from './MacWindow';

export interface MacDialogProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: string;
}

export const MacDialog: React.FC<MacDialogProps> = ({
  isOpen,
  onClose,
  title = 'ALERT.DLG',
  children,
  footer,
  maxWidth = 'max-w-md',
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-[#252820]/40 backdrop-blur-2xs transition-opacity"
        onClick={onClose}
      />

      {/* Centered Modal Window */}
      <div className={`relative z-10 w-full ${maxWidth}`}>
        <MacWindow title={title} onClose={onClose} shadowSize="lg" footer={footer}>
          {children}
        </MacWindow>
      </div>
    </div>
  );
};
