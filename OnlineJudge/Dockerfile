FROM python:3.11

# Set workdir
WORKDIR /OJ

# Install system dependencies in one layer & clean up
RUN apt-get update && apt-get install -y \
    g++ \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for caching
COPY requirements.txt /OJ/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /OJ

# Environment variables
ENV DJANGO_SETTINGS_MODULE=OnlineJudge.settings
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run server (migrations at runtime)
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

