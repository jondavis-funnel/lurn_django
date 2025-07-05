from rest_framework import serializers
from .models import Module, Lesson, UserProgress, CodeSnippet, Quiz, UserQuizAttempt


class CodeSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeSnippet
        fields = ['id', 'title', 'language', 'code', 'description']


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'question', 'options', 'correct_answer', 'explanation', 'order']
        extra_kwargs = {
            'correct_answer': {'write_only': True},
            'explanation': {'write_only': True}
        }


class LessonSerializer(serializers.ModelSerializer):
    snippets = CodeSnippetSerializer(many=True, read_only=True)
    quizzes = QuizSerializer(many=True, read_only=True)
    is_completed = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'content', 'order',
            'django_code', 'dotnet_code', 'has_exercise',
            'exercise_starter_code', 'exercise_solution', 'exercise_tests',
            'snippets', 'quizzes', 'is_completed', 'progress'
        ]
        
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserProgress.objects.filter(
                user=request.user,
                lesson=obj,
                completed=True
            ).exists()
        return False
    
    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            progress = UserProgress.objects.filter(
                user=request.user,
                lesson=obj
            ).first()
            if progress:
                return {
                    'completed': progress.completed,
                    'exercise_completed': progress.exercise_completed,
                    'time_spent_seconds': progress.time_spent_seconds,
                    'last_accessed': progress.last_accessed
                }
        return None


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    total_lessons = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'slug', 'description', 'order',
            'estimated_minutes', 'dotnet_comparison',
            'lessons', 'total_lessons', 'completed_lessons',
            'progress_percentage'
        ]
    
    def get_total_lessons(self, obj):
        return obj.lessons.count()
    
    def get_completed_lessons(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserProgress.objects.filter(
                user=request.user,
                lesson__module=obj,
                completed=True
            ).count()
        return 0
    
    def get_progress_percentage(self, obj):
        total = self.get_total_lessons(obj)
        if total == 0:
            return 0
        completed = self.get_completed_lessons(obj)
        return int((completed / total) * 100)


class UserProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    module_title = serializers.CharField(source='lesson.module.title', read_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'lesson', 'lesson_title', 'module_title',
            'completed', 'completed_at', 'exercise_completed',
            'exercise_attempts', 'exercise_code', 'time_spent_seconds',
            'last_accessed'
        ]


class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuizAttempt
        fields = ['id', 'quiz', 'selected_answer', 'is_correct', 'attempted_at']
        read_only_fields = ['is_correct', 'attempted_at']
    
    def create(self, validated_data):
        quiz = validated_data['quiz']
        selected_answer = validated_data['selected_answer']
        is_correct = selected_answer == quiz.correct_answer
        
        return UserQuizAttempt.objects.create(
            user=self.context['request'].user,
            quiz=quiz,
            selected_answer=selected_answer,
            is_correct=is_correct
        )


class ExerciseSubmissionSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField()
    code = serializers.CharField()
    
    def validate_lesson_id(self, value):
        try:
            lesson = Lesson.objects.get(id=value)
            if not lesson.has_exercise:
                raise serializers.ValidationError("This lesson does not have an exercise.")
            return value
        except Lesson.DoesNotExist:
            raise serializers.ValidationError("Lesson not found.")
