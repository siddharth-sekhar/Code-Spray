# Dockerfile for Django app
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install compilers and interpreters for code execution
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "OnlineJudgeProject.wsgi:application", "--bind", "0.0.0.0:8000"]
