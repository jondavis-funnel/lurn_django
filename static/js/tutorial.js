// Tutorial App JavaScript
class TutorialApp {
    constructor() {
        this.currentModule = null;
        this.currentLesson = null;
        this.modules = [];
        this.progress = {};
        this.timeTracker = null;
        this.startTime = null;
        
        this.init();
    }
    
    async init() {
        // Load progress from localStorage
        this.loadProgress();
        
        // Load modules
        await this.loadModules();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Check authentication
        this.checkAuth();
        
        // Apply saved theme
        this.applyTheme();
        
        // Handle initial URL routing
        this.handleInitialRoute();
    }
    
    loadProgress() {
        const savedProgress = localStorage.getItem('djangoTutorialProgress');
        if (savedProgress) {
            this.progress = JSON.parse(savedProgress);
        }
    }
    
    saveProgress() {
        localStorage.setItem('djangoTutorialProgress', JSON.stringify(this.progress));
    }
    
    async loadModules() {
        try {
            const response = await fetch('/api/modules/');
            this.modules = await response.json();
            this.renderModulesList();
            this.renderModulesGrid();
            this.updateOverallProgress();
        } catch (error) {
            console.error('Error loading modules:', error);
        }
    }
    
    renderModulesList() {
        const container = document.getElementById('modules-list');
        container.innerHTML = '';
        
        this.modules.forEach(module => {
            const moduleEl = document.createElement('div');
            moduleEl.className = 'module-item';
            
            const headerEl = document.createElement('div');
            headerEl.className = 'module-header';
            const moduleProgress = this.calculateModuleProgress(module);
            headerEl.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <span>${module.title}</span>
                    <small class="module-progress">${moduleProgress}%</small>
                </div>
            `;
            headerEl.onclick = () => this.toggleModule(module.id);
            
            const lessonsEl = document.createElement('div');
            lessonsEl.className = 'lessons-list';
            lessonsEl.id = `module-${module.id}-lessons`;
            lessonsEl.style.display = 'none';
            
            module.lessons.forEach(lesson => {
                const lessonEl = document.createElement('div');
                lessonEl.className = 'lesson-item';
                lessonEl.setAttribute('data-lesson-id', lesson.id);
                if (lesson.is_completed) {
                    lessonEl.classList.add('completed');
                }
                lessonEl.textContent = lesson.title;
                lessonEl.onclick = () => this.loadLesson(module, lesson);
                lessonsEl.appendChild(lessonEl);
            });
            
            moduleEl.appendChild(headerEl);
            moduleEl.appendChild(lessonsEl);
            container.appendChild(moduleEl);
        });
    }
    
    renderModulesGrid() {
        const grid = document.getElementById('modules-grid');
        if (!grid) return;
        
        grid.innerHTML = this.modules.map(module => {
            const completedLessons = module.lessons.filter(lesson => 
                this.isLessonCompleted(lesson.id)
            ).length;
            const totalLessons = module.lessons.length;
            const progressPercent = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;
            
            return `
                <div class="col-md-6">
                    <div class="card h-100 module-card" onclick="window.tutorialApp.showModuleOverview(${module.id})">
                        <div class="card-body">
                            <h5 class="card-title">${module.title}</h5>
                            <p class="card-text">${module.description}</p>
                            <div class="mb-3">
                                <span class="badge bg-primary">${module.estimated_minutes} min</span>
                                <span class="badge bg-secondary">${totalLessons} lessons</span>
                            </div>
                            <div class="progress mb-3">
                                <div class="progress-bar" role="progressbar" style="width: ${progressPercent}%" 
                                     aria-valuenow="${progressPercent}" aria-valuemin="0" aria-valuemax="100">
                                    ${progressPercent}%
                                </div>
                            </div>
                            <button class="btn btn-sm btn-outline-primary" 
                                    onclick="event.stopPropagation(); window.tutorialApp.showModuleOverview(${module.id})">
                                View Module
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    toggleModule(moduleId) {
        const lessonsEl = document.getElementById(`module-${moduleId}-lessons`);
        const isVisible = lessonsEl.style.display !== 'none';
        
        // Close all modules
        document.querySelectorAll('.lessons-list').forEach(el => {
            el.style.display = 'none';
        });
        document.querySelectorAll('.module-header').forEach(el => {
            el.classList.remove('active');
        });
        
        // Open selected module
        if (!isVisible) {
            lessonsEl.style.display = 'block';
            lessonsEl.previousElementSibling.classList.add('active');
        }
        
        // Show module overview page
        const module = this.modules.find(m => m.id === moduleId);
        if (module) {
            this.showModuleOverview(module);
        }
    }
    
    async loadLesson(module, lesson) {
        // Stop time tracking for previous lesson
        this.stopTimeTracking();
        
        this.currentModule = module;
        this.currentLesson = lesson;
        
        // Update URL
        this.updateURL('lesson', { moduleSlug: module.slug, lessonSlug: lesson.slug });
        
        // Update UI
        document.getElementById('welcome-screen').style.display = 'none';
        document.getElementById('progress-dashboard').style.display = 'none';
        document.getElementById('settings-panel').style.display = 'none';
        document.getElementById('lesson-content').style.display = 'block';
        
        // Scroll to top of lesson content
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // Update breadcrumb
        document.getElementById('module-breadcrumb').textContent = module.title;
        document.getElementById('module-breadcrumb').style.cursor = 'pointer';
        document.getElementById('lesson-breadcrumb').textContent = lesson.title;
        document.getElementById('lesson-title').textContent = lesson.title;
        
        // Render lesson content
        document.getElementById('lesson-body').innerHTML = marked.parse(lesson.content);
        
        // Syntax highlighting
        Prism.highlightAll();
        
        // Show code comparison if available
        if (lesson.django_code || lesson.dotnet_code) {
            document.getElementById('code-comparison').style.display = 'block';
            document.getElementById('django-code').textContent = lesson.django_code || '';
            document.getElementById('dotnet-code').textContent = lesson.dotnet_code || '';
            Prism.highlightAll();
        } else {
            document.getElementById('code-comparison').style.display = 'none';
        }
        
        // Show exercise if available
        if (lesson.has_exercise) {
            document.getElementById('exercise-section').style.display = 'block';
            
            // Restore saved exercise code or use starter code
            const savedCode = this.getSavedExerciseCode(lesson.id);
            document.getElementById('exercise-code').value = savedCode || lesson.exercise_starter_code || '';
            
            // Add auto-save for exercise code
            this.setupExerciseAutoSave(lesson.id);
        } else {
            document.getElementById('exercise-section').style.display = 'none';
        }
        
        // Show quiz if available
        if (lesson.quizzes && lesson.quizzes.length > 0) {
            document.getElementById('quiz-section').style.display = 'block';
            this.renderQuizzes(lesson.quizzes);
        } else {
            document.getElementById('quiz-section').style.display = 'none';
        }
        
        // Show and update navigation buttons
        document.getElementById('lesson-navigation').style.display = 'block';
        this.updateNavigationButtons();
        
        // Update active lesson in sidebar
        document.querySelectorAll('.lesson-item').forEach(el => {
            el.classList.remove('active');
        });
        
        // Find and highlight the current lesson in sidebar
        const currentLessonElement = document.querySelector(`[data-lesson-id="${lesson.id}"]`);
        if (currentLessonElement) {
            currentLessonElement.classList.add('active');
        }
        
        // Start time tracking
        this.startTimeTracking();
        
        // Update lesson progress
        this.updateLessonProgress();
    }
    
    renderQuizzes(quizzes) {
        const container = document.getElementById('quiz-container');
        container.innerHTML = '';
        
        quizzes.forEach((quiz, index) => {
            const quizEl = document.createElement('div');
            quizEl.className = 'quiz-question';
            quizEl.innerHTML = `
                <h6>Question ${index + 1}</h6>
                <p>${quiz.question}</p>
                <div class="quiz-options" data-quiz-id="${quiz.id}">
                    ${quiz.options.map((option, i) => `
                        <div class="quiz-option" data-quiz="${quiz.id}" data-answer="${i}">
                            ${option}
                        </div>
                    `).join('')}
                </div>
                <div class="quiz-result" id="quiz-result-${quiz.id}"></div>
            `;
            container.appendChild(quizEl);
        });
        
        // Add click handlers
        document.querySelectorAll('.quiz-option').forEach(el => {
            el.onclick = (e) => {
                const quizId = parseInt(el.dataset.quiz);
                const answer = parseInt(el.dataset.answer);
                if (quizId && answer !== undefined) {
                    this.selectQuizAnswer(quizId, answer);
                } else {
                    console.error('Missing quiz data attributes:', el.dataset);
                }
            };
        });
        
        // Restore previously selected answers from localStorage
        this.restoreQuizAnswers(quizzes);
    }
    
    restoreQuizAnswers(quizzes) {
        const quizResults = JSON.parse(localStorage.getItem('quizResults') || '{}');
        
        quizzes.forEach(quiz => {
            const savedResult = quizResults[quiz.id];
            if (savedResult && savedResult.selected_answer !== undefined) {
                // Restore the visual selection without triggering API call
                const option = document.querySelector(`[data-quiz="${quiz.id}"][data-answer="${savedResult.selected_answer}"]`);
                if (option) {
                    // Clear previous selections
                    option.parentElement.querySelectorAll('.quiz-option').forEach(el => {
                        el.classList.remove('selected', 'correct', 'incorrect');
                    });
                    
                    // Mark as selected and show result
                    option.classList.add('selected');
                    option.classList.add(savedResult.is_correct ? 'correct' : 'incorrect');
                    
                    // Show the result message
                    const resultEl = document.getElementById(`quiz-result-${quiz.id}`);
                    if (resultEl) {
                        resultEl.innerHTML = savedResult.is_correct ? 
                            '<div class="alert alert-success">Correct!</div>' : 
                            '<div class="alert alert-danger">Incorrect. Try again!</div>';
                    }
                }
            }
        });
    }
    
    async selectQuizAnswer(quizId, answer) {
        const option = document.querySelector(`[data-quiz="${quizId}"][data-answer="${answer}"]`);
        
        if (!option) {
            console.error('Quiz option not found');
            return;
        }
        
        // Clear previous selections
        option.parentElement.querySelectorAll('.quiz-option').forEach(el => {
            el.classList.remove('selected', 'correct', 'incorrect');
        });
        option.classList.add('selected');
        
        // Submit answer to server
        try {
            const response = await fetch('/api/submit-quiz/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    quiz: quizId,
                    selected_answer: answer
                })
            });
            
            const result = await response.json();
            const resultEl = document.getElementById(`quiz-result-${quizId}`);
            
            // Show result
            if (result.is_correct) {
                option.classList.add('correct');
                option.classList.add('selected'); // Keep selected state
                resultEl.innerHTML = `<div class="alert alert-success">Correct! ${result.explanation}</div>`;
            } else {
                option.classList.add('incorrect');
                option.classList.add('selected'); // Keep selected state
                const correctOption = option.parentElement.children[result.correct_answer];
                if (correctOption) {
                    correctOption.classList.add('correct');
                }
                resultEl.innerHTML = `<div class="alert alert-danger">Incorrect. ${result.explanation}</div>`;
            }
            
            // Store result locally for progress tracking
            const quizResults = JSON.parse(localStorage.getItem('quizResults') || '{}');
            quizResults[quizId] = { selected_answer: answer, is_correct: result.is_correct };
            localStorage.setItem('quizResults', JSON.stringify(quizResults));
            
            // Disable further selection
            option.parentElement.querySelectorAll('.quiz-option').forEach(el => {
                el.style.pointerEvents = 'none';
            });
        } catch (error) {
            console.error('Error submitting quiz:', error);
        }
    }
    
    async runExercise() {
        const code = document.getElementById('exercise-code').value;
        const resultsEl = document.getElementById('test-results');
        
        resultsEl.innerHTML = '<div class="alert alert-info">Running tests...</div>';
        
        try {
            const response = await fetch('/api/submit-exercise/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    lesson_id: this.currentLesson.id,
                    code: code
                })
            });
            
            const result = await response.json();
            
            if (result.all_passed) {
                resultsEl.innerHTML = '<div class="alert alert-success">All tests passed! Great job!</div>';
                // Mark exercise as completed in local progress
                this.updateLocalProgress('exercise_completed', true);
            } else {
                let html = '<div class="alert alert-danger">Some tests failed:</div>';
                result.results.forEach(test => {
                    html += `<div class="test-result ${test.passed ? 'passed' : 'failed'}">
                        ${test.test || 'Test'}: ${test.passed ? 'Passed' : 'Failed'}
                        ${test.error ? `<br>Error: ${test.error}` : ''}
                        ${!test.passed && test.expected ? `<br>Expected: ${test.expected}<br>Got: ${test.actual}` : ''}
                    </div>`;
                });
                resultsEl.innerHTML = html;
            }
        } catch (error) {
            resultsEl.innerHTML = '<div class="alert alert-danger">Error running tests: ' + error.message + '</div>';
        }
    }
    
    getSavedExerciseCode(lessonId) {
        const exerciseCodes = JSON.parse(localStorage.getItem('exerciseCodes') || '{}');
        return exerciseCodes[lessonId];
    }
    
    saveExerciseCode(lessonId, code) {
        const exerciseCodes = JSON.parse(localStorage.getItem('exerciseCodes') || '{}');
        exerciseCodes[lessonId] = code;
        localStorage.setItem('exerciseCodes', JSON.stringify(exerciseCodes));
    }
    
    setupExerciseAutoSave(lessonId) {
        const codeTextarea = document.getElementById('exercise-code');
        if (codeTextarea) {
            // Remove any existing listeners to avoid duplicates
            codeTextarea.removeEventListener('input', codeTextarea._autoSaveHandler);
            
            // Create new auto-save handler
            codeTextarea._autoSaveHandler = () => {
                this.saveExerciseCode(lessonId, codeTextarea.value);
            };
            
            // Add auto-save on input (with debouncing)
            let saveTimeout;
            codeTextarea.addEventListener('input', () => {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    this.saveExerciseCode(lessonId, codeTextarea.value);
                }, 1000); // Save after 1 second of no typing
            });
        }
    }
    
    showSolution() {
        console.log('showSolution called');
        console.log('Current lesson:', this.currentLesson);
        
        if (!this.currentLesson) {
            console.error('No current lesson available');
            return;
        }
        
        if (this.currentLesson.exercise_solution) {
            console.log('Setting solution:', this.currentLesson.exercise_solution);
            const codeTextarea = document.getElementById('exercise-code');
            if (codeTextarea) {
                codeTextarea.value = this.currentLesson.exercise_solution;
                // Show a confirmation message
                const resultsEl = document.getElementById('test-results');
                if (resultsEl) {
                    resultsEl.innerHTML = '<div class="alert alert-info"><i class="fas fa-lightbulb"></i> Solution loaded! You can now see the complete implementation.</div>';
                }
            } else {
                console.error('Exercise code textarea not found');
            }
        } else {
            console.log('No exercise solution available for this lesson');
            const resultsEl = document.getElementById('test-results');
            if (resultsEl) {
                resultsEl.innerHTML = '<div class="alert alert-warning"><i class="fas fa-exclamation-triangle"></i> No solution available for this exercise.</div>';
            }
        }
    }
    
    showHome() {
        // Hide all content sections
        document.getElementById('lesson-content').style.display = 'none';
        document.getElementById('progress-dashboard').style.display = 'none';
        document.getElementById('settings-panel').style.display = 'none';
        
        // Show welcome screen
        document.getElementById('welcome-screen').style.display = 'block';
        
        // Clear current module/lesson
        this.currentModule = null;
        this.currentLesson = null;
        
        // Stop time tracking
        this.stopTimeTracking();
    }
    
    showModuleOverview(moduleOrId) {
        // Handle both module objects and module IDs
        let module;
        if (typeof moduleOrId === 'number') {
            module = this.modules?.find(m => m.id === moduleOrId);
            if (!module) {
                console.error('Module not found:', moduleOrId);
                return;
            }
        } else {
            module = moduleOrId;
        }
        
        if (!module) {
            console.error('Invalid module provided');
            return;
        }
        // Hide all content sections
        document.getElementById('lesson-content').style.display = 'none';
        document.getElementById('progress-dashboard').style.display = 'none';
        document.getElementById('settings-panel').style.display = 'none';
        document.getElementById('welcome-screen').style.display = 'none';
        
        // Determine if module has been started
        const moduleProgress = this.calculateModuleProgress(module);
        const hasStarted = moduleProgress > 0;
        const nextLesson = this.getNextIncompleteLesson(module);
        
        // Create module overview content
        const overviewHtml = `
            <div class="module-overview">
                <h1>${module.title}</h1>
                <p class="lead">${module.description}</p>
                <div class="mb-4">
                    <span class="badge bg-primary">Estimated time: ${module.estimated_minutes} minutes</span>
                    <span class="badge bg-success">${module.lessons.length} lessons</span>
                    ${hasStarted ? `<span class="badge bg-info">${moduleProgress}% Complete</span>` : ''}
                </div>
                ${module.dotnet_comparison ? `
                    <div class="alert alert-info">
                        <h5>.NET Comparison</h5>
                        <pre>${module.dotnet_comparison}</pre>
                    </div>
                ` : ''}
                <h3>Lessons in this module:</h3>
                <div class="list-group">
                    ${module.lessons.map((lesson, index) => `
                        <a href="#" class="list-group-item list-group-item-action" 
                           onclick="window.tutorialApp.loadLessonById(${lesson.id}); return false;">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h5 class="mb-1">${index + 1}. ${lesson.title}</h5>
                                    ${lesson.has_exercise ? '<span class="badge bg-warning">Has Exercise</span>' : ''}
                                </div>
                                ${this.isLessonCompleted(lesson.id) ? '<span class="badge bg-success">Completed</span>' : ''}
                            </div>
                        </a>
                    `).join('')}
                </div>
                <div class="mt-4">
                    <button class="btn btn-primary" onclick="window.tutorialApp.${hasStarted ? 'continueModule' : 'startModule'}(${module.id}); return false;">
                        <i class="fas fa-${hasStarted ? 'play-circle' : 'play'}"></i> ${hasStarted ? 'Continue Module' : 'Start Module'}
                    </button>
                </div>
                
                <!-- Module Navigation -->
                <div class="module-navigation mt-4 d-flex justify-content-between">
                    <button class="btn btn-outline-secondary" onclick="window.tutorialApp.showHome(); return false;">
                        <i class="fas fa-arrow-left"></i> Back to Home
                    </button>
                    <button class="btn btn-primary" onclick="window.tutorialApp.${hasStarted ? 'continueModule' : 'startModule'}(${module.id}); return false;">
                        ${hasStarted ? `Continue from Lesson ${nextLesson ? nextLesson.order : '1'}` : 'Start First Lesson'} <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        `;
        
        // Show in lesson content area
        document.getElementById('lesson-content').style.display = 'block';
        document.getElementById('lesson-body').innerHTML = overviewHtml;
        
        // Update breadcrumb
        document.getElementById('module-breadcrumb').textContent = module.title;
        document.getElementById('lesson-breadcrumb').textContent = 'Overview';
        document.getElementById('lesson-title').textContent = 'Module Overview';
        
        // Hide elements not needed for overview (safely)
        const elementsToHide = ['code-comparison', 'exercise-section', 'quiz-section', 'lesson-navigation'];
        elementsToHide.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.style.display = 'none';
            }
        });
        
        // Clear current lesson but keep module
        this.currentModule = module;
        this.currentLesson = null;
        
        // Update URL
        this.updateURL('module', { moduleSlug: module.slug });
        
        // Stop time tracking
        this.stopTimeTracking();
    }
    
    async completeLesson() {
        if (!this.currentLesson) return;
        
        try {
            const response = await fetch(`/api/lessons/${this.currentLesson.id}/complete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });
            
            if (response.ok) {
                // Update local progress
                this.updateLocalProgress('completed', true);
                
                // Update UI
                document.querySelector('.lesson-item.active').classList.add('completed');
                document.getElementById('complete-lesson').style.display = 'none';
                
                // Update module progress bar
                this.updateModuleProgress();
                
                // Reload modules to update progress
                await this.loadModules();
                
                // Show success message
                this.showNotification('Lesson completed!', 'success');
            }
        } catch (error) {
            console.error('Error completing lesson:', error);
        }
    }
    
    updateLocalProgress(field, value) {
        if (!this.progress[this.currentLesson.id]) {
            this.progress[this.currentLesson.id] = {};
        }
        this.progress[this.currentLesson.id][field] = value;
        this.saveProgress();
    }
    
    updateLessonProgress() {
        const progress = this.progress[this.currentLesson.id] || {};
        
        // Check if lesson is completed in current session or previously completed
        const sessionCompleted = progress.completed;
        const previouslyCompleted = this.currentLesson.is_completed;
        
        // Show complete button based on current session status
        if (sessionCompleted || previouslyCompleted) {
            document.getElementById('complete-lesson').style.display = 'none';
        } else {
            document.getElementById('complete-lesson').style.display = 'inline-block';
        }
        
        // Update progress bar to show module completion progress
        this.updateModuleProgress();
    }
    
    updateModuleProgress() {
        if (!this.currentModule) return;
        
        const totalLessons = this.currentModule.lessons.length;
        let completedLessons = 0;
        
        this.currentModule.lessons.forEach(lesson => {
            const progress = this.progress[lesson.id] || {};
            if (progress.completed || lesson.is_completed) {
                completedLessons++;
            }
        });
        
        const progressPercentage = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;
        document.getElementById('lesson-progress').style.width = progressPercentage + '%';
        
        // Also update sidebar progress
        this.updateSidebarProgress();
    }
    
    calculateModuleProgress(module) {
        let totalLessons = module.lessons.length;
        let completedLessons = 0;
        
        module.lessons.forEach(lesson => {
            const progress = this.progress[lesson.id] || {};
            if (progress.completed || lesson.is_completed) {
                completedLessons++;
            }
        });
        
        return totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;
    }
    
    getNextIncompleteLesson(module) {
        return module.lessons.find(lesson => {
            const progress = this.progress[lesson.id] || {};
            return !progress.completed && !lesson.is_completed;
        });
    }
    
    continueModule(moduleId) {
        const module = this.modules.find(m => m.id === moduleId);
        if (!module) return;
        
        const nextLesson = this.getNextIncompleteLesson(module);
        if (nextLesson) {
            this.loadLessonById(nextLesson.id);
        } else {
            // All lessons completed, start from first lesson
            this.startModule(moduleId);
        }
    }
    
    updateSidebarProgress() {
        // Update progress for all modules in the sidebar
        this.modules.forEach(module => {
            const progressElement = document.querySelector(`#module-${module.id}-lessons`)
                ?.parentElement.querySelector('.module-progress');
            if (progressElement) {
                const progress = this.calculateModuleProgress(module);
                progressElement.textContent = `${progress}%`;
            }
        });
    }
    
    updateNavigationButtons() {
        const currentModuleIndex = this.modules.findIndex(m => m.id === this.currentModule.id);
        const currentLessonIndex = this.currentModule.lessons.findIndex(l => l.id === this.currentLesson.id);
        
        const prevButton = document.getElementById('prev-lesson');
        const nextButton = document.getElementById('next-lesson');
        
        // Check if there's a previous lesson
        if (currentLessonIndex > 0 || currentModuleIndex > 0) {
            prevButton.disabled = false;
        } else {
            prevButton.disabled = true;
        }
        
        // Check if there's a next lesson
        if (currentLessonIndex < this.currentModule.lessons.length - 1 || 
            currentModuleIndex < this.modules.length - 1) {
            nextButton.disabled = false;
        } else {
            nextButton.disabled = true;
        }
    }
    
    startModule(moduleId) {
        const module = this.modules?.find(m => m.id === moduleId);
        if (module && module.lessons && module.lessons.length > 0) {
            this.loadLesson(module, module.lessons[0]);
        } else {
            console.error('Module or lessons not found:', moduleId);
        }
    }
    
    loadLessonById(lessonId) {
        // Find the lesson and its module
        let targetModule = null;
        let targetLesson = null;
        
        for (const module of this.modules || []) {
            const lesson = module.lessons?.find(l => l.id === lessonId);
            if (lesson) {
                targetModule = module;
                targetLesson = lesson;
                break;
            }
        }
        
        if (targetModule && targetLesson) {
            this.loadLesson(targetModule, targetLesson);
        } else {
            console.error('Lesson not found:', lessonId);
        }
    }
    
    navigateLesson(direction) {
        // If we're on module overview, start with first lesson
        if (!this.currentLesson) {
            if (this.currentModule && this.currentModule.lessons.length > 0) {
                this.loadLesson(this.currentModule, this.currentModule.lessons[0]);
            }
            return;
        }
        
        const currentModuleIndex = this.modules.findIndex(m => m.id === this.currentModule.id);
        const currentLessonIndex = this.currentModule.lessons.findIndex(l => l.id === this.currentLesson.id);
        
        if (direction === 'next') {
            if (currentLessonIndex < this.currentModule.lessons.length - 1) {
                // Next lesson in same module
                this.loadLesson(this.currentModule, this.currentModule.lessons[currentLessonIndex + 1]);
            } else if (currentModuleIndex < this.modules.length - 1) {
                // First lesson of next module
                const nextModule = this.modules[currentModuleIndex + 1];
                this.toggleModule(nextModule.id);
                this.loadLesson(nextModule, nextModule.lessons[0]);
            }
        } else if (direction === 'prev') {
            if (currentLessonIndex > 0) {
                // Previous lesson in same module
                this.loadLesson(this.currentModule, this.currentModule.lessons[currentLessonIndex - 1]);
            } else if (currentModuleIndex > 0) {
                // Last lesson of previous module
                const prevModule = this.modules[currentModuleIndex - 1];
                this.toggleModule(prevModule.id);
                this.loadLesson(prevModule, prevModule.lessons[prevModule.lessons.length - 1]);
            }
        }
    }
    
    startTimeTracking() {
        this.startTime = Date.now();
        this.timeTracker = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            if (elapsed > 0 && elapsed % 30 === 0) {
                // Save time every 30 seconds
                this.saveTimeSpent(elapsed);
            }
        }, 1000);
    }
    
    stopTimeTracking() {
        if (this.timeTracker) {
            clearInterval(this.timeTracker);
            if (this.startTime) {
                const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
                this.saveTimeSpent(elapsed);
            }
            this.timeTracker = null;
            this.startTime = null;
        }
    }
    
    async saveTimeSpent(seconds) {
        if (!this.currentLesson) return;
        
        // Save to local storage
        if (!this.progress[this.currentLesson.id]) {
            this.progress[this.currentLesson.id] = {};
        }
        this.progress[this.currentLesson.id].time_spent_seconds = 
            (this.progress[this.currentLesson.id].time_spent_seconds || 0) + seconds;
        this.saveProgress();
        
        // Try to save to server (gracefully handle auth errors)
        try {
            const response = await fetch(`/api/lessons/${this.currentLesson.id}/track_time/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    time_spent_seconds: seconds
                })
            });
            
            if (!response.ok && response.status === 403) {
                console.log('Time tracking requires authentication, using local storage only');
            }
        } catch (error) {
            console.log('Server time tracking failed, using local storage only:', error.message);
        }
    }
    
    showProgressDashboard() {
        document.getElementById('welcome-screen').style.display = 'none';
        document.getElementById('lesson-content').style.display = 'none';
        document.getElementById('settings-panel').style.display = 'none';
        document.getElementById('progress-dashboard').style.display = 'block';
        
        // Update URL
        this.updateURL('progress');
        
        this.updateProgressDashboard();
    }
    
    async updateProgressDashboard() {
        try {
            const response = await fetch('/api/progress/summary/');
            const data = await response.json();
            
            document.getElementById('overall-percentage').textContent = data.progress_percentage + '%';
            document.getElementById('lessons-completed').textContent = 
                `${data.completed_lessons}/${data.total_lessons}`;
            document.getElementById('time-spent').textContent = 
                this.formatTime(data.total_time_seconds);
            
            // Module progress
            const modulesContainer = document.getElementById('modules-progress');
            modulesContainer.innerHTML = '';
            
            data.modules_progress.forEach(module => {
                const moduleEl = document.createElement('div');
                moduleEl.className = 'progress-module';
                moduleEl.innerHTML = `
                    <h5>${module.title}</h5>
                    <div class="progress">
                        <div class="progress-bar" style="width: ${module.progress_percentage}%">
                            ${module.progress_percentage}%
                        </div>
                    </div>
                `;
                modulesContainer.appendChild(moduleEl);
            });
        } catch (error) {
            // Use local progress
            this.updateProgressFromLocal();
        }
    }
    
    updateProgressFromLocal() {
        let totalLessons = 0;
        let completedLessons = 0;
        let totalTime = 0;
        
        this.modules.forEach(module => {
            module.lessons.forEach(lesson => {
                totalLessons++;
                const progress = this.progress[lesson.id];
                if (progress) {
                    if (progress.completed) completedLessons++;
                    totalTime += progress.time_spent_seconds || 0;
                }
            });
        });
        
        const percentage = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;
        
        document.getElementById('overall-percentage').textContent = percentage + '%';
        document.getElementById('lessons-completed').textContent = `${completedLessons}/${totalLessons}`;
        document.getElementById('time-spent').textContent = this.formatTime(totalTime);
    }
    
    updateOverallProgress() {
        let totalLessons = 0;
        let completedLessons = 0;
        
        this.modules.forEach(module => {
            // Use server-side data if available, otherwise calculate from local progress
            if (module.total_lessons !== undefined && module.completed_lessons !== undefined) {
                totalLessons += module.total_lessons;
                completedLessons += module.completed_lessons;
            } else {
                // Fallback to local calculation
                totalLessons += module.lessons ? module.lessons.length : 0;
                if (module.lessons) {
                    module.lessons.forEach(lesson => {
                        const progress = this.progress[lesson.id];
                        if (progress && progress.completed) {
                            completedLessons++;
                        }
                    });
                }
            }
        });
        
        const percentage = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;
        document.getElementById('overall-progress').textContent = percentage + '%';
    }
    
    isLessonCompleted(lessonId) {
        // Check local progress first
        const localProgress = this.progress[lessonId]?.completed;
        if (localProgress) return true;
        
        // Check server-side progress from lesson data
        for (const module of this.modules) {
            const lesson = module.lessons?.find(l => l.id === lessonId);
            if (lesson && lesson.is_completed) {
                return true;
            }
        }
        
        return false;
    }
    
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else {
            return `${minutes}m`;
        }
    }
    
    showSettings() {
        document.getElementById('welcome-screen').style.display = 'none';
        document.getElementById('lesson-content').style.display = 'none';
        document.getElementById('progress-dashboard').style.display = 'none';
        document.getElementById('settings-panel').style.display = 'block';
        
        // Update URL
        this.updateURL('settings');
    }
    
    showHome() {
        document.getElementById('welcome-screen').style.display = 'block';
        document.getElementById('lesson-content').style.display = 'none';
        document.getElementById('progress-dashboard').style.display = 'none';
        document.getElementById('settings-panel').style.display = 'none';
        document.getElementById('lesson-navigation').style.display = 'none';
        
        // Update URL
        this.updateURL('home');
        
        // Reset current lesson and module
        this.currentLesson = null;
        this.currentModule = null;
        
        // Reset breadcrumb to home state
        document.getElementById('module-breadcrumb').textContent = '';
        document.getElementById('lesson-breadcrumb').textContent = '';
        document.getElementById('module-breadcrumb').style.cursor = 'default';
    }
    
    async exportProgress() {
        try {
            const response = await fetch('/api/export-progress/');
            const data = await response.json();
            
            // Merge with local progress
            data.local_progress = this.progress;
            
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `django-tutorial-progress-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting progress:', error);
        }
    }
    
    importProgress() {
        document.getElementById('import-file').click();
    }
    
    async handleImportFile(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        try {
            const text = await file.text();
            const data = JSON.parse(text);
            
            // Import local progress
            if (data.local_progress) {
                this.progress = data.local_progress;
                this.saveProgress();
            }
            
            // Import server progress if authenticated
            if (data.progress) {
                await fetch('/api/import-progress/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    },
                    body: JSON.stringify(data)
                });
            }
            
            // Reload modules
            await this.loadModules();
            this.showNotification('Progress imported successfully!', 'success');
        } catch (error) {
            console.error('Error importing progress:', error);
            this.showNotification('Error importing progress file', 'danger');
        }
    }
    
    resetProgress() {
        if (confirm('Are you sure you want to reset all progress? This cannot be undone.')) {
            this.progress = {};
            this.saveProgress();
            this.loadModules();
            this.showNotification('Progress reset successfully', 'info');
        }
    }
    
    toggleDarkMode() {
        const isDark = document.getElementById('dark-mode').checked;
        if (isDark) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'true');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'false');
        }
    }
    
    applyTheme() {
        const darkMode = localStorage.getItem('darkMode') === 'true';
        if (darkMode) {
            document.body.classList.add('dark-mode');
            document.getElementById('dark-mode').checked = true;
        }
    }
    
    checkAuth() {
        // Check if user is authenticated by looking for Django's sessionid cookie
        const isAuthenticated = document.cookie.includes('sessionid');
        const authSection = document.getElementById('auth-section');
        
        if (isAuthenticated) {
            authSection.innerHTML = `
                <a class="nav-link" href="/api-auth/logout/">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            `;
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-5`;
        notification.style.zIndex = '9999';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // URL Routing Methods
    updateURL(type, params = {}) {
        let hash = '';
        let title = 'Django for .NET Developers';
        
        switch (type) {
            case 'lesson':
                hash = `#/module/${params.moduleSlug}/lesson/${params.lessonSlug}`;
                title = `${this.currentLesson.title} - ${this.currentModule.title}`;
                break;
            case 'module':
                hash = `#/module/${params.moduleSlug}`;
                title = `${this.currentModule.title} - Django for .NET Developers`;
                break;
            case 'settings':
                hash = '#/settings';
                title = 'Settings - Django for .NET Developers';
                break;
            case 'progress':
                hash = '#/progress';
                title = 'Progress - Django for .NET Developers';
                break;
            case 'home':
            default:
                hash = '';
                title = 'Django for .NET Developers';
                break;
        }
        
        window.location.hash = hash;
        document.title = title;
    }
    
    handleInitialRoute() {
        const hash = window.location.hash.substring(1); // Remove the # character
        const pathParts = hash.split('/').filter(part => part);
        
        if (pathParts.length === 0) {
            // Home page
            this.showHome();
        } else if (pathParts[0] === 'settings') {
            this.showSettings();
        } else if (pathParts[0] === 'progress') {
            this.showProgressDashboard();
        } else if (pathParts[0] === 'module') {
            if (pathParts.length === 2) {
                // Module overview: #/module/slug
                this.loadModuleBySlug(pathParts[1]);
            } else if (pathParts.length === 4 && pathParts[2] === 'lesson') {
                // Lesson: #/module/module-slug/lesson/lesson-slug
                this.loadLessonBySlug(pathParts[1], pathParts[3]);
            }
        }
    }
    
    handleRouteChange() {
        // Handle browser back/forward navigation
        this.handleInitialRoute();
    }
    
    loadModuleBySlug(moduleSlug) {
        const module = this.modules.find(m => m.slug === moduleSlug);
        if (module) {
            this.showModuleOverview(module);
        } else {
            console.error('Module not found:', moduleSlug);
            this.showHome();
        }
    }
    
    loadLessonBySlug(moduleSlug, lessonSlug) {
        const module = this.modules.find(m => m.slug === moduleSlug);
        if (module) {
            const lesson = module.lessons.find(l => l.slug === lessonSlug);
            if (lesson) {
                this.toggleModule(module.id); // Expand the module in sidebar
                this.loadLesson(module, lesson);
            } else {
                console.error('Lesson not found:', lessonSlug);
                this.showModuleOverview(module);
            }
        } else {
            console.error('Module not found:', moduleSlug);
            this.showHome();
        }
    }
    
    setupEventListeners() {
        // Navigation
        document.getElementById('start-tutorial').onclick = () => {
            if (this.modules.length > 0 && this.modules[0].lessons.length > 0) {
                this.toggleModule(this.modules[0].id);
                this.loadLesson(this.modules[0], this.modules[0].lessons[0]);
            }
        };
        
        // Breadcrumb navigation
        document.getElementById('home-breadcrumb').onclick = (e) => {
            e.preventDefault();
            this.showHome();
        };
        
        document.getElementById('module-breadcrumb').onclick = (e) => {
            e.preventDefault();
            if (this.currentModule) {
                this.showModuleOverview(this.currentModule);
            }
        };
        
        // Home link in navbar
        const homeLink = document.querySelector('.navbar-brand');
        if (homeLink) {
            homeLink.onclick = (e) => {
                e.preventDefault();
                this.showHome();
            };
        }
        
        document.getElementById('prev-lesson').onclick = () => this.navigateLesson('prev');
        document.getElementById('next-lesson').onclick = () => this.navigateLesson('next');
        document.getElementById('complete-lesson').onclick = () => this.completeLesson();
        
        // Exercise
        document.getElementById('run-exercise').onclick = () => this.runExercise();
        document.getElementById('show-solution').onclick = () => this.showSolution();
        
        // Progress
        document.getElementById('progress-link').onclick = (e) => {
            e.preventDefault();
            this.showProgressDashboard();
        };
        
        // Settings
        document.getElementById('settings-link').onclick = (e) => {
            e.preventDefault();
            this.showSettings();
        };
        
        // Settings back button
        document.getElementById('settings-back-btn').onclick = (e) => {
            e.preventDefault();
            this.showHome();
        };
        
        document.getElementById('export-progress').onclick = () => this.exportProgress();
        document.getElementById('import-progress').onclick = () => this.importProgress();
        document.getElementById('reset-progress').onclick = () => this.resetProgress();
        document.getElementById('import-file').onchange = (e) => this.handleImportFile(e);
        document.getElementById('dark-mode').onchange = () => this.toggleDarkMode();
        
        // Handle browser back/forward navigation
        window.addEventListener('hashchange', (event) => {
            this.handleRouteChange();
        });
        
        // Handle page visibility changes (better than beforeunload)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopTimeTracking();
            } else if (this.currentLesson) {
                // Restart time tracking when page becomes visible again
                this.startTimeTracking();
            }
        });
        
        // Also handle when the window loses focus
        window.addEventListener('blur', () => {
            this.stopTimeTracking();
        });
        
        window.addEventListener('focus', () => {
            if (this.currentLesson) {
                this.startTimeTracking();
            }
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.tutorialApp = new TutorialApp();
});
