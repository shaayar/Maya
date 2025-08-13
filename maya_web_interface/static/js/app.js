// Chat API Service
class ChatAPI {
    constructor() {
        this.baseUrl = '/api/chat';
    }

    async sendMessage(message, conversationId = null) {
        try {
            const response = await fetch(this.baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message,
                    conversation_id: conversationId
                })
            });

            if (!response.ok) {
                throw new Error(`API request failed with status ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                data: data.response,
                conversationId: data.conversation_id || conversationId
            };
        } catch (error) {
            console.error('Error sending message:', error);
            return {
                success: false,
                error: error.message || 'Failed to get response from the server'
            };
        }
    }
}

// Todo Management
class TodoManager {
    constructor() {
        this.todos = JSON.parse(localStorage.getItem('maya_todos')) || [];
    }

    addTodo(todo) {
        const newTodo = {
            id: Date.now(),
            title: todo.title,
            description: todo.description || '',
            dueDate: todo.dueDate || null,
            priority: todo.priority || 'medium',
            completed: false,
            createdAt: new Date().toISOString()
        };
        this.todos.push(newTodo);
        this.save();
        return newTodo;
    }

    getTodos() {
        return [...this.todos];
    }

    toggleComplete(id) {
        const todo = this.todos.find(t => t.id === id);
        if (todo) {
            todo.completed = !todo.completed;
            this.save();
        }
    }

    deleteTodo(id) {
        this.todos = this.todos.filter(todo => todo.id !== id);
        this.save();
    }

    save() {
        localStorage.setItem('maya_todos', JSON.stringify(this.todos));
    }
}

// Main Application Class
class MayaWebApp {
    constructor() {
        // DOM Elements
        this.chatForm = document.getElementById('chat-form');
        this.messageInput = document.getElementById('message-input');
        this.chatMessages = document.getElementById('chat-messages');
        this.voiceToggle = document.getElementById('voice-toggle');
        this.clearChatBtn = document.getElementById('clear-chat');
        this.navItems = document.querySelectorAll('[data-section]');
        this.contentSections = document.querySelectorAll('.content-section');
        
        // State
        this.isListening = false;
        this.messages = [];
        this.conversationId = null;
        this.isProcessing = false;
        this.todoManager = new TodoManager();
        this.chatAPI = new ChatAPI();
        
        // Initialize the app
        this.initializeEventListeners();
        this.loadChatHistory();
        this.adjustTextareaHeight();
    }
    
    // Initialize event listeners
    initializeEventListeners() {
        // Chat form submission
        if (this.chatForm) {
            this.chatForm.addEventListener('submit', (e) => this.handleSendMessage(e));
        }
        
        // Input auto-resize
        if (this.messageInput) {
            this.messageInput.addEventListener('input', () => this.adjustTextareaHeight());
        }
        
        // Voice toggle
        if (this.voiceToggle) {
            this.voiceToggle.addEventListener('click', () => this.toggleVoiceInput());
        }
        
        // Clear chat
        if (this.clearChatBtn) {
            this.clearChatBtn.addEventListener('click', () => this.clearChat());
        }
        
        // Navigation
        this.navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.currentTarget.dataset.section;
                this.showSection(section);
            });
        });
        
        // Setup todo modal
        this.setupTodoModal();
    }
    
    // Handle sending a message
    async handleSendMessage(e) {
        e.preventDefault();
        const message = this.messageInput.value.trim();
        
        if (!message || this.isProcessing) return;
        
        // Add user message to chat
        const userMessage = { 
            role: 'user', 
            content: message,
            timestamp: new Date().toISOString()
        };
        
        this.messages.push(userMessage);
        this.renderMessage(userMessage);
        this.saveChatHistory();
        
        // Clear input
        this.messageInput.value = '';
        this.adjustTextareaHeight();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            this.isProcessing = true;
            
            // Send message to API
            const response = await this.chatAPI.sendMessage(message, this.conversationId);
            
            if (response.success) {
                // Update conversation ID if this is a new conversation
                if (response.conversationId) {
                    this.conversationId = response.conversationId;
                }
                
                // Add AI response to chat
                const aiMessage = { 
                    role: 'assistant', 
                    content: response.data,
                    timestamp: new Date().toISOString()
                };
                
                this.messages.push(aiMessage);
                this.saveChatHistory();
                
                // Remove typing indicator and show response
                this.hideTypingIndicator();
                this.renderMessage(aiMessage);
            } else {
                throw new Error(response.error || 'Failed to get response');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.showError('Failed to get response. Please try again.');
        } finally {
            this.isProcessing = false;
        }
    }
    
    // Show typing indicator
    showTypingIndicator() {
        // Remove any existing typing indicators
        this.hideTypingIndicator();
        
        const typingHtml = `
            <div class="message assistant" id="typing-indicator">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.chatMessages.insertAdjacentHTML('beforeend', typingHtml);
        this.scrollToBottom();
    }
    
    // Hide typing indicator
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Show error message
    showError(message) {
        const errorHtml = `
            <div class="message error">
                <div class="text-red-600">${message}</div>
            </div>
        `;
        this.chatMessages.insertAdjacentHTML('beforeend', errorHtml);
        this.scrollToBottom();
    }
    
    // Render a message
    renderMessage(message) {
        if (message.role === 'assistant') {
            this.hideTypingIndicator();
        }
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.role} ${message.error ? 'error' : ''}`;
        
        const timestamp = message.timestamp ? new Date(message.timestamp) : new Date();
        const timeString = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageElement.innerHTML = `
            <div class="flex items-start">
                <div class="flex-1">
                    <div class="message-content">${message.content}</div>
                    <div class="timestamp">${timeString}</div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    // Add a message to the chat
    addMessage(role, content) {
        const message = {
            role,
            content,
            timestamp: new Date().toISOString()
        };
        
        this.messages.push(message);
        this.renderMessage(message);
        this.saveChatHistory();
    }
    
    // Save chat history to localStorage
    saveChatHistory() {
        localStorage.setItem('maya_chat_history', JSON.stringify({
            messages: this.messages,
            conversationId: this.conversationId
        }));
    }
    
    // Load chat history from localStorage
    loadChatHistory() {
        const savedChat = localStorage.getItem('maya_chat_history');
        if (savedChat) {
            try {
                const { messages, conversationId } = JSON.parse(savedChat);
                this.messages = messages || [];
                this.conversationId = conversationId || null;
                this.renderChatHistory();
            } catch (e) {
                console.error('Error loading chat history:', e);
                this.messages = [];
                this.conversationId = null;
            }
        }
    }
    
    // Load and display todos with animations
    async loadTodos() {
        const todosContainer = document.getElementById('todos-container');
        if (!todosContainer) return;
        
        const todos = this.todoManager.getTodos();
        
        if (todos.length === 0) {
            todosContainer.innerHTML = `
                <div class="text-gray-500 text-center py-4">
                    No tasks yet. Click "Add Task" to get started.
                </div>
            `;
            return;
        }
        
        // Store current todo IDs to check for removals
        const currentTodoElements = [...todosContainer.querySelectorAll('.todo-item')];
        const currentTodoIds = currentTodoElements.map(el => parseInt(el.dataset.id));
        const newTodoIds = todos.map(todo => todo.id);
        
        // Animate out removed todos
        currentTodoElements.forEach(el => {
            const id = parseInt(el.dataset.id);
            if (!newTodoIds.includes(id)) {
                window.mayaAnimations?.animateTodoOut(el);
            }
        });
        
        // Create new todo elements for added todos
        const newTodos = todos.filter(todo => !currentTodoIds.includes(todo.id));
        const fragment = document.createDocumentFragment();
        
        newTodos.forEach(todo => {
            const todoElement = document.createElement('div');
            todoElement.className = 'todo-item bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-2 flex items-center justify-between';
            todoElement.dataset.id = todo.id;
            todoElement.innerHTML = `
                <div class="flex items-center space-x-3 flex-1">
                    <input type="checkbox" 
                           ${todo.completed ? 'checked' : ''} 
                           class="todo-toggle w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
                           data-id="${todo.id}">
                    <div class="flex-1">
                        <div class="todo-title font-medium ${todo.completed ? 'line-through text-gray-400' : 'text-gray-900 dark:text-white'}">
                            ${todo.title}
                        </div>
                        ${todo.description ? `
                            <div class="todo-description text-sm text-gray-500 dark:text-gray-400 mt-1">
                                ${todo.description}
                            </div>
                        ` : ''}
                        ${todo.dueDate ? `
                            <div class="todo-due-date text-xs text-gray-400 mt-1">
                                <i class="far fa-calendar-alt mr-1"></i>
                                ${new Date(todo.dueDate).toLocaleDateString()}
                            </div>
                        ` : ''}
                    </div>
                </div>
                <button class="todo-delete text-gray-400 hover:text-red-500 transition-colors p-2" data-id="${todo.id}">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            fragment.appendChild(todoElement);
        });
        
        // Append new todos to container with animation
        if (fragment.children.length > 0) {
            todosContainer.appendChild(fragment);
            
            // Animate in new todos
            Array.from(fragment.children).forEach((todoEl, index) => {
                todoEl.style.opacity = '0';
                todoEl.style.transform = 'translateY(20px)';
                
                window.mayaAnimations?.animateTodoIn(todoEl, () => {
                    // Add hover effect after animation
                    todoEl.addEventListener('mouseenter', () => {
                        gsap.to(todoEl, { 
                            y: -2, 
                            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                            duration: 0.2,
                            ease: 'power2.out'
                        });
                    });
                    
                    todoEl.addEventListener('mouseleave', () => {
                        gsap.to(todoEl, { 
                            y: 0, 
                            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
                            duration: 0.2,
                            ease: 'power2.out'
                        });
                    });
                });
            });
        }
        
        // Update existing todos
        todos.forEach(todo => {
            const existingEl = todosContainer.querySelector(`[data-id="${todo.id}"]`);
            if (existingEl) {
                // Update completed state with animation
                const titleEl = existingEl.querySelector('.todo-title');
                if (titleEl) {
                    gsap.to(titleEl, {
                        textDecoration: todo.completed ? 'line-through' : 'none',
                        color: todo.completed ? '#9ca3af' : '#111827',
                        duration: 0.2,
                        ease: 'power2.out'
                    });
                }
            }
        });
        
        // Add event listeners for todo actions
        document.querySelectorAll('.todo-toggle').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const id = parseInt(e.target.dataset.id);
                const todoItem = e.target.closest('.todo-item');
                
                // Animate the toggle
                gsap.to(todoItem, {
                    scale: 0.98,
                    duration: 0.1,
                    yoyo: true,
                    repeat: 1,
                    onComplete: () => {
                        this.todoManager.toggleComplete(id);
                        this.loadTodos();
                    }
                });
            });
        });
        
        document.querySelectorAll('.todo-delete').forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = parseInt(e.currentTarget.dataset.id);
                const todoItem = e.currentTarget.closest('.todo-item');
                
                if (confirm('Are you sure you want to delete this task?')) {
                    window.mayaAnimations?.animateTodoOut(todoItem, () => {
                        this.todoManager.deleteTodo(id);
                        this.loadTodos();
                    });
                }
            });
        });
    }
    
    // Render all chat messages
    renderChatHistory() {
        if (!this.chatMessages) return;
        
        this.chatMessages.innerHTML = '';
        this.messages.forEach(msg => this.renderMessage(msg));
        this.scrollToBottom();
    }
    
    // Clear chat history
    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            this.messages = [];
            this.conversationId = null;
            if (this.chatMessages) {
                this.chatMessages.innerHTML = '';
            }
            localStorage.removeItem('maya_chat_history');
        }
    }
    
    // Toggle voice input
    toggleVoiceInput() {
        if (this.isListening) {
            this.stopVoiceInput();
        } else {
            this.startVoiceInput();
        }       
    }
    
    // Setup todo modal with animations
    setupTodoModal() {
        const modal = document.getElementById('todo-modal');
        const openModalBtn = document.getElementById('open-todo-modal');
        const closeModalBtns = document.querySelectorAll('.modal-close');
        const todoForm = document.getElementById('todo-form');

        // Open modal with animation
        if (openModalBtn) {
            openModalBtn.addEventListener('click', () => {
                if (modal) {
                    window.mayaAnimations?.animateModalIn(modal);
                    document.getElementById('task-title')?.focus();
                }
            });
        }

        // Close modal with animation
        const closeModal = () => {
            if (modal) {
                window.mayaAnimations?.animateModalOut(modal)
                    .then(() => {
                        if (todoForm) todoForm.reset();
                    });
            }
        };

        // Close modal buttons
        closeModalBtns.forEach(btn => {
            btn.addEventListener('click', closeModal);
        });

        // Close when clicking outside modal
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        // Handle form submission
        if (todoForm) {
            todoForm.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const title = document.getElementById('task-title')?.value.trim();
                const description = document.getElementById('task-description')?.value.trim() || '';
                const dueDate = document.getElementById('task-due-date')?.value || null;
                const priority = document.getElementById('task-priority')?.value || 'medium';

                if (title) {
                    this.todoManager.addTodo({
                        title,
                        description,
                        dueDate,
                        priority
                    });

                    // Reset form and close modal
                    todoForm.reset();
                    if (modal) modal.style.display = 'none';
                    
                    // Refresh todo list
                    this.loadTodos();
                }
            });
        }
    }
    
    // Start voice input
    startVoiceInput() {
        // Implementation for starting voice input
        this.isListening = true;
        if (this.voiceToggle) {
            this.voiceToggle.classList.add('text-red-500');
            this.voiceToggle.innerHTML = '<i class="fas fa-microphone-slash"></i>';
        }
        
        // TODO: Add actual voice recognition implementation
        console.log('Voice input started');
    }
    
    // Stop voice input
    stopVoiceInput() {
        this.isListening = false;
        if (this.voiceToggle) {
            this.voiceToggle.classList.remove('text-red-500');
            this.voiceToggle.innerHTML = '<i class="fas fa-microphone"></i>';
        }
        
        // TODO: Add actual voice recognition stop
        console.log('Voice input stopped');
    }
    
    // Show a specific section with animation
    showSection(sectionId) {
        // Update active nav item with animation
        this.navItems.forEach(item => {
            if (item.dataset.section === sectionId) {
                gsap.to(item, { 
                    backgroundColor: 'rgba(74, 144, 226, 0.1)',
                    duration: 0.2,
                    ease: 'power2.out'
                });
                item.classList.add('active');
            } else {
                gsap.to(item, { 
                    backgroundColor: 'transparent',
                    duration: 0.2,
                    ease: 'power2.out'
                });
                item.classList.remove('active');
            }
        });
        
        // Find current and new sections
        const currentSection = this.contentSections.find(s => !s.classList.contains('hidden'));
        const newSection = document.getElementById(`${sectionId}-section`);
        
        if (!newSection) return;
        
        // If no section is currently shown, just show the new one
        if (!currentSection) {
            newSection.style.display = 'block';
            window.mayaAnimations?.switchSection(newSection, newSection);
            return;
        }
        
        // If clicking the same section, do nothing
        if (currentSection === newSection) return;
        
        // Animate the section transition
        window.mayaAnimations?.switchSection(currentSection, newSection);
    }
    
    // Adjust textarea height based on content
    adjustTextareaHeight() {
        if (this.messageInput) {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 200) + 'px';
        }
    }
    
    // Scroll chat to bottom
    scrollToBottom() {
        if (this.chatMessages) {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }
}

// Initialize the app when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new MayaWebApp();
});
