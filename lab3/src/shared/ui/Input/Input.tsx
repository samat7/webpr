import React, { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> { }

export const Input: React.FC<InputProps> = ({ className = '', ...props }) => {
    return (
        <input
            className={`
        w-full bg-slate-900/60 border border-white/10 rounded-xl px-4 py-3
        text-white placeholder-slate-400
        focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500
        transition-all duration-300
        ${className}
      `}
            {...props}
        />
    );
};
