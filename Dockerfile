# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files into the container
COPY . .

# Expose no ports, as this is a background worker
# ENV variables (API_ID, API_HASH) should be set in Koyeb or passed in manually

# Start the application
CMD ["python", "app.py"]
