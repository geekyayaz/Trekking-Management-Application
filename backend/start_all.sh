#!/bin/bash

# Start Redis
redis-server --daemonize yes

# Start MailHog
./MailHog_linux_amd64 > mailhog.log 2>&1 &

# Start Celery
celery -A app.celery worker --beat --loglevel=info > celery.log 2>&1 &


sleep 2

# Start Flask
python app.py