import React from 'react';

export interface MacButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'paper' | 'vermilion' | 'teal' | 'ink' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const MacButton: React.FC<MacButtonProps> = ({
  variant = 'paper',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses =
    'inline-flex items-center justify-center gap-1.5 font-mono uppercase font-bold tracking-wider select-none border-2 border-[#252820] transition-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-[#252820]';

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5 min-h-[26px]',
    md: 'text-xs px-3.5 py-1.5 min-h-[34px]',
    lg: 'text-sm px-5 py-2.5 min-h-[42px]',
  }[size];

  const variantClasses = {
    paper: 'bg-[#FDFBF7] text-[#252820] hover:bg-[#EAE2CF]',
    vermilion: 'bg-[#C0392B] text-white hover:bg-[#A93226]',
    teal: 'bg-[#2B7A78] text-white hover:bg-[#226462]',
    ink: 'bg-[#252820] text-[#F3EEDD] hover:bg-[#3D4036]',
    outline: 'bg-transparent text-[#252820] hover:bg-[#EAE2CF]/60',
  }[variant];

  const shadowClasses = disabled || isLoading
    ? 'opacity-60 cursor-not-allowed shadow-none'
    : 'shadow-[2px_2px_0px_#252820] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none';

  return (
    <button
      className={`${baseClasses} ${sizeClasses} ${variantClasses} ${shadowClasses} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="inline-block animate-pulse font-mono">[ ... ]</span>
      ) : (
        <>
          {leftIcon && <span className="shrink-0">{leftIcon}</span>}
          <span>{children}</span>
          {rightIcon && <span className="shrink-0">{rightIcon}</span>}
        </>
      )}
    </button>
  );
};
