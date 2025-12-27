import React, { useState, useEffect } from 'react';
import TodoItem from './components/TodoItem';

const App = () => {
    // State initialization
    const [tasks, setTasks] = useState(() => {
        const saved = localStorage.getItem('lab2_tasks');
        return saved ? JSON.parse(saved) : [];
    });
    const [inputValue, setInputValue] = useState('');

    // Effect to save tasks
    useEffect(() => {
        localStorage.setItem('lab2_tasks', JSON.stringify(tasks));
    }, [tasks]);

    // Handlers
    const addTask = (e) => {
        e.preventDefault();
        if (!inputValue.trim()) return;

        const newTask = {
            id: Date.now(),
            text: inputValue,
            completed: false
        };

        setTasks([...tasks, newTask]);
        setInputValue('');
    };

    const toggleTask = (id) => {
        setTasks(tasks.map(task =>
            task.id === id ? { ...task, completed: !task.completed } : task
        ));
    };

    const deleteTask = (id) => {
        setTasks(tasks.filter(task => task.id !== id));
    };

    const clearAll = () => {
        setTasks([]);
    };

    const activeCount = tasks.filter(t => !t.completed).length;

    // Helper for declension (Russian)
    const getDeclension = (number) => {
        const lastDigit = number % 10;
        const lastTwoDigits = number % 100;

        if (lastTwoDigits >= 11 && lastTwoDigits <= 19) return '';
        if (lastDigit === 1) return 'а';
        if (lastDigit >= 2 && lastDigit <= 4) return 'и';
        return '';
    };

    return (
        <div className="app-container">
            <div className="background-blobs">
                <div className="blob blob-1"></div>
                <div className="blob blob-2"></div>
                <div className="blob blob-3"></div>
            </div>

            <main className="container">
                <header className="app-header">
                    <h1>React Tasks</h1>
                    <p>Лабораторная работа №2</p>
                </header>

                <section className="todo-card">
                    <form onSubmit={addTask} className="todo-form">
                        <input
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            placeholder="Что нужно сделать?"
                        />
                        <button type="submit" className="add-btn" aria-label="Добавить">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M12 5V19M5 12H19" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>
                    </form>

                    <div className="todo-list-container">
                        {tasks.length === 0 ? (
                            <div className="empty-state">
                                <p>Список задач пуст. Добавьте что-нибудь!</p>
                            </div>
                        ) : (
                            <ul className="todo-list">
                                {tasks.map(task => (
                                    <TodoItem
                                        key={task.id}
                                        task={task}
                                        onToggle={() => toggleTask(task.id)}
                                        onDelete={() => deleteTask(task.id)}
                                    />
                                ))}
                            </ul>
                        )}
                    </div>

                    <div className="todo-footer">
                        <span>{activeCount} задач{getDeclension(activeCount)}</span>
                        <button onClick={clearAll} className="text-btn">Очистить все</button>
                    </div>
                </section>
            </main>
        </div>
    );
};

export default App;
