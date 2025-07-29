# Django Tutorial for .NET Developers

An interactive, multi-lesson Django tutorial specifically designed for experienced .NET developers transitioning to Python and Django. Features progress tracking, interactive exercises, and side-by-side code comparisons.

## Features

- **Tailored for .NET Developers**: Every concept explained with ASP.NET comparisons
- **Multi-Module Curriculum**: From Django basics to advanced topics like async, DRF, and LLM proxying
- **Interactive Exercises**: Write and test code directly in the browser
- **Progress Tracking**: Automatic progress saving with localStorage
- **Modern UI**: Responsive design with dark mode support
- **Quizzes**: Test your understanding with instant feedback

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd lurn_django

# Start with Docker Compose
docker-compose up

# Populate tutorial content (in another terminal)
docker-compose exec web python manage.py populate_tutorial

# Visit http://localhost:8000
# Login with: admin / admin123
```

### Option 2: Local Python Environment

```bash
# Create virtual environment
python3 -m venv .venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Populate tutorial content
python manage.py populate_tutorial

# Run development server
python manage.py runserver

# Visit http://localhost:8000
```

## Tutorial Modules

### Module 1: Django Fundamentals for .NET Developers
- Project structure comparison (Solution vs Project)
- MVT vs MVC pattern
- URL routing vs ASP.NET routing
- Views vs Controllers

### Module 2: Django REST Framework
- Building REST APIs
- Serializers vs DTOs
- ViewSets vs Web API Controllers
- Authentication & Permissions

### Module 3: Async Django & Background Tasks
- Async views (like async/await in C#)
- Celery for background tasks (like BackgroundService)
- Django Channels (like SignalR)

### Module 4: Building an LLM Proxy Service
- Implementing OpenAI proxy
- Rate limiting and monitoring
- Adding business logic layers
- Async request handling

### Module 5: Docker & AWS EKS Deployment
- Containerizing Django apps
- Docker Compose for development
- Deploying to AWS EKS
- Managing secrets and configuration

## Key Translations for .NET Developers

| ASP.NET Concept | Django Equivalent |
|-----------------|-------------------|
| Solution | Project |
| Project | App |
| Controller | View |
| Action | View function/class |
| Razor View | Template |
| Entity Framework | Django ORM |
| appsettings.json | settings.py |
| Startup.cs | settings.py + wsgi.py |
| IIS/Kestrel | Gunicorn/uWSGI |
| NuGet | pip/PyPI |
| .csproj | requirements.txt |

## Development Tips

### Adding New Content

1. **Via Admin Interface**: 
   - Go to http://localhost:8000/admin
   - Add modules, lessons, quizzes

2. **Via Management Command**:
   - Edit `lessons/management/commands/populate_tutorial.py`
   - Run `python manage.py populate_tutorial`

### Customizing the Tutorial

- **Styles**: Edit `static/css/tutorial.css`
- **Frontend Logic**: Modify `static/js/tutorial.js`
- **API Endpoints**: Update `lessons/views.py`
- **Models**: Extend `lessons/models.py`

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│  Frontend (JS)  │────▶│  Django REST    │
│                 │     │  Framework API  │
└─────────────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   localStorage  │     │  PostgreSQL/    │
│ (Progress Data) │     │    SQLite       │
└─────────────────┘     └─────────────────┘
```

## Production Deployment

1. Update `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Configure proper database (PostgreSQL recommended)
4. Set up proper static file serving (WhiteNoise included)
5. Use environment variables for sensitive data

## Contributing

Feel free to add more modules, improve exercises, or enhance the UI!

## License

MIT License
