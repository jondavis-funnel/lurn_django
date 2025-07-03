from django.contrib import admin
from .models import Module, Lesson, UserProgress, CodeSnippet, Quiz, UserQuizAttempt


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'order', 'estimated_minutes', 'created_at']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'description']
    ordering = ['order']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'has_exercise', 'created_at']
    list_filter = ['module', 'has_exercise']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'content']
    ordering = ['module__order', 'order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('module', 'title', 'slug', 'order')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Code Examples', {
            'fields': ('django_code', 'dotnet_code'),
            'classes': ('collapse',)
        }),
        ('Exercise', {
            'fields': ('has_exercise', 'exercise_starter_code', 'exercise_solution', 'exercise_tests'),
            'classes': ('collapse',)
        })
    )


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'exercise_completed', 'time_spent_seconds', 'last_accessed']
    list_filter = ['completed', 'exercise_completed', 'last_accessed']
    search_fields = ['user__username', 'lesson__title']
    readonly_fields = ['last_accessed']


@admin.register(CodeSnippet)
class CodeSnippetAdmin(admin.ModelAdmin):
    list_display = ['title', 'language', 'lesson']
    list_filter = ['language']
    search_fields = ['title', 'code', 'description']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'order', 'question']
    list_filter = ['lesson__module']
    list_editable = ['order']
    search_fields = ['question', 'explanation']
    ordering = ['lesson__module__order', 'lesson__order', 'order']


@admin.register(UserQuizAttempt)
class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'selected_answer', 'is_correct', 'attempted_at']
    list_filter = ['is_correct', 'attempted_at']
    search_fields = ['user__username']
    readonly_fields = ['attempted_at']
