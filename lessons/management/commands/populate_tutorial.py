from django.core.management.base import BaseCommand
from lessons.models import Module, Lesson, Quiz
import json
import sys
import os

# Add the content directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../content'))

try:
    from module1_content import get_module1_lessons, get_module1_exercises
    from module2_content import get_module2_lessons, get_module2_exercises
    from module3_content import get_module3_lessons, get_module3_exercises
    from module4_content import get_module4_lessons
    from module5_content import get_module5_lessons
except ImportError as e:
    print(f"Warning: Could not import content modules: {e}")


class Command(BaseCommand):
    help = 'Populate the tutorial with initial content'

    def handle(self, *args, **options):
        self.stdout.write('Populating tutorial content...')
        
        # Module 1: Django Fundamentals for .NET Developers
        module1 = Module.objects.create(
            title="Django Fundamentals for .NET Developers",
            slug="django-fundamentals",
            description="Learn Django basics with direct comparisons to ASP.NET concepts you already know",
            order=1,
            estimated_minutes=45,
            dotnet_comparison="""
            - Django Project = ASP.NET Solution
            - Django App = ASP.NET Project/Assembly
            - urls.py = RouteConfig/Controllers
            - views.py = Controllers/Actions
            - models.py = Entity Models
            - settings.py = appsettings.json + Startup.cs
            """
        )
        
        # Lesson 1.1: Project Structure
        lesson1_1 = Lesson.objects.create(
            module=module1,
            title="Django Project Structure vs ASP.NET",
            slug="project-structure",
            order=1,
            content="""
# Django Project Structure vs ASP.NET

Welcome! Let's start by comparing Django's project structure with what you know from ASP.NET.

## Key Differences

### Project Organization
- **ASP.NET**: Solution (.sln) contains multiple projects (.csproj)
- **Django**: Project contains multiple apps (Python packages)

### Configuration
- **ASP.NET**: `appsettings.json`, `Startup.cs`, dependency injection
- **Django**: `settings.py`, explicit configuration, apps registration

### Entry Points
- **ASP.NET**: `Program.cs` → `Startup.cs` → Controllers
- **Django**: `manage.py` → `settings.py` → `urls.py` → views

## Django Project Structure

```
myproject/
├── manage.py              # Like dotnet CLI
├── requirements.txt       # Like .csproj package references
├── myproject/
│   ├── __init__.py       # Makes it a Python package
│   ├── settings.py       # Like appsettings.json + Startup.cs
│   ├── urls.py           # Root URL configuration
│   ├── asgi.py          # For async deployment
│   └── wsgi.py          # For traditional deployment
└── myapp/               # Like a project in your solution
    ├── __init__.py
    ├── models.py        # Entity models
    ├── views.py         # Controllers
    ├── urls.py          # App-specific routes
    ├── admin.py         # Admin interface config
    └── apps.py          # App configuration
```

## Key Concepts Translation

| ASP.NET Concept | Django Equivalent |
|-----------------|-------------------|
| Solution | Project |
| Project | App |
| Controller | View |
| Action | View function/class |
| Razor View | Template |
| Entity Framework | Django ORM |
| DbContext | Models + Manager |
| IIS/Kestrel | Gunicorn/uWSGI |
            """,
            django_code="""# Django project structure example
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'myapp',  # Your app
]

# urls.py
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
]

# myapp/views.py
from django.http import JsonResponse

def hello_world(request):
    return JsonResponse({'message': 'Hello from Django!'})
""",
            dotnet_code="""// ASP.NET Core structure example
// Program.cs
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
var app = builder.Build();
app.MapControllers();
app.Run();

// Controllers/HelloController.cs
[ApiController]
[Route("api/[controller]")]
public class HelloController : ControllerBase
{
    [HttpGet]
    public IActionResult Get()
    {
        return Ok(new { message = "Hello from ASP.NET!" });
    }
}
"""
        )
        
        # Lesson 1.2: MVT vs MVC
        lesson1_2 = Lesson.objects.create(
            module=module1,
            title="MVT Pattern vs MVC",
            slug="mvt-vs-mvc",
            order=2,
            content="""
# Understanding Django's MVT vs ASP.NET's MVC

Django uses MVT (Model-View-Template) instead of MVC, but they're very similar!

## Pattern Comparison

### ASP.NET MVC
- **Model**: Data + Business Logic
- **View**: Razor templates (.cshtml)
- **Controller**: Handles requests, coordinates M&V

### Django MVT
- **Model**: Data + Business Logic (same!)
- **View**: Handles requests (like Controllers!)
- **Template**: HTML templates (like Razor views!)

## The Key Insight

**Django Views = ASP.NET Controllers**
**Django Templates = ASP.NET Views**

This naming difference often confuses .NET developers, but once you understand this mapping, everything clicks!

## Request Flow Comparison

### ASP.NET Flow:
1. Route → Controller Action
2. Action processes request
3. Action returns View with Model
4. Razor renders HTML

### Django Flow:
1. URL pattern → View function
2. View processes request
3. View returns rendered Template with Context
4. Template engine renders HTML

## Example: User List Page

Both examples show how to display a list of users - notice the similarities!
            """,
            django_code="""# models.py
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

# views.py
from django.shortcuts import render
from .models import User

def user_list(request):
    users = User.objects.all()
    return render(request, 'users/list.html', {
        'users': users,
        'title': 'User List'
    })

# urls.py
urlpatterns = [
    path('users/', user_list, name='user_list'),
]

# templates/users/list.html
{% extends 'base.html' %}
{% block content %}
<h1>{{ title }}</h1>
<ul>
{% for user in users %}
    <li>{{ user.name }} - {{ user.email }}</li>
{% endfor %}
</ul>
{% endblock %}
""",
            dotnet_code="""// Models/User.cs
public class User
{
    public int Id { get; set; }
    public string Name { get; set; }
    public string Email { get; set; }
    public DateTime CreatedAt { get; set; }
}

// Controllers/UserController.cs
public class UserController : Controller
{
    private readonly AppDbContext _context;
    
    public UserController(AppDbContext context)
    {
        _context = context;
    }
    
    public IActionResult List()
    {
        var users = _context.Users.ToList();
        ViewBag.Title = "User List";
        return View(users);
    }
}

// Views/User/List.cshtml
@model List<User>
@{
    ViewData["Title"] = ViewBag.Title;
}

<h1>@ViewBag.Title</h1>
<ul>
@foreach (var user in Model)
{
    <li>@user.Name - @user.Email</li>
}
</ul>
""",
            has_exercise=True,
            exercise_starter_code="""# Create a Django view that returns a list of products
# The view should:
# 1. Get all products from the database
# 2. Return them as JSON
# 3. Include product name, price, and stock

from django.http import JsonResponse
from .models import Product

def product_list(request):
    # Your code here
    pass
""",
            exercise_solution="""from django.http import JsonResponse
from .models import Product

def product_list(request):
    products = Product.objects.all()
    product_data = []
    
    for product in products:
        product_data.append({
            'name': product.name,
            'price': float(product.price),
            'stock': product.stock
        })
    
    return JsonResponse({
        'products': product_data,
        'count': len(product_data)
    })
""",
            exercise_tests=json.dumps([
                {
                    "description": "Check if function returns JsonResponse",
                    "code": "print(type(product_list(None)).__name__)",
                    "expected": "JsonResponse"
                }
            ])
        )
        
        # Add a quiz to lesson 1.1
        Quiz.objects.create(
            lesson=lesson1_1,
            question="In Django, what is the equivalent of an ASP.NET Controller?",
            options=["Model", "View", "Template", "URL"],
            correct_answer=1,
            explanation="Django Views handle HTTP requests and return responses, just like ASP.NET Controllers. This is a common source of confusion due to the naming difference.",
            order=1
        )
        
        Quiz.objects.create(
            lesson=lesson1_2,
            question="What file in Django serves a similar purpose to appsettings.json in ASP.NET?",
            options=["urls.py", "views.py", "settings.py", "models.py"],
            correct_answer=2,
            explanation="settings.py in Django contains all configuration settings, similar to how appsettings.json (and Startup.cs) work in ASP.NET Core.",
            order=1
        )
        
        # Module 2: Django REST Framework
        module2 = Module.objects.create(
            title="Django REST Framework",
            slug="django-rest-framework",
            description="Build REST APIs in Django, comparing with ASP.NET Web API",
            order=2,
            estimated_minutes=35,
            dotnet_comparison="""
            - DRF ViewSets = Web API Controllers
            - Serializers = DTOs + Model Validation
            - DRF Routers = Web API Routing
            - Permissions = Authorization Policies
            """
        )
        
        # Lesson 2.1: Building REST APIs
        lesson2_1 = Lesson.objects.create(
            module=module2,
            title="REST APIs: DRF vs Web API",
            slug="rest-apis",
            order=1,
            content="""
# Building REST APIs: Django REST Framework vs ASP.NET Web API

Django REST Framework (DRF) is to Django what Web API is to ASP.NET Core - a powerful toolkit for building REST APIs.

## Core Concepts Mapping

| ASP.NET Web API | Django REST Framework |
|-----------------|----------------------|
| ApiController | ViewSet / APIView |
| DTOs | Serializers |
| Model Validation | Serializer Validation |
| Action Filters | Permissions & Throttling |
| OData | django-filter |

## Key Differences

### Serialization
- **ASP.NET**: Automatic JSON serialization, DTOs for shaping
- **DRF**: Explicit serializers that handle both serialization AND validation

### Routing
- **ASP.NET**: Attribute routing `[Route("api/[controller]")]`
- **DRF**: URL patterns + ViewSet routers

### Validation
- **ASP.NET**: Data Annotations + Model State
- **DRF**: Serializer fields + validators

## Example: Product API

Let's build a complete CRUD API for products to see the comparison.
            """,
            django_code="""# serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'created_at']
        read_only_fields = ['created_at']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value

# views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        low_stock_products = self.queryset.filter(stock__lt=10)
        serializer = self.get_serializer(low_stock_products, many=True)
        return Response(serializer.data)

# urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

# This automatically creates:
# GET /api/products/ - list
# POST /api/products/ - create
# GET /api/products/{id}/ - retrieve
# PUT /api/products/{id}/ - update
# DELETE /api/products/{id}/ - delete
# GET /api/products/low_stock/ - custom action
""",
            dotnet_code="""// DTOs/ProductDto.cs
public class ProductDto
{
    public int Id { get; set; }
    [Required]
    public string Name { get; set; }
    [Range(0.01, double.MaxValue, ErrorMessage = "Price must be positive")]
    public decimal Price { get; set; }
    public int Stock { get; set; }
    public DateTime CreatedAt { get; set; }
}

// Controllers/ProductController.cs
[ApiController]
[Route("api/[controller]")]
public class ProductController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly IMapper _mapper;
    
    public ProductController(AppDbContext context, IMapper mapper)
    {
        _context = context;
        _mapper = mapper;
    }
    
    [HttpGet]
    public async Task<ActionResult<IEnumerable<ProductDto>>> GetProducts()
    {
        var products = await _context.Products.ToListAsync();
        return Ok(_mapper.Map<List<ProductDto>>(products));
    }
    
    [HttpGet("{id}")]
    public async Task<ActionResult<ProductDto>> GetProduct(int id)
    {
        var product = await _context.Products.FindAsync(id);
        if (product == null) return NotFound();
        return Ok(_mapper.Map<ProductDto>(product));
    }
    
    [HttpPost]
    public async Task<ActionResult<ProductDto>> CreateProduct(ProductDto dto)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);
        
        var product = _mapper.Map<Product>(dto);
        _context.Products.Add(product);
        await _context.SaveChangesAsync();
        
        return CreatedAtAction(nameof(GetProduct), 
            new { id = product.Id }, _mapper.Map<ProductDto>(product));
    }
    
    [HttpGet("low-stock")]
    public async Task<ActionResult<IEnumerable<ProductDto>>> GetLowStock()
    {
        var products = await _context.Products
            .Where(p => p.Stock < 10)
            .ToListAsync();
        return Ok(_mapper.Map<List<ProductDto>>(products));
    }
}
"""
        )
        
        # Module 3: Async Django & Background Tasks
        module3 = Module.objects.create(
            title="Async Django & Background Tasks",
            slug="async-background-tasks",
            description="Learn async patterns and background task processing, comparing with .NET's async/await and BackgroundService",
            order=3,
            estimated_minutes=45,
            dotnet_comparison="""
            - Django async views = ASP.NET async actions
            - Celery = BackgroundService + Queue
            - Django Channels = SignalR
            - asyncio = Task/async/await
            """
        )
        
        # Module 4: LLM Proxy Implementation
        module4 = Module.objects.create(
            title="Building an LLM Proxy Service",
            slug="llm-proxy",
            description="Implement a production-ready OpenAI proxy with rate limiting, logging, and business rules",
            order=4,
            estimated_minutes=40,
            dotnet_comparison="""
            - Django Middleware = ASP.NET Middleware
            - Django REST Framework Throttling = ASP.NET Rate Limiting
            - Django Signals = .NET Events
            - Celery Tasks = Hosted Services
            """
        )
        
        # Module 5: Docker & AWS Deployment
        module5 = Module.objects.create(
            title="Docker & AWS EKS Deployment",
            slug="docker-deployment",
            description="Containerize Django apps and deploy to AWS EKS",
            order=5,
            estimated_minutes=35,
            dotnet_comparison="""
            - Gunicorn = Kestrel
            - requirements.txt = .csproj
            - Django static files = wwwroot
            - manage.py commands = dotnet CLI tools
            """
        )
        
        # Add remaining lessons for Module 1
        self.add_module1_lessons(module1)
        
        # Add remaining lessons for Module 2
        self.add_module2_lessons(module2)
        
        # Add lessons for Module 3
        self.add_module3_lessons(module3)
        
        # Add lessons for Module 4
        self.add_module4_lessons(module4)
        
        # Add lessons for Module 5
        self.add_module5_lessons(module5)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated tutorial content!'))
    
    def add_module1_lessons(self, module):
        """Add additional lessons for Module 1: Django Fundamentals"""
        try:
            lessons = get_module1_lessons()
            exercises = get_module1_exercises()
            
            for lesson_data in lessons:
                # Find matching exercise
                exercise = next((ex for ex in exercises if ex['lesson_slug'] == lesson_data['slug']), None)
                
                Lesson.objects.create(
                    module=module,
                    title=lesson_data['title'],
                    slug=lesson_data['slug'],
                    order=lesson_data['order'],
                    content=lesson_data['content'],
                    has_exercise=bool(exercise),
                    exercise_starter_code=exercise['starter_code'] if exercise else '',
                    exercise_solution=exercise['solution'] if exercise else '',
                    exercise_tests=json.dumps(exercise['tests']) if exercise else ''
                )
        except Exception as e:
            print(f"Could not add Module 1 lessons: {e}")
    
    def add_module2_lessons(self, module):
        """Add lessons for Module 2: Django REST Framework"""
        try:
            lessons = get_module2_lessons()
            exercises = get_module2_exercises()
            
            for i, lesson_data in enumerate(lessons[1:], 2):  # Skip first lesson (already exists)
                # Find matching exercise
                exercise = next((ex for ex in exercises if ex['lesson_slug'] == lesson_data['slug']), None)
                
                lesson = Lesson.objects.create(
                    module=module,
                    title=lesson_data['title'],
                    slug=lesson_data['slug'],
                    order=lesson_data['order'],
                    content=lesson_data['content'],
                    has_exercise=bool(exercise),
                    exercise_starter_code=exercise['starter_code'] if exercise else '',
                    exercise_solution=exercise['solution'] if exercise else '',
                    exercise_tests=json.dumps(exercise['tests']) if exercise else ''
                )
        except Exception as e:
            print(f"Could not add Module 2 lessons: {e}")
    
    def add_module3_lessons(self, module):
        """Add lessons for Module 3: Async Django"""
        try:
            lessons = get_module3_lessons()
            exercises = get_module3_exercises()
            
            for lesson_data in lessons:
                # Find matching exercise
                exercise = next((ex for ex in exercises if ex['lesson_slug'] == lesson_data['slug']), None)
                
                Lesson.objects.create(
                    module=module,
                    title=lesson_data['title'],
                    slug=lesson_data['slug'],
                    order=lesson_data['order'],
                    content=lesson_data['content'],
                    has_exercise=bool(exercise),
                    exercise_starter_code=exercise['starter_code'] if exercise else '',
                    exercise_solution=exercise['solution'] if exercise else '',
                    exercise_tests=json.dumps(exercise['tests']) if exercise else ''
                )
        except Exception as e:
            print(f"Could not add Module 3 lessons: {e}")
    
    def add_module4_lessons(self, module):
        """Add lessons for Module 4: LLM Proxy"""
        try:
            lessons = get_module4_lessons()
            for lesson_data in lessons:
                Lesson.objects.create(
                    module=module,
                    title=lesson_data['title'],
                    slug=lesson_data['slug'],
                    order=lesson_data['order'],
                    content=lesson_data['content']
                )
        except Exception as e:
            print(f"Could not add Module 4 lessons: {e}")
    
    def add_module5_lessons(self, module):
        """Add lessons for Module 5: Docker & Deployment"""
        try:
            lessons = get_module5_lessons()
            for lesson_data in lessons:
                Lesson.objects.create(
                    module=module,
                    title=lesson_data['title'],
                    slug=lesson_data['slug'],
                    order=lesson_data['order'],
                    content=lesson_data['content']
                )
        except Exception as e:
            print(f"Could not add Module 5 lessons: {e}")
        self.stdout.write(f'Created {Module.objects.count()} modules and {Lesson.objects.count()} lessons')
