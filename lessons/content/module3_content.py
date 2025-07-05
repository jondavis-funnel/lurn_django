# Module 3: Async Django & Background Tasks - Complete Content

def get_module3_lessons():
    """Returns all lessons for Module 3: Async Django & Background Tasks"""
    
    lessons = []
    
    lesson3_1_content = """
# Async Django: From .NET async/await to Python asyncio

Django 3.1+ supports async views, similar to how ASP.NET Core handles async operations. Let's explore the similarities and differences.

## Key Concepts Mapping

| .NET Concept | Django/Python Equivalent |
|--------------|--------------------------|
| `async Task<IActionResult>` | `async def view(request)` |
| `await SomeMethodAsync()` | `await some_method()` |
| `Task.Run()` | `asyncio.create_task()` |
| `ConfigureAwait(false)` | Not needed in Python |
| `CancellationToken` | `asyncio.timeout()` |

## Async Views in Django

### Basic Async View
```python
import asyncio
from django.http import JsonResponse
from asgiref.sync import sync_to_async

async def async_product_list(request):
    # Simulate async database call
    await asyncio.sleep(0.1)  # Like await Task.Delay(100)
    
    # Convert sync ORM call to async
    products = await sync_to_async(list)(Product.objects.all())
    
    return JsonResponse({
        'products': [{'name': p.name, 'price': str(p.price)} for p in products],
        'count': len(products)
    })
```

### Async with External API Calls
```python
import aiohttp
from django.http import JsonResponse

async def weather_data(request):
    city = request.GET.get('city', 'Seattle')
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://api.weather.com/v1/{city}') as response:
            weather = await response.json()
    
    return JsonResponse(weather)
```

## When to Use Async in Django

### Good Use Cases
1. **External API calls**: Like calling OpenAI, AWS services
2. **I/O-bound operations**: File uploads, email sending
3. **WebSocket connections**: Real-time features
4. **Multiple concurrent operations**: Parallel API calls

### Avoid Async For
1. **Simple database queries**: Django ORM is still mostly sync
2. **CPU-intensive tasks**: Use Celery instead
3. **Simple CRUD operations**: Sync views are simpler

## Database Operations in Async Views

Django's ORM is still primarily synchronous, so you need adapters:

```python
from asgiref.sync import sync_to_async
from django.shortcuts import aget_object_or_404  # New in Django 4.1

async def async_product_detail(request, product_id):
    # Method 1: Use Django's async shortcuts (Django 4.1+)
    product = await aget_object_or_404(Product, id=product_id)
    
    # Method 2: Convert sync to async
    product = await sync_to_async(Product.objects.get)(id=product_id)
    
    # Method 3: Use database-specific async libraries
    # (requires additional setup)
    
    return JsonResponse({
        'name': product.name,
        'price': str(product.price)
    })
```

## Comparison with ASP.NET Core Async

### .NET Way
```csharp
[HttpGet("{id}")]
public async Task<ActionResult<ProductDto>> GetProduct(int id)
{
    var product = await _context.Products.FindAsync(id);
    if (product == null) return NotFound();
    
    // Call external service
    var enrichedData = await _externalService.EnrichProductAsync(product);
    
    return Ok(enrichedData);
}
```

### Django Way
```python
async def product_detail(request, product_id):
    try:
        product = await sync_to_async(Product.objects.get)(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    
    # Call external service
    enriched_data = await external_service.enrich_product(product)
    
    return JsonResponse(enriched_data)
```

Both approaches are similar, but Django requires more explicit async/sync conversion for database operations.
"""

    lesson3_2_content = """
# Background Tasks: Celery vs .NET BackgroundService

For long-running tasks, Django uses Celery (like .NET's BackgroundService or Hangfire).

## Architecture Comparison

### .NET Background Services
```csharp
public class EmailService : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            await ProcessEmailQueue();
            await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken);
        }
    }
}
```

### Django + Celery
```python
# tasks.py
from celery import Celery
from django.core.mail import send_mail

app = Celery('myapp')

@app.task
def send_email_task(subject, message, recipient):
    send_mail(subject, message, 'from@example.com', [recipient])
    return f"Email sent to {recipient}"

@app.task
def process_large_file(file_path):
    # Long-running file processing
    # This runs in background worker
    pass
```

## Setting Up Celery

### 1. Install Dependencies
```bash
pip install celery redis  # or celery[redis]
```

### 2. Celery Configuration
```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

### 3. Celery App Setup
```python
# celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

## Task Types

### Fire-and-Forget Tasks
```python
# Like .NET's Task.Run() for background work
@app.task
def cleanup_old_files():
    # Delete files older than 30 days
    pass

# Trigger from view
def trigger_cleanup(request):
    cleanup_old_files.delay()  # Runs in background
    return JsonResponse({'status': 'cleanup started'})
```

### Scheduled Tasks (Cron Jobs)
```python
# Like .NET's Timer or HostedService
from celery.schedules import crontab

app.conf.beat_schedule = {
    'daily-cleanup': {
        'task': 'myapp.tasks.cleanup_old_files',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'hourly-sync': {
        'task': 'myapp.tasks.sync_external_data',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

### Task Chains and Groups
```python
# Sequential tasks (like .NET's ContinueWith)
from celery import chain, group

# Chain: task1 → task2 → task3
workflow = chain(
    process_file.s(file_path),
    validate_results.s(),
    send_notification.s()
)
workflow.apply_async()

# Group: Run tasks in parallel (like Task.WhenAll)
parallel_tasks = group(
    process_file.s(file1),
    process_file.s(file2),
    process_file.s(file3)
)
result = parallel_tasks.apply_async()
```

## Error Handling and Retries

```python
@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def unreliable_task(self, data):
    try:
        # Potentially failing operation
        result = external_api_call(data)
        return result
    except Exception as exc:
        # Log the error
        logger.error(f"Task failed: {exc}")
        # Celery will automatically retry
        raise
```

## Running Celery Workers

```bash
# Start worker (like running a .NET BackgroundService)
celery -A myproject worker --loglevel=info

# Start scheduler (for periodic tasks)
celery -A myproject beat --loglevel=info

# Monitor tasks
celery -A myproject flower  # Web-based monitoring
```

## Integration with Django Views

```python
from .tasks import process_large_file, send_email_task

def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        
        # Save file
        file_path = save_uploaded_file(uploaded_file)
        
        # Process in background
        task = process_large_file.delay(file_path)
        
        return JsonResponse({
            'status': 'processing',
            'task_id': task.id
        })

def check_task_status(request, task_id):
    task = process_large_file.AsyncResult(task_id)
    
    return JsonResponse({
        'status': task.status,
        'result': task.result if task.ready() else None
    })
```

This is similar to .NET's pattern of starting background work and checking status via API endpoints.
"""

    lesson3_3_content = """
# Django Channels: WebSockets and Real-time Features

Django Channels brings WebSocket support to Django, similar to SignalR in .NET.

## Channels vs SignalR

| SignalR Feature | Django Channels Equivalent |
|----------------|---------------------------|
| Hub | Consumer |
| Connection Groups | Channel Groups |
| Client Methods | WebSocket send |
| Server Events | Channel Layer |
| Authentication | Middleware |

## Setting Up Channels

### 1. Installation
```bash
pip install channels channels-redis
```

### 2. Configuration
```python
# settings.py
INSTALLED_APPS = [
    'channels',
    # ... other apps
]

ASGI_APPLICATION = 'myproject.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

### 3. ASGI Configuration
```python
# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import myapp.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            myapp.routing.websocket_urlpatterns
        )
    ),
})
```

## WebSocket Consumers

### Basic Consumer (like SignalR Hub)
```python
# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))
```

### Routing WebSockets
```python
# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\\w+)/$', consumers.ChatConsumer.as_asgi()),
]
```

## Real-time Notifications

### Notification Consumer
```python
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_authenticated:
            self.user_group = f'user_{self.scope["user"].id}'
            
            await self.channel_layer.group_add(
                self.user_group,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()
    
    async def notification_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
```

### Sending Notifications from Views
```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def create_order(request):
    # Create order logic
    order = Order.objects.create(...)
    
    # Send real-time notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{request.user.id}',
        {
            'type': 'notification_message',
            'message': f'Order #{order.id} created successfully',
            'timestamp': order.created_at.isoformat()
        }
    )
    
    return JsonResponse({'status': 'success'})
```

## Frontend Integration

### JavaScript WebSocket Client
```javascript
// Similar to SignalR client setup
const socket = new WebSocket('ws://localhost:8000/ws/chat/general/');

socket.onopen = function(e) {
    console.log('Connected to WebSocket');
};

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    displayMessage(data.username, data.message);
};

socket.onclose = function(e) {
    console.log('WebSocket connection closed');
};

function sendMessage(message) {
    socket.send(JSON.stringify({
        'message': message,
        'username': currentUser
    }));
}
```

## Comparison with SignalR

### SignalR Hub (.NET)
```csharp
public class ChatHub : Hub
{
    public async Task SendMessage(string user, string message)
    {
        await Clients.All.SendAsync("ReceiveMessage", user, message);
    }
    
    public async Task JoinGroup(string groupName)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, groupName);
    }
}
```

### Django Channels Consumer
```python
class ChatConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data['message'],
                'username': data['username']
            }
        )
```

Both provide similar functionality, but Channels uses a more explicit message-passing approach while SignalR has more automatic client method invocation.
"""

    lessons.append({
        'title': "Async Views and asyncio",
        'slug': "async-views",
        'order': 1,
        'content': lesson3_1_content
    })
    
    lessons.append({
        'title': "Background Tasks with Celery",
        'slug': "celery-tasks",
        'order': 2,
        'content': lesson3_2_content
    })
    
    lessons.append({
        'title': "Real-time Features with Django Channels",
        'slug': "django-channels",
        'order': 3,
        'content': lesson3_3_content
    })
    
    return lessons

def get_module3_exercises():
    """Returns exercises for Module 3"""
    
    exercises = [
        {
            'lesson_slug': 'async-views',
            'starter_code': '''# Create an async view that fetches data from multiple APIs
# Requirements:
# - Make concurrent calls to 3 different APIs
# - Combine the results into a single response
# - Handle errors gracefully

import asyncio
import aiohttp
from django.http import JsonResponse

async def combined_data_view(request):
    # Your code here
    pass
''',
            'solution': '''import asyncio
import aiohttp
from django.http import JsonResponse

async def combined_data_view(request):
    async def fetch_api(session, url, key):
        try:
            async with session.get(url) as response:
                data = await response.json()
                return key, data
        except Exception as e:
            return key, {'error': str(e)}
    
    apis = [
        ('weather', 'https://api.weather.com/current'),
        ('news', 'https://api.news.com/headlines'),
        ('stocks', 'https://api.stocks.com/prices')
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_api(session, url, key) for key, url in apis]
        results = await asyncio.gather(*tasks)
    
    combined_data = dict(results)
    return JsonResponse(combined_data)
''',
            'tests': [
                {
                    "description": "Check if function is async",
                    "code": "import inspect; print(inspect.iscoroutinefunction(combined_data_view))",
                    "expected": "True"
                }
            ]
        }
    ]
    
    return exercises
