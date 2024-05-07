# Stage 1: Install system dependencies, install poetry, and install project dependencies
FROM python:3.12 

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/