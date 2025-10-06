# Development Dockerfile for Django
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN python -m venv .venv

RUN .venv/bin/pip install --upgrade pip && .venv/bin/pip install -r requirements.txt

COPY . .

CMD [".venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]
