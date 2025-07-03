from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'modules', views.ModuleViewSet)
router.register(r'lessons', views.LessonViewSet)
router.register(r'progress', views.UserProgressViewSet, basename='progress')

app_name = 'lessons'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('api/', include(router.urls)),
    path('api/submit-exercise/', views.submit_exercise, name='submit-exercise'),
    path('api/submit-quiz/', views.submit_quiz, name='submit-quiz'),
    path('api/export-progress/', views.get_progress_export, name='export-progress'),
    path('api/import-progress/', views.import_progress, name='import-progress'),
]
