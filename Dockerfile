FROM python:3.11-slim

LABEL maintainer="DevOps Team"
LABEL description="Automated Security Update for Drupal"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ssh \
    rsync \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Install Drush globally
RUN composer global require drush/drush:^12 \
    && ln -s /root/.composer/vendor/bin/drush /usr/local/bin/drush

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs reports patches

# Make scripts executable
RUN chmod +x scripts/*.sh

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "from core.config import load_config; load_config()" || exit 1

# Default command
CMD ["bash"]
