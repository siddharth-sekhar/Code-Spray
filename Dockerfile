# Dockerfile for Django app with comprehensive compiler support
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update package list and install essential tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Essential build tools
    build-essential \
    # C/C++ compilers
    gcc \
    g++ \
    clang \
    # Java Development Kit
    default-jdk \
    # Additional tools for compilation
    make \
    cmake \
    # Utilities
    wget \
    curl \
    unzip \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="$JAVA_HOME/bin:$PATH"

# Verify installations
RUN gcc --version && \
    g++ --version && \
    javac -version && \
    java -version && \
    python --version

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "OnlineJudgeProject.wsgi:application", "--bind", "0.0.0.0:8000"]
