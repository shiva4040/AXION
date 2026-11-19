import React from 'react';

export interface MacInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const MacInput: React.FC<MacInputProps> = ({
  label,
  error,
  helperText,
  leftIcon,
  rightIcon,
  className = '',
  disabled,
  ...props
}) => {
  return (
    <div className="w-full space-y-1">
      {label && (
        <label className="block font-mono text-[11px] font-bold uppercase tracking-wider text-[#252820]">
          {label}
        </label>
      )}

      <div className="relative flex items-center">
        {leftIcon && (
          <span className="absolute left-3 text-[#777568] pointer-events-none">{leftIcon}</span>
        )}
        <input
          disabled={disabled}
          className={`w-full font-mono text-xs sm:text-sm text-[#252820] bg-[#FDFBF7] border-2 border-[#252820] px-3 py-2 shadow-[2px_2px_0px_#252820] placeholder:text-[#A39E8F] focus:outline-none focus:bg-white focus:shadow-[3px_3px_0px_#252820] disabled:bg-[#EAE2CF] disabled:cursor-not-allowed ${
            leftIcon ? 'pl-9' : ''
          } ${rightIcon ? 'pr-9' : ''} ${error ? 'border-[#C0392B]' : ''} ${className}`}
          {...props}
        />
        {rightIcon && (
          <span className="absolute right-3 text-[#777568] pointer-events-none">{rightIcon}</span>
        )}
      </div>

      {error ? (
        <p className="font-mono text-[10px] text-[#C0392B] font-semibold mt-0.5 tracking-wide">
          ERROR: {error}
        </p>
      ) : helperText ? (
        <p className="font-mono text-[10px] text-[#777568] mt-0.5">{helperText}</p>
      ) : null}
    </div>
  );
};

export interface MacTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const MacTextarea: React.FC<MacTextareaProps> = ({
  label,
  error,
  helperText,
  className = '',
  disabled,
  rows = 3,
  ...props
}) => {
  return (
    <div className="w-full space-y-1">
      {label && (
        <label className="block font-mono text-[11px] font-bold uppercase tracking-wider text-[#252820]">
          {label}
        </label>
      )}

      <textarea
        rows={rows}
        disabled={disabled}
        className={`w-full font-mono text-xs sm:text-sm text-[#252820] bg-[#FDFBF7] border-2 border-[#252820] p-3 shadow-[2px_2px_0px_#252820] placeholder:text-[#A39E8F] focus:outline-none focus:bg-white focus:shadow-[3px_3px_0px_#252820] leading-relaxed resize-y disabled:bg-[#EAE2CF] disabled:cursor-not-allowed ${
          error ? 'border-[#C0392B]' : ''
        } ${className}`}
        {...props}
      />

      {error ? (
        <p className="font-mono text-[10px] text-[#C0392B] font-semibold mt-0.5 tracking-wide">
          ERROR: {error}
        </p>
      ) : helperText ? (
        <p className="font-mono text-[10px] text-[#777568] mt-0.5">{helperText}</p>
      ) : null}
    </div>
  );
};
