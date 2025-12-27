document.addEventListener('DOMContentLoaded', () => {
    
    const todoForm = document.getElementById('todo-form');
    const todoInput = document.getElementById('todo-input');
    const todoList = document.getElementById('todo-list');
    const taskCountSpan = document.getElementById('task-count');
    const clearAllBtn = document.getElementById('clear-all');
    const emptyState = document.querySelector('.empty-state');

   
    let tasks = [];


    function renderTasks() {
       
        todoList.innerHTML = '';

        if (tasks.length === 0) {
            todoList.appendChild(emptyState);
            emptyState.style.display = 'block';
        } else {
           
            tasks.forEach((task, index) => {
                const li = document.createElement('li');
                li.className = `todo-item ${task.completed ? 'completed' : ''}`;
                li.setAttribute('data-id', task.id);

                li.innerHTML = `
                    <div class="checkbox" role="button"></div>
                    <span class="task-text">${escapeHtml(task.text)}</span>
                    <button class="delete-btn" aria-label="Удалить задачу">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6"/>
                        </svg>
                    </button>
                `;

            
                const checkbox = li.querySelector('.checkbox');
                checkbox.addEventListener('click', () => toggleTask(task.id));
                
                const deleteBtn = li.querySelector('.delete-btn');
                deleteBtn.addEventListener('click', (e) => {
                    e.stopPropagation(); // prevent triggering row click if we had one
                    deleteTask(task.id);
                });

                todoList.appendChild(li);
            });
        }

        updateCount();
    }


    function addTask(text) {
        const newTask = {
            id: Date.now(),
            text: text,
            completed: false
        };
        tasks.push(newTask);
        renderTasks();
        saveTasks();
    }


    function toggleTask(id) {
        tasks = tasks.map(task => 
            task.id === id ? { ...task, completed: !task.completed } : task
        );
        renderTasks();
        saveTasks();
    }

    // удаление
    function deleteTask(id) {
        tasks = tasks.filter(task => task.id !== id);
        renderTasks();
        saveTasks();
    }

    // очистка
    function clearAll() {
        tasks = [];
        renderTasks();
        saveTasks();
    }

    // обновление счетчика
    function updateCount() {
        const activeCount = tasks.filter(t => !t.completed).length;
        taskCountSpan.textContent = `${activeCount} задач${getDeclension(activeCount)}`;
    }

    // окончания
    function getDeclension(number) {
        const lastDigit = number % 10;
        const lastTwoDigits = number % 100;
        
        if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
            return ''; // задач
        }
        if (lastDigit === 1) {
            return 'а'; // задача
        }
        if (lastDigit >= 2 && lastDigit <= 4) {
            return 'и'; // задачи
        }
        return ''; // задач
    }

    // экранирование
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // сохранение и загрузка
    function saveTasks() {
        localStorage.setItem('lab1_tasks', JSON.stringify(tasks));
    }

    function loadTasks() {
        const stored = localStorage.getItem('lab1_tasks');
        if (stored) {
            tasks = JSON.parse(stored);
            renderTasks();
        }
    }

    // события
    todoForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = todoInput.value.trim();
        if (text) {
            addTask(text);
            todoInput.value = '';
        }
    });

    clearAllBtn.addEventListener('click', clearAll);

    loadTasks();
});
