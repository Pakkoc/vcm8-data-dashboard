# Multi-stage build for Node.js + Python application

# Stage 1: Build frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
# Override outDir to build to dist folder instead of ../backend/staticfiles
RUN npm run build -- --outDir=dist

# Stage 2: Python runtime
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./backend/staticfiles/

# Collect Django static files
WORKDIR /app/backend
RUN python manage.py collectstatic --noinput

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Start gunicorn
CMD gunicorn dashboard_project.wsgi --bind 0.0.0.0:$PORT
