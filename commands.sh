#!/bin/bash

# Start Django development server
# python manage.py runserver &

# # Wait until Django server is accessible
# while ! nc -z localhost 8000; do
#   sleep 1
# done

# Start Celery worker
celery -A core worker -l INFO -E &

# Start Celery Flower
celery -A core flower &

# Wait for all background processes to finish
# wait
