# Use Python 3.9 on Alpine Linux (small, fast image)
FROM python:3.9-alpine3.13

# Metadata: who maintains this image
LABEL maintainer="recipe-app"

# Prevent Python from buffering stdout/stderr
# (so logs appear immediately in Docker)
ENV PYTHONUNBUFFERED=1                

# -------------------------------
# Copy project files into image
# -------------------------------

# Main Python dependencies
COPY ./requirements.txt /tmp/requirements.txt

# Development-only dependencies (linting, testing, etc.)
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Copy Django app source code
COPY ./app /app

# -------------------------------
# Container configuration
# -------------------------------

# Set working directory inside container
WORKDIR /app    

# Expose Django development server port
EXPOSE 8000                           

# Build-time argument (used to install dev packages)
ARG DEV=false                          

# -------------------------------
# Install dependencies
# -------------------------------
 # Create virtual environment at /py"""
RUN python -m venv /py && \            
    /py/bin/pip install --upgrade pip && \

    # Install PostgreSQL client (needed at runtime)
    apk add --update --no-cache postgresql-client && \

    # Install temporary build dependencies (needed only to build psycopg2)
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \

    # Install production Python dependencies
    /py/bin/pip install -r /tmp/requirements.txt && \

    # If DEV=true, also install development dependencies
    if [ $DEV = "true" ]; then \
        /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \

    # Remove temporary files to keep image small
    rm -rf /tmp && \

    # Remove build-only packages
    apk del .tmp-build-deps && \

    # Create non-root user for security
    adduser --disabled-password --no-create-home django-user

# Add virtual environment binaries to PATH
# (so "python" and "pip" work normally)
ENV PATH="/py/bin:$PATH"       

# -------------------------------
# Security
# -------------------------------

# Run container as non-root user
USER django-user                       
