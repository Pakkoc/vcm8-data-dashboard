#!/bin/bash

echo "========================================="
echo "Starting build process..."
echo "========================================="

# 1. Install Node.js dependencies
echo "1. Installing frontend dependencies..."
cd frontend
npm install

# 2. Build React app
echo "2. Building React app..."
npm run build

# 3. Install Python dependencies
echo "3. Installing backend dependencies..."
cd ../backend
pip install -r requirements.txt

# 4. Collect static files
echo "4. Collecting static files..."
python manage.py collectstatic --noinput

# 5. Run migrations
echo "5. Running database migrations..."
python manage.py migrate --noinput

echo "========================================="
echo "Build completed successfully!"
echo "========================================="
