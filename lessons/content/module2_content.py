# Module 2: Django REST Framework - Complete Content

def get_module2_lessons():
    """Returns all lessons for Module 2: Django REST Framework"""
    
    lessons = []
    
    # Lesson 2.1: Building REST APIs (already exists, but let's expand it)
    lesson2_1_content = """
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
- **ASP.NET**: Automatic JSON serialization, DTOs for shaping data
- **DRF**: Explicit serializers that handle both serialization AND validation

### Routing
- **ASP.NET**: Attribute routing `[Route("api/[controller]")]`
- **DRF**: URL patterns + ViewSet routers (more explicit but flexible)

### Validation
- **ASP.NET**: Data Annotations + Model State
- **DRF**: Serializer fields + custom validators

## Example: Product API

Let's build a complete CRUD API for products to see the comparison.

### The Django Way
DRF provides ViewSets that automatically handle CRUD operations, similar to how Web API controllers work but with less boilerplate.

### Key Benefits of DRF
1. **Browsable API**: Built-in web interface for testing
2. **Automatic serialization**: Less manual JSON handling
3. **Built-in pagination**: Easy to implement
4. **Flexible permissions**: Fine-grained access control
"""

    lesson2_2_content = """
# Serializers: The Heart of DRF

Serializers in DRF are more powerful than DTOs in .NET - they handle both data transformation AND validation.

## Serializer Types

### ModelSerializer (Most Common)
Like Entity Framework's automatic mapping, but with explicit control:

```python
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock']
        read_only_fields = ['id', 'created_at']
```

### Custom Serializers
For complex data transformation:

```python
class ProductSummarySerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    in_stock = serializers.SerializerMethodField()
    
    def get_in_stock(self, obj):
        return obj.stock > 0
```

## Validation in Serializers

### Field-Level Validation
```python
def validate_price(self, value):
    if value <= 0:
        raise serializers.ValidationError("Price must be positive")
    return value
```

### Object-Level Validation
```python
def validate(self, data):
    if data['price'] > 1000 and data['stock'] < 5:
        raise serializers.ValidationError(
            "High-priced items should have more stock"
        )
    return data
```

## Nested Serializers

Unlike simple DTOs, DRF serializers can handle complex nested relationships:

```python
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'category_id']
```

This is more powerful than .NET's automatic model binding because you get explicit control over what's serialized vs what's accepted for updates.
"""

    lesson2_3_content = """
# ViewSets and Routers: DRF's Routing Magic

ViewSets in DRF are like Web API controllers but with automatic CRUD operations and flexible routing.

## ViewSet Types

### ModelViewSet (Full CRUD)
```python
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # This automatically provides:
    # GET /products/ (list)
    # POST /products/ (create)
    # GET /products/{id}/ (retrieve)
    # PUT /products/{id}/ (update)
    # PATCH /products/{id}/ (partial update)
    # DELETE /products/{id}/ (destroy)
```

### ReadOnlyModelViewSet
For read-only APIs:
```python
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # Only provides list and retrieve
```

## Custom Actions

Add custom endpoints to your ViewSet:

```python
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        # GET /products/low_stock/
        low_stock = self.queryset.filter(stock__lt=10)
        serializer = self.get_serializer(low_stock, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restock(self, request, pk=None):
        # POST /products/{id}/restock/
        product = self.get_object()
        quantity = request.data.get('quantity', 0)
        product.stock += quantity
        product.save()
        return Response({'status': 'restocked', 'new_stock': product.stock})
```

## Automatic Routing

DRF routers automatically create URL patterns:

```python
# urls.py
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
urlpatterns = router.urls

# This creates all the CRUD URLs automatically!
```

## Comparison with ASP.NET Web API

| Feature | ASP.NET Web API | Django REST Framework |
|---------|----------------|----------------------|
| CRUD Operations | Manual controller actions | Automatic via ViewSet |
| Routing | Attribute routing | Router + URL patterns |
| Validation | Data Annotations | Serializer validation |
| Filtering | Manual or OData | django-filter integration |
| Pagination | Manual implementation | Built-in pagination classes |
"""

    lessons.append({
        'title': "REST APIs: DRF vs Web API",
        'slug': "rest-apis",
        'order': 1,
        'content': lesson2_1_content
    })
    
    lessons.append({
        'title': "Serializers: Data Transformation & Validation",
        'slug': "serializers",
        'order': 2,
        'content': lesson2_2_content
    })
    
    lessons.append({
        'title': "ViewSets and Routers",
        'slug': "viewsets-routers",
        'order': 3,
        'content': lesson2_3_content
    })
    
    return lessons

def get_module2_exercises():
    """Returns exercises for Module 2"""
    
    exercises = [
        {
            'lesson_slug': 'serializers',
            'starter_code': '''# Create a serializer for a Book model
# Requirements:
# - Include title, author, price, publication_date
# - Validate that price is positive
# - Make publication_date read-only
# - Add a custom field 'is_recent' (published in last 2 years)

from rest_framework import serializers
from datetime import date, timedelta
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    # Your code here
    pass
''',
            'solution': '''from rest_framework import serializers
from datetime import date, timedelta
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    is_recent = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'publication_date', 'is_recent']
        read_only_fields = ['publication_date']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value
    
    def get_is_recent(self, obj):
        two_years_ago = date.today() - timedelta(days=730)
        return obj.publication_date >= two_years_ago
''',
            'tests': [
                {
                    "description": "Check if serializer has is_recent field",
                    "code": "serializer = BookSerializer(); print('is_recent' in serializer.fields)",
                    "expected": "True"
                }
            ]
        }
    ]
    
    return exercises
