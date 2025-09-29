FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application files
COPY requirements.txt .
COPY requirements-test.txt .
COPY scripts/ ./scripts/
COPY tests/ ./tests/
COPY sql/ ./sql/
COPY cronjobs .
COPY .ruff.toml .
COPY pytest.ini .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-test.txt

# Set permissions for scripts
RUN chmod +x scripts/*.py

# Create log file and set permissions
RUN touch /var/log/cron.log && chmod 666 /var/log/cron.log

# Install cron jobs (ensure cronjobs file has newline at end!)
RUN /usr/bin/crontab /app/cronjobs

# Use simple CMD for cron in foreground
CMD ["cron", "-f"]