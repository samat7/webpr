import React from 'react';

const TodoItem = ({ task, onToggle, onDelete }) => {
    return (
        <li className={`todo-item ${task.completed ? 'completed' : ''}`}>
            <div
                className="checkbox"
                onClick={onToggle}
                role="button"
            ></div>
            <span className="task-text">{task.text}</span>
            <button
                className="delete-btn"
                onClick={(e) => {
                    e.stopPropagation();
                    onDelete();
                }}
                aria-label="Удалить"
            >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            </button>
        </li>
    );
};

export default TodoItem;
