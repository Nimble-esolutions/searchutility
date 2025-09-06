# AI-Powered Document Search System
## CC & RCS Maharashtra - Search Utility

[![Django](https://img.shields.io/badge/Django-5.2.6-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Government-red.svg)](LICENSE)

> **Advanced AI-powered document search and management system for the Commissioner for Cooperation and Registrar, Cooperative Societies, Maharashtra State.**

## 🎯 Overview

This Django-based web application provides intelligent document search capabilities using OpenAI's GPT models. It's specifically designed for the Maharashtra government's cooperative societies department to efficiently search, analyze, and manage PDF documents with AI-powered natural language queries.

### 🌟 Key Features

- **🤖 AI-Powered Search**: Natural language queries using OpenAI GPT-4
- **📄 PDF Processing**: Automatic text extraction and OCR capabilities
- **🔍 Advanced Search**: Full-text search with PostgreSQL integration
- **👥 User Management**: Role-based access control with department assignments
- **📁 File Organization**: Hierarchical folder structure for document management
- **🌐 Multi-language**: Support for English and Marathi
- **🔒 Secure**: CSRF protection, HTTPS support, and environment-based configuration
- **📱 Responsive**: Mobile-friendly interface with modern UI

## 🏗️ Architecture

```
searchutility/
├── flowdocs/                    # Main Django project
│   ├── flowdocs/               # Project settings
│   │   ├── settings.py         # Development settings
│   │   ├── settings_production.py  # Production settings
│   │   ├── wsgi.py            # WSGI configuration
│   │   └── urls.py            # Main URL routing
│   ├── core/                   # Core application
│   │   ├── models.py          # Database models
│   │   ├── views.py           # Application views
│   │   ├── utils.py           # AI utilities & PDF processing
│   │   ├── forms.py           # Django forms
│   │   ├── templates/         # HTML templates
│   │   └── static/            # Static assets
│   ├── media/                  # Uploaded files
│   ├── locale/                 # Internationalization
│   └── manage.py              # Django management
├── Dockerfile                  # Container configuration
├── start.sh                   # Container startup script
├── requirements.txt           # Python dependencies
├── .env.template              # Environment variables template
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 12+ (for production)
- Redis (for caching)
- Tesseract OCR
- Poppler utilities
- OpenAI API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Nimble-esolutions/searchutility.git
   cd searchutility
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application.

## 🐳 Docker Deployment

### Build and Run Locally

```bash
# Build the image
docker build -t cc-rcs-search .

# Run with environment file
docker run -d \
  --name cc-rcs-search \
  --env-file .env \
  -p 8000:8000 \
  -v $(pwd)/media:/app/flowdocs/media \
  cc-rcs-search
```

### Docker Compose (Development)

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./media:/app/flowdocs/media
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: flowdocs
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your-password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 🚀 Dokploy Deployment Guide

### Step 1: Repository Setup

1. **Fork/Clone Repository**
   - Ensure your repository is accessible to Dokploy
   - Repository: `https://github.com/Nimble-esolutions/searchutility.git`
   - Branch: `development` (for production deployment)

### Step 2: Dokploy Configuration

#### General Settings
- **Project Name**: `Search Utility`
- **Application Name**: `prod-frontend-aywco9`
- **Build Type**: `Dockerfile` ✅
- **Repository**: `Nimble-esolutions/searchutility`
- **Branch**: `development`

#### Environment Variables
Configure the following in Dokploy's Environment tab:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,dev.ai-sahakar.net,www.ai-sahakar.net,ai-sahakar.net

# Database Configuration (PostgreSQL recommended for production)
DB_NAME=flowdocs
DB_USER=postgres
DB_PASSWORD=your-secure-db-password
DB_HOST=localhost
DB_PORT=5432

# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Google API (if needed)
GOOGLE_API_KEY=your-google-api-key-here

# Redis Configuration
REDIS_URL=redis://localhost:6379/1

# CORS and CSRF Configuration
CORS_ALLOWED_ORIGINS=https://dev.ai-sahakar.net,https://www.ai-sahakar.net,https://ai-sahakar.net
CSRF_TRUSTED_ORIGINS=https://dev.ai-sahakar.net,https://www.ai-sahakar.net,https://ai-sahakar.net,http://localhost:8000

# Sentry (Optional - for error tracking)
SENTRY_DSN=your-sentry-dsn-here
```

#### Domain Configuration
- **Host**: `dev.ai-sahakar.net`
- **Path**: `/`
- **Internal Path**: `/`
- **Container Port**: `8000`
- **HTTPS**: Enabled with Let's Encrypt
- **Certificate Provider**: Let's Encrypt

#### Build Configuration
- **Docker File**: `./Dockerfile`
- **Docker Context Path**: `.`
- **Docker Build Stage**: `production` (optional)

### Step 3: Database Setup

#### Option A: Dokploy PostgreSQL Service
1. Create a PostgreSQL service in Dokploy
2. Configure connection details in environment variables
3. Database will be automatically created

#### Option B: External Database
1. Set up PostgreSQL instance
2. Create database: `flowdocs`
3. Update environment variables with connection details

### Step 4: Volume Mounts (Important)

Configure volume mounts for persistent data:

```yaml
# In Dokploy Volume Backups section
/app/flowdocs/media:/data/media    # For uploaded PDF files
/app/staticfiles:/data/static      # For static files (optional)
```

### Step 5: Deployment Process

1. **Initial Deployment**
   ```bash
   # Dokploy will automatically:
   # 1. Clone the repository
   # 2. Build Docker image using Dockerfile
   # 3. Run database migrations
   # 4. Create superuser (if configured)
   # 5. Collect static files
   # 6. Start Gunicorn server
   ```

2. **Post-Deployment Setup**
   - Access the application at `https://dev.ai-sahakar.net`
   - Login with superuser credentials
   - Upload initial PDF documents
   - Configure user roles and departments

### Step 6: Traefik Configuration

Your current Traefik configuration is correctly set up:

```yaml
http:
  routers:
    prod-frontend-aywco9-router-1:
      rule: Host(`dev.ai-sahakar.net`)
      service: prod-frontend-aywco9-service-1
      middlewares:
        - redirect-to-https
      entryPoints:
        - web
    prod-frontend-aywco9-router-websecure-1:
      rule: Host(`dev.ai-sahakar.net`)
      service: prod-frontend-aywco9-service-1
      entryPoints:
        - websecure
      tls:
        certResolver: letsencrypt
  services:
    prod-frontend-aywco9-service-1:
      loadBalancer:
        servers:
          - url: http://prod-frontend-aywco9:8000
        passHostHeader: true
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Django secret key | - | ✅ |
| `DEBUG` | Debug mode | `False` | ✅ |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost` | ✅ |
| `DB_NAME` | Database name | `flowdocs` | ✅ |
| `DB_USER` | Database user | `postgres` | ✅ |
| `DB_PASSWORD` | Database password | - | ✅ |
| `DB_HOST` | Database host | `localhost` | ✅ |
| `DB_PORT` | Database port | `5432` | ✅ |
| `OPENAI_API_KEY` | OpenAI API key | - | ✅ |
| `REDIS_URL` | Redis connection URL | - | ❌ |
| `SENTRY_DSN` | Sentry error tracking | - | ❌ |
| `CORS_ALLOWED_ORIGINS` | CORS allowed origins | - | ✅ |
| `CSRF_TRUSTED_ORIGINS` | CSRF trusted origins | - | ✅ |

### Settings Files

- **`flowdocs/flowdocs/settings.py`**: Development settings
- **`flowdocs/flowdocs/settings_production.py`**: Production settings with PostgreSQL, Redis, and security configurations

The application automatically selects the appropriate settings based on the `DEBUG` environment variable.

## 📊 Database Models

### Core Models

- **`CustomUser`**: Extended user model with department and role fields
- **`Folder`**: Hierarchical folder structure for document organization
- **`PDFFile`**: PDF document metadata with search vectors and content
- **`SearchHistory`**: User search query tracking

### Key Features

- **Full-text search** with PostgreSQL's built-in search capabilities
- **File upload validation** with size and type restrictions
- **User role management** with department-based access control
- **Search vector indexing** for fast text search

## 🤖 AI Integration

### OpenAI GPT-4 Integration

The application uses OpenAI's GPT-4 model for:
- **Natural language queries**: Convert user questions to search results
- **Document summarization**: Generate summaries of PDF content
- **Context-aware responses**: Provide relevant answers based on document content

### PDF Processing Pipeline

1. **Upload**: User uploads PDF file
2. **Text Extraction**: Extract text using `pdf2image` and `pytesseract`
3. **Content Analysis**: Process text for search indexing
4. **AI Processing**: Generate embeddings and summaries
5. **Storage**: Store in database with search vectors

## 🔒 Security Features

- **CSRF Protection**: Cross-site request forgery protection
- **CORS Configuration**: Cross-origin resource sharing controls
- **HTTPS Enforcement**: SSL/TLS encryption in production
- **Environment-based Secrets**: Secure configuration management
- **User Authentication**: Django's built-in authentication system
- **Role-based Access**: Department and role-based permissions

## 🚨 Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   # Ensure you're in the correct directory
   cd flowdocs
   python manage.py runserver
   ```

2. **Database Connection Issues**
   ```bash
   # Check database configuration
   python manage.py dbshell
   ```

3. **OpenAI API Errors**
   ```bash
   # Verify API key is set
   echo $OPENAI_API_KEY
   ```

4. **Static Files Not Loading**
   ```bash
   # Collect static files
   python manage.py collectstatic --noinput
   ```

### Logs and Monitoring

- **Application Logs**: Check Dokploy logs tab
- **Database Logs**: Monitor PostgreSQL logs
- **Error Tracking**: Use Sentry for production error monitoring

## 🔄 Updates and Maintenance

### Deployment Updates

1. **Code Updates**
   ```bash
   git push origin development
   # Dokploy will automatically redeploy
   ```

2. **Database Migrations**
   ```bash
   # Migrations run automatically during deployment
   # Manual migration: python manage.py migrate
   ```

3. **Environment Updates**
   - Update environment variables in Dokploy
   - Restart application if needed

### Landing Pages (SPA)

The project includes a separate Single Page Application for landing pages:

- **Branch**: `feature/landing-pages`
- **Features**: Client-side routing, PWA support, offline functionality
- **Deployment**: Can be deployed independently as static files
- **Documentation**: See `landing-pages/README.md` for SPA deployment guide

### Backup Strategy

- **Database**: Regular PostgreSQL backups
- **Media Files**: Volume backup of `/app/flowdocs/media`
- **Configuration**: Environment variables backup
- **Landing Pages**: Static files with service worker caching

## 📞 Support

### Technical Support
- **Email**: support@ccrs.maharashtra.gov.in
- **Phone**: +91-20-XXXX-XXXX
- **Address**: Pune, Maharashtra, India

### Development Team
- **Repository**: [GitHub - Nimble-esolutions/searchutility](https://github.com/Nimble-esolutions/searchutility)
- **Issues**: Report bugs and feature requests on GitHub

## 📄 License

© 2025 Commissioner for Cooperation and Registrar, Cooperative Societies, Maharashtra State. All rights reserved.

---

**Note**: This application is specifically designed for the Maharashtra government's cooperative societies department. Ensure all API keys and sensitive information are properly configured before deployment.
