FROM python:3.9-alpine3.13
LABEL maintainer="sadykovIsmail"

# Prevent Python from buffering stdout/stderr so logs appear immediately
ENV PYTHONUNBUFFERED=1

# ── Copy dependency manifests ────────────────────────────────────────────────
COPY ./requirements.txt     /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# ── Copy application source ──────────────────────────────────────────────────
COPY ./app /app

# ── Working directory & port ─────────────────────────────────────────────────
WORKDIR /app
EXPOSE 8000

# ── Build argument: set DEV=true in docker-compose to install dev packages ───
ARG DEV=false

# ── Install system deps + Python packages ────────────────────────────────────
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    \
    # Runtime system libraries
    apk add --update --no-cache \
        postgresql-client \
        jpeg-dev && \
    \
    # Temporary build libraries (removed at the end to keep image lean)
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base \
        postgresql-dev \
        musl-dev \
        zlib \
        zlib-dev && \
    \
    /py/bin/pip install -r /tmp/requirements.txt && \
    \
    # Install dev extras only when DEV=true
    if [ "$DEV" = "true" ]; then \
        /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    \
    # Clean up to reduce final image size
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    \
    # Create non-root user (security best practice)
    adduser --disabled-password --no-create-home django-user && \
    \
    # Create volume directories and grant write permission to our user
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

# Put virtualenv binaries first on PATH
ENV PATH="/py/bin:$PATH"

# Drop privileges — never run containers as root
USER django-user
