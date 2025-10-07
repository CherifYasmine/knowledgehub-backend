# Makefile for development workflow

.PHONY: up down build prune shell migrate makemigrations test lint

up:
	docker-compose up

stop:
	docker-compose stop

down:
	docker-compose down --volumes --remove-orphans

build:
	docker-compose build

prune:
	docker system prune -af

shell:
	docker-compose exec web sh

migrate:
	docker-compose exec web .venv/bin/python manage.py migrate

makemigrations:
	docker-compose exec web .venv/bin/python manage.py makemigrations

test:
	docker-compose exec web .venv/bin/python manage.py test

lint:
	pre-commit run --all-files

restart-web:
	docker-compose restart web

rebuild-web:
	docker-compose build web

up-web:
	docker-compose up web

dependencies-up:
	docker-compose up -d db redis