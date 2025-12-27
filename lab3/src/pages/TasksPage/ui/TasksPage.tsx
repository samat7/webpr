import React from 'react';
import { TodoList } from '@widgets/TodoList/ui/TodoList';

export const TasksPage = () => {
    return (
        <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-slate-900 text-slate-200">
            {/* Background Blobs */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-100px] left-[-100px] w-[500px] h-[500px] bg-indigo-600/30 rounded-full blur-[100px] animate-pulse"></div>
                <div className="absolute bottom-[-50px] right-[-50px] w-[400px] h-[400px] bg-pink-600/30 rounded-full blur-[100px] animate-pulse delay-1000"></div>
                <div className="absolute bottom-[20%] left-[20%] w-[250px] h-[250px] bg-cyan-600/30 rounded-full blur-[100px] animate-pulse delay-2000"></div>
            </div>

            <TodoList />
        </div>
    );
};
