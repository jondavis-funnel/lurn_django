"""
Module 1: Django Fundamentals for .NET Developers
Comprehensive content covering Django basics with .NET comparisons
"""

def get_module1_lessons():
    """Returns additional lessons for Module 1"""
    
    lessons = []
    
    # Lesson 1.3: Django ORM vs Entity Framework
    lesson1_3_content = """
# Django ORM vs Entity Framework

As a .NET developer, you're familiar with Entity Framework. Django's ORM is similar but has some key differences.

## Core Concepts Comparison

| Entity Framework | Django ORM |
|------------------|------------|
| DbContext | Models + Manager |
| DbSet<T> | QuerySet |
| LINQ | QuerySet API |
| Migrations | Migrations |
| Code First | Models First |
| Data Annotations | Field options |

## Model Definition

### Key Differences:
- **Django**: Models inherit from `models.Model`
- **EF**: POCOs with DbContext configuration
- **Django**: Field types are explicit (CharField, IntegerField)
- **EF**: Uses C# types with attributes

## Relationships

Django relationships work similarly to EF:
- `ForeignKey` = One-to-Many (like navigation properties)
- `ManyToManyField` = Many-to-Many
- `OneToOneField` = One-to-One

## Querying Data

The Django QuerySet API is similar to LINQ but uses method chaining differently.

## Migrations

Both frameworks use migrations, but Django's are more explicit and file-based.
"""

    lesson1_4_content = """
# URL Routing: Django vs ASP.NET

URL routing in Django is explicit and centralized, unlike ASP.NET's attribute routing.

## Routing Philosophy

### ASP.NET Core
- **Attribute Routing**: Routes defined on controllers/actions
- **Convention Routing**: Based on controller/action names
- **Route Templates**: `[Route("api/[controller]")]`

### Django
- **Explicit URL Patterns**: All routes defined in `urls.py` files
- **Regular Expressions**: Powerful pattern matching
- **Hierarchical**: Project-level and app-level URL configs

## URL Pattern Structure

Django uses a hierarchical approach:
1. **Project URLs** (`myproject/urls.py`) - Root configuration
2. **App URLs** (`myapp/urls.py`) - App-specific routes
3. **Include Pattern** - Links project to app URLs

## Route Parameters

Both frameworks support route parameters, but syntax differs:
- **ASP.NET**: `{id:int}` or `{slug}`
- **Django**: `<int:id>` or `<slug:slug>`

## Named Routes

Both support named routes for URL generation:
- **ASP.NET**: `Url.Action()` or `asp-action` tag helper
- **Django**: `{% url 'name' %}` template tag or `reverse()` function

## Best Practices

1. **Keep URLs RESTful** - Similar to ASP.NET Web API conventions
2. **Use meaningful names** - For reverse URL lookup
3. **Group related URLs** - In app-specific URL files
4. **Avoid hardcoding URLs** - Use named patterns instead
"""

    lesson1_5_content = """
# Django Settings vs ASP.NET Configuration

Django's settings system is different from ASP.NET's configuration but serves the same purpose.

## Configuration Approach

### ASP.NET Core
- **appsettings.json** - JSON-based configuration
- **Environment Variables** - Override settings
- **User Secrets** - Development secrets
- **IConfiguration** - Dependency injection

### Django
- **settings.py** - Python module
- **Environment Variables** - Via `os.environ`
- **Local Settings** - settings_local.py (not in git)
- **Import-based** - Direct imports throughout app

## Key Settings Categories

### Database Configuration
- **ASP.NET**: Connection strings in appsettings.json
- **Django**: DATABASES dictionary in settings.py

### Security Settings
- **ASP.NET**: Authentication/Authorization middleware
- **Django**: MIDDLEWARE, SECRET_KEY, security settings

### Static Files
- **ASP.NET**: wwwroot folder, UseStaticFiles()
- **Django**: STATIC_URL, STATICFILES_DIRS, collectstatic

## Environment-Specific Settings

Both frameworks support different configurations per environment:
- **ASP.NET**: appsettings.Development.json, appsettings.Production.json
- **Django**: Different settings files or environment variables

## Best Practices

1. **Never commit secrets** - Use environment variables
2. **Separate by environment** - Different settings files
3. **Use meaningful names** - Clear configuration keys
4. **Document settings** - Comments for complex configurations
"""

    lesson1_6_content = """
# Django Admin vs ASP.NET Scaffolding

Django includes a powerful admin interface out of the box - something ASP.NET developers often build manually.

## What is Django Admin?

Django Admin is an automatic admin interface for your models. It's like having a complete CRUD interface generated automatically.

### ASP.NET Equivalent
The closest ASP.NET equivalent would be:
- **ASP.NET Core Scaffolding** - Generates controllers/views
- **Admin Templates** - Custom admin panels you build
- **Third-party Admin** - Libraries like AdminLTE

## Key Features

### Automatic Interface Generation
- **Models Registration** - Register models in admin.py
- **CRUD Operations** - Create, Read, Update, Delete automatically
- **Relationships** - Foreign keys become dropdowns
- **Permissions** - User/group-based access control

### Customization Options
- **List Display** - Choose which fields to show
- **Filters** - Add sidebar filters
- **Search** - Full-text search capabilities
- **Custom Actions** - Bulk operations
- **Inline Editing** - Edit related objects inline

## When to Use Django Admin

### Perfect For:
- **Content Management** - Non-technical users managing data
- **Development** - Quick data manipulation during development
- **Internal Tools** - Admin interfaces for staff

### Not Ideal For:
- **Public Interfaces** - Customer-facing applications
- **Complex Workflows** - Multi-step processes
- **Custom UI/UX** - Specific design requirements

## Comparison with Custom Admin

| Feature | Django Admin | Custom ASP.NET Admin |
|---------|--------------|---------------------|
| Development Time | Minutes | Hours/Days |
| Customization | Limited | Unlimited |
| Maintenance | Automatic | Manual |
| Learning Curve | Minimal | Significant |
| UI/UX Control | Basic | Complete |
"""

    lessons.append({
        'title': "Django ORM vs Entity Framework",
        'slug': "django-orm",
        'order': 3,
        'content': lesson1_3_content
    })
    
    lessons.append({
        'title': "URL Routing: Django vs ASP.NET",
        'slug': "url-routing",
        'order': 4,
        'content': lesson1_4_content
    })
    
    lessons.append({
        'title': "Django Settings vs ASP.NET Configuration",
        'slug': "django-settings",
        'order': 5,
        'content': lesson1_5_content
    })
    
    lessons.append({
        'title': "Django Admin vs ASP.NET Scaffolding",
        'slug': "django-admin",
        'order': 6,
        'content': lesson1_6_content
    })
    
    return lessons

def get_module1_exercises():
    """Returns exercises for Module 1"""
    
    exercises = [
        {
            'lesson_slug': 'django-orm',
            'starter_code': '''# Create a Django model for a Product
# Requirements:
# - Name (max 100 characters)
# - Price (decimal with 2 decimal places)
# - Category (foreign key to Category model)
# - Created date (auto-set on creation)
# - Is active (boolean, default True)

from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    # Your code here
    pass
''',
            'solution': '''from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
''',
            'tests': [
                {
                    "description": "Check if Product model has required fields",
                    "code": "from django.db import models; print(hasattr(Product, 'name') and hasattr(Product, 'price'))",
                    "expected": "True"
                }
            ]
        },
        {
            'lesson_slug': 'url-routing',
            'starter_code': '''# Create URL patterns for a blog app
# Requirements:
# - Home page: /
# - Post list: /posts/
# - Post detail: /posts/<id>/
# - Post by category: /posts/category/<slug>/
# - About page: /about/

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Your URL patterns here
]
''',
            'solution': '''from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('posts/category/<slug:slug>/', views.posts_by_category, name='posts_by_category'),
    path('about/', views.about, name='about'),
]
''',
            'tests': [
                {
                    "description": "Check if URL patterns are defined",
                    "code": "print(len(urlpatterns) >= 4)",
                    "expected": "True"
                }
            ]
        }
    ]
    
    return exercises
