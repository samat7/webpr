import React from 'react';
import { Task } from '../model/types';

interface TaskCardProps {
    task: Task;
    actions?: React.ReactNode;
    onToggle?: () => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({ task, actions, onToggle }) => {
    return (
        <div className={`
      group flex items-center justify-between
      p-4 mb-3 rounded-xl
      bg-white/5 border border-white/5
      hover:bg-white/10 hover:translate-x-1
      transition-all duration-300 animate-fade-in
      ${task.completed ? 'opacity-60' : ''}
    `}>
            <div className="flex items-center gap-3 flex-1">
                <div
                    onClick={onToggle}
                    className={`
            w-5 h-5 rounded-md border-2 cursor-pointer
            flex items-center justify-center
            transition-all duration-200
            ${task.completed
                            ? 'bg-indigo-600 border-indigo-600'
                            : 'border-slate-400 group-hover:border-indigo-500'}
          `}
                >
                    {task.completed && (
                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                    )}
                </div>
                <span className={`
          text-base font-medium transition-all duration-300
          ${task.completed ? 'text-slate-500 line-through' : 'text-slate-100'}
        `}>
                    {task.text}
                </span>
            </div>

            {actions && (
                <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    {actions}
                </div>
            )}
        </div>
    );
};
