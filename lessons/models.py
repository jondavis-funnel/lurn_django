from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Module(models.Model):
    """Represents a learning module (like 'Django Fundamentals')"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    order = models.IntegerField(default=0)
    estimated_minutes = models.IntegerField(default=30)
    dotnet_comparison = models.TextField(help_text="Key comparisons with .NET concepts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Individual lessons within a module"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    content = models.TextField(help_text="Markdown content for the lesson")
    order = models.IntegerField(default=0)
    
    # Code examples
    django_code = models.TextField(blank=True, help_text="Django/Python code example")
    dotnet_code = models.TextField(blank=True, help_text="Equivalent .NET/C# code for comparison")
    
    # Interactive elements
    has_exercise = models.BooleanField(default=False)
    exercise_starter_code = models.TextField(blank=True)
    exercise_solution = models.TextField(blank=True)
    exercise_tests = models.TextField(blank=True, help_text="JSON array of test cases")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['module', 'order']
        unique_together = ['module', 'slug']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"


class UserProgress(models.Model):
    """Tracks user progress through lessons"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Exercise tracking
    exercise_completed = models.BooleanField(default=False)
    exercise_attempts = models.IntegerField(default=0)
    exercise_code = models.TextField(blank=True, help_text="User's submitted code")
    
    # Time tracking
    time_spent_seconds = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'lesson']
    
    def mark_complete(self):
        self.completed = True
        self.completed_at = timezone.now()
        self.save()


class CodeSnippet(models.Model):
    """Reusable code snippets for lessons"""
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('csharp', 'C#'),
        ('javascript', 'JavaScript'),
        ('yaml', 'YAML'),
        ('dockerfile', 'Dockerfile'),
        ('bash', 'Bash'),
    ]
    
    title = models.CharField(max_length=200)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    code = models.TextField()
    description = models.TextField(blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='snippets', null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.language})"


class Quiz(models.Model):
    """Quiz questions for lessons"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    question = models.TextField()
    options = models.JSONField(help_text="List of answer options")
    correct_answer = models.IntegerField(help_text="Index of correct answer in options")
    explanation = models.TextField(help_text="Explanation of the correct answer")
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = "Quizzes"


class UserQuizAttempt(models.Model):
    """Track quiz attempts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    selected_answer = models.IntegerField()
    is_correct = models.BooleanField()
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-attempted_at']
