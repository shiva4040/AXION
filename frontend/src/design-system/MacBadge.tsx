import React from 'react';

export interface MacBadgeProps {
  variant?: 'vermilion' | 'teal' | 'amber' | 'ink' | 'paper';
  isStamp?: boolean;
  size?: 'sm' | 'md';
  children: React.ReactNode;
  className?: string;
}

export const MacBadge: React.FC<MacBadgeProps> = ({
  variant = 'ink',
  isStamp = false,
  size = 'md',
  children,
  className = '',
}) => {
  const variantClasses = {
    vermilion: 'border-[#C0392B] text-[#C0392B] bg-[#FBEBE9]',
    teal: 'border-[#2B7A78] text-[#2B7A78] bg-[#EAF4F3]',
    amber: 'border-[#D9822B] text-[#D9822B] bg-[#FAF2E8]',
    ink: 'border-[#252820] text-[#252820] bg-[#EAE2CF]',
    paper: 'border-[#252820] text-[#252820] bg-[#FDFBF7]',
  }[variant];

  const sizeClasses = {
    sm: 'text-[9px] px-1.5 py-0.2',
    md: 'text-[10px] px-2 py-0.5',
  }[size];

  const stampRotation = isStamp ? 'rotate-[-2deg] shadow-[1px_1px_0px_#252820]' : '';

  return (
    <span
      className={`inline-flex items-center gap-1 font-mono uppercase font-bold tracking-widest border-2 select-none ${variantClasses} ${sizeClasses} ${stampRotation} ${className}`}
    >
      {children}
    </span>
  );
};
