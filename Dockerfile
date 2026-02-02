# Use Python 3.9 Alpine (small image)
FROM python:3.9-alpine3.13
LABEL maintainer="recipe-app"
 # no Python buffering
ENV PYTHONUNBUFFERED=1                

# Copy requirements & app code
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app

 # working directory inside container
WORKDIR /app    
 # Django port                      
EXPOSE 8000                           
 # build argument for dev packages
ARG DEV=false                          
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt ; fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser --disabled-password --no-create-home django-user
 # add virtual env to PATH
ENV PATH="/py/bin:$PATH"       
# run container as non-root user

USER django-user                       