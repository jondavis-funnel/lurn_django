from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import json
import subprocess
import tempfile
import os

from .models import Module, Lesson, UserProgress, Quiz, UserQuizAttempt
from .serializers import (
    ModuleSerializer, LessonSerializer, UserProgressSerializer,
    QuizSerializer, QuizAttemptSerializer, ExerciseSubmissionSerializer
)


class HomeView(TemplateView):
    """Main tutorial interface"""
    template_name = 'lessons/home.html'


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for modules"""
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for lessons"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def complete(self, request, pk=None):
        """Mark a lesson as complete"""
        lesson = self.get_object()
        if request.user.is_authenticated:
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson
            )
            progress.mark_complete()
        return Response({'status': 'completed'})
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def track_time(self, request, pk=None):
        """Track time spent on a lesson"""
        lesson = self.get_object()
        time_spent = request.data.get('time_spent_seconds', 0)
        
        if request.user.is_authenticated:
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson
            )
            progress.time_spent_seconds += time_spent
            progress.save()
            return Response({'total_time': progress.time_spent_seconds})
        else:
            return Response({'total_time': time_spent})


class UserProgressViewSet(viewsets.ModelViewSet):
    """API endpoint for user progress"""
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get overall progress summary"""
        progress = self.get_queryset()
        total_lessons = Lesson.objects.count()
        completed_lessons = progress.filter(completed=True).count()
        total_time = sum(p.time_spent_seconds for p in progress)
        
        modules_progress = []
        for module in Module.objects.all():
            module_data = ModuleSerializer(module, context={'request': request}).data
            modules_progress.append({
                'id': module.id,
                'title': module.title,
                'progress_percentage': module_data['progress_percentage']
            })
        
        return Response({
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percentage': int((completed_lessons / total_lessons * 100) if total_lessons > 0 else 0),
            'total_time_seconds': total_time,
            'modules_progress': modules_progress
        })


@api_view(['POST'])
def submit_exercise(request):
    """Submit and test exercise code"""
    serializer = ExerciseSubmissionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    lesson_id = serializer.validated_data['lesson_id']
    code = serializer.validated_data['code']
    
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Run tests on the submitted code
    test_results = run_exercise_tests(code, lesson.exercise_tests)
    
    # Update progress if authenticated
    if request.user.is_authenticated:
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        progress.exercise_attempts += 1
        progress.exercise_code = code
        
        if test_results['all_passed']:
            progress.exercise_completed = True
        
        progress.save()
    
    return Response(test_results)


def run_exercise_tests(code, tests_json):
    """Run tests on submitted code"""
    if not tests_json:
        return {'all_passed': True, 'results': [], 'message': 'No tests defined'}
    
    try:
        tests = json.loads(tests_json)
    except json.JSONDecodeError:
        return {'all_passed': False, 'error': 'Invalid test configuration'}
    
    results = []
    all_passed = True
    
    # Create a temporary file to run the code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.write('\n\n# Test execution\n')
        
        for i, test in enumerate(tests):
            test_code = test.get('code', '')
            expected = test.get('expected', '')
            f.write(f'\n# Test {i+1}\n')
            f.write(test_code)
        
        temp_file = f.name
    
    try:
        # Run the code
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            all_passed = False
            results.append({
                'passed': False,
                'error': result.stderr
            })
        else:
            # Parse output and compare with expected results
            output_lines = result.stdout.strip().split('\n')
            for i, test in enumerate(tests):
                expected = str(test.get('expected', ''))
                actual = output_lines[i] if i < len(output_lines) else ''
                passed = actual == expected
                if not passed:
                    all_passed = False
                results.append({
                    'test': test.get('description', f'Test {i+1}'),
                    'passed': passed,
                    'expected': expected,
                    'actual': actual
                })
    
    except subprocess.TimeoutExpired:
        all_passed = False
        results = [{'passed': False, 'error': 'Code execution timed out'}]
    
    except Exception as e:
        all_passed = False
        results = [{'passed': False, 'error': str(e)}]
    
    finally:
        # Clean up
        os.unlink(temp_file)
    
    return {
        'all_passed': all_passed,
        'results': results
    }


@api_view(['POST'])
def submit_quiz(request):
    """Submit quiz answer"""
    quiz_id = request.data.get('quiz')
    selected_answer = request.data.get('selected_answer')
    
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)
    
    is_correct = selected_answer == quiz.correct_answer
    
    # Save attempt if user is authenticated
    if request.user.is_authenticated:
        UserQuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            selected_answer=selected_answer,
            is_correct=is_correct
        )
    
    response_data = {
        'is_correct': is_correct,
        'correct_answer': quiz.correct_answer,
        'explanation': quiz.explanation
    }
    
    return Response(response_data)


@api_view(['GET'])
def get_progress_export(request):
    """Export user progress data for localStorage"""
    if not request.user.is_authenticated:
        # Return anonymous progress structure
        return Response({
            'user': 'anonymous',
            'progress': {},
            'quiz_attempts': []
        })
    
    progress_data = UserProgressSerializer(
        UserProgress.objects.filter(user=request.user),
        many=True
    ).data
    
    quiz_attempts = UserQuizAttempt.objects.filter(user=request.user).values(
        'quiz_id', 'selected_answer', 'is_correct', 'attempted_at'
    )
    
    return Response({
        'user': request.user.username,
        'progress': {str(p['lesson']): p for p in progress_data},
        'quiz_attempts': list(quiz_attempts)
    })


@api_view(['POST'])
def import_progress(request):
    """Import progress data from localStorage"""
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    data = request.data
    progress_data = data.get('progress', {})
    
    imported_count = 0
    for lesson_id, progress_info in progress_data.items():
        try:
            lesson = Lesson.objects.get(id=int(lesson_id))
            progress, created = UserProgress.objects.update_or_create(
                user=request.user,
                lesson=lesson,
                defaults={
                    'completed': progress_info.get('completed', False),
                    'exercise_completed': progress_info.get('exercise_completed', False),
                    'time_spent_seconds': progress_info.get('time_spent_seconds', 0),
                }
            )
            imported_count += 1
        except (Lesson.DoesNotExist, ValueError):
            continue
    
    return Response({
        'imported': imported_count,
        'message': f'Successfully imported progress for {imported_count} lessons'
    })
