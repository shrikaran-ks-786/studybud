# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Clean apt cache, update package list, and install system dependencies
RUN apt-get clean && \
    apt-get update && \
    apt-get install -y \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables
# ENV PYTHONUNBUFFERED 1

# Run database migrations and start the server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 127.0.0.1:8000"]