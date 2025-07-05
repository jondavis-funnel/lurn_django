# Module 5: Docker & AWS EKS Deployment - Complete Content

def get_module5_lessons():
    """Returns all lessons for Module 5: Docker & AWS EKS Deployment"""
    
    lessons = []
    
    lesson5_1_content = """
# Containerizing Django Applications

Learn to containerize Django apps for deployment, comparing with .NET containerization patterns.

## Dockerfile for Django

```dockerfile
# Multi-stage build (similar to .NET)
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run as non-root user
RUN useradd -m django
USER django

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
```

## Docker Compose for Development

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    
  celery:
    build: .
    command: celery -A myproject worker --loglevel=info
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb

volumes:
  postgres_data:
```

## Production Configuration

```python
# settings/production.py
import os

DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files (AWS S3)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'
```
"""

    lesson5_2_content = """
# AWS EKS Deployment

Deploy Django to AWS EKS (Elastic Kubernetes Service) for production scalability.

## Kubernetes Manifests

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: django-app
  template:
    metadata:
      labels:
        app: django-app
    spec:
      containers:
      - name: django
        image: your-registry/django-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: django-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: django-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: django-service
spec:
  selector:
    app: django-app
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Ingress (with SSL)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: django-ingress
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:region:account:certificate/cert-id
spec:
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: django-service
            port:
              number: 80
```

## Deployment Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to EKS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    
    - name: Build and push Docker image
      run: |
        aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $ECR_REGISTRY
        docker build -t $ECR_REGISTRY/django-app:$GITHUB_SHA .
        docker push $ECR_REGISTRY/django-app:$GITHUB_SHA
    
    - name: Deploy to EKS
      run: |
        aws eks update-kubeconfig --region us-west-2 --name my-cluster
        kubectl set image deployment/django-app django=$ECR_REGISTRY/django-app:$GITHUB_SHA
        kubectl rollout status deployment/django-app
```

This provides a complete production deployment pipeline similar to Azure DevOps or GitHub Actions for .NET applications.
"""

    lessons.append({
        'title': "Containerizing Django Applications",
        'slug': "docker-django",
        'order': 1,
        'content': lesson5_1_content
    })
    
    lessons.append({
        'title': "AWS EKS Deployment",
        'slug': "eks-deployment",
        'order': 2,
        'content': lesson5_2_content
    })
    
    return lessons
