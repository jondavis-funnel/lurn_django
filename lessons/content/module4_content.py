# Module 4: LLM Proxy Implementation - Complete Content

def get_module4_lessons():
    """Returns all lessons for Module 4: Building an LLM Proxy Service"""
    
    lessons = []
    
    lesson4_1_content = """
# Building an LLM Proxy Service with Django

Learn to build a production-ready OpenAI proxy with rate limiting, logging, and business rules - essential for LLM-powered applications.

## Architecture Overview

```
Client → Django Proxy → OpenAI API
         ↓
    Rate Limiting
    Authentication  
    Request Logging
    Response Caching
    Business Rules
```

## Key Components

### 1. Proxy View
```python
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class OpenAIProxyView(APIView):
    permission_classes = [IsAuthenticated]
    
    async def post(self, request):
        # Extract and validate request
        user_prompt = request.data.get('prompt')
        model = request.data.get('model', 'gpt-3.5-turbo')
        
        # Apply business rules
        if not self.is_request_allowed(request.user, user_prompt):
            return JsonResponse({'error': 'Request not allowed'}, status=403)
        
        # Make OpenAI call
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": user_prompt}],
                user=str(request.user.id)  # For OpenAI tracking
            )
            
            # Log the interaction
            self.log_interaction(request.user, user_prompt, response)
            
            return JsonResponse(response)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
```

### 2. Rate Limiting
```python
from django.core.cache import cache
from django.http import JsonResponse

class RateLimitMixin:
    def check_rate_limit(self, user):
        key = f"rate_limit_{user.id}"
        current_count = cache.get(key, 0)
        
        if current_count >= 100:  # 100 requests per hour
            return False
            
        cache.set(key, current_count + 1, 3600)  # 1 hour timeout
        return True
```

### 3. Request Logging
```python
from .models import LLMRequest

def log_interaction(self, user, prompt, response):
    LLMRequest.objects.create(
        user=user,
        prompt=prompt[:1000],  # Truncate for storage
        response=response.get('choices', [{}])[0].get('message', {}).get('content', ''),
        model=response.get('model'),
        tokens_used=response.get('usage', {}).get('total_tokens', 0),
        cost=self.calculate_cost(response)
    )
```

This creates a robust proxy layer between your application and OpenAI, similar to how you might implement middleware in .NET Core.
"""

    lesson4_2_content = """
# Advanced Proxy Features

## Content Filtering & Business Rules

```python
import re
from django.conf import settings

class ContentFilter:
    BLOCKED_PATTERNS = [
        r'generate.*code.*hack',
        r'create.*virus',
        r'bypass.*security'
    ]
    
    def is_content_allowed(self, prompt):
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                return False
        return True
    
    def apply_business_rules(self, user, prompt):
        # Check user permissions
        if not user.has_perm('llm.use_advanced_models'):
            return False
            
        # Check content
        if not self.is_content_allowed(prompt):
            return False
            
        return True
```

## Response Caching

```python
import hashlib
from django.core.cache import cache

class ResponseCache:
    def get_cache_key(self, prompt, model):
        content = f"{prompt}:{model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_response(self, prompt, model):
        key = self.get_cache_key(prompt, model)
        return cache.get(key)
    
    def cache_response(self, prompt, model, response, timeout=3600):
        key = self.get_cache_key(prompt, model)
        cache.set(key, response, timeout)
```

## Cost Tracking

```python
class CostCalculator:
    PRICING = {
        'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},  # per 1K tokens
        'gpt-4': {'input': 0.03, 'output': 0.06}
    }
    
    def calculate_cost(self, response):
        model = response.get('model', '')
        usage = response.get('usage', {})
        
        if model not in self.PRICING:
            return 0
            
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)
        
        pricing = self.PRICING[model]
        cost = (input_tokens * pricing['input'] + output_tokens * pricing['output']) / 1000
        
        return round(cost, 6)
```
"""

    lessons.append({
        'title': "Building an LLM Proxy Service",
        'slug': "llm-proxy-basics",
        'order': 1,
        'content': lesson4_1_content
    })
    
    lessons.append({
        'title': "Advanced Proxy Features",
        'slug': "advanced-proxy",
        'order': 2,
        'content': lesson4_2_content
    })
    
    return lessons
