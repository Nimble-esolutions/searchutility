# Use Python 3.11 slim image for better performance
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-mar \
        poppler-utils \
        libpq-dev \
        gcc \
        g++ \
        libjpeg-dev \
        zlib1g-dev \
        libpng-dev \
        libtiff-dev \
        libwebp-dev \
        libopenjp2-7-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        libffi-dev \
        pkg-config \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Copy .env file if it exists
COPY .env* ./

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
#RUN cd flowdocs && STATIC_ROOT=/app/staticfiles python manage.py collectstatic --noinput --clear
# Collect static files
RUN STATIC_ROOT=/app/staticfiles python manage.py collectstatic --noinput --clear

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["./start.sh"]
