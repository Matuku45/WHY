# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port (Fly.io uses 8080 internally)
EXPOSE 8080

# Command to run the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
