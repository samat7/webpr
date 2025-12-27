import React, { useEffect, useState } from 'react';
import { Task } from '@entities/Task/model/types';
import { TaskCard } from '@entities/Task/ui/TaskCard';
import { AddTask } from '@features/AddTask/ui/AddTask';
import { Button } from '@shared/ui/Button/Button';

export const TodoList = () => {
    const [tasks, setTasks] = useState<Task[]>(() => {
        const saved = localStorage.getItem('lab3_tasks');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        localStorage.setItem('lab3_tasks', JSON.stringify(tasks));
    }, [tasks]);

    const addTask = (text: string) => {
        const newTask: Task = {
            id: Date.now(),
            text,
            completed: false,
        };
        setTasks([...tasks, newTask]);
    };

    const toggleTask = (id: number) => {
        setTasks(tasks.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
    };

    const deleteTask = (id: number) => {
        setTasks(tasks.filter(t => t.id !== id));
    };

    const activeCount = tasks.filter(t => !t.completed).length;

    return (
        <section className="bg-slate-800/70 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl max-w-lg w-full z-10 relative">
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 mb-2">
                    Tasks FSD
                </h1>
                <p className="text-slate-400">Лабораторная работа №3</p>
            </div>

            <AddTask onAdd={addTask} />

            <div className="space-y-1 mb-6 max-h-[400px] overflow-y-auto custom-scrollbar pr-2">
                {tasks.length === 0 ? (
                    <div className="text-center py-10 text-slate-500 italic">
                        Список задач пуст
                    </div>
                ) : (
                    tasks.map(task => (
                        <TaskCard
                            key={task.id}
                            task={task}
                            onToggle={() => toggleTask(task.id)}
                            actions={
                                <Button variant="danger" onClick={() => deleteTask(task.id)}>
                                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                </Button>
                            }
                        />
                    ))
                )}
            </div>

            <div className="flex justify-between items-center pt-6 border-t border-white/10 text-slate-400 text-sm">
                <span>{activeCount} задач осталось</span>
                <Button variant="ghost" onClick={() => setTasks([])} className="text-sm">
                    Очистить все
                </Button>
            </div>
        </section>
    );
};
