
# 1. Base Python image
FROM python:3.12-slim

# 2. Container working directory
WORKDIR /app

# 3. Python configuration
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements first
COPY requirements.txt .

# 6. Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 7. Copy application
COPY . .

# 8. Create resume directory
RUN mkdir -p /app/uploads/resumes

# 9. Expose application port
EXPOSE 8000

# 10. Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

