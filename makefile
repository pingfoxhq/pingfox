# Makefile

build:
	docker-compose build

up:
	docker-compose up --build

down:
	docker-compose down -v

migrate:
	docker-compose exec server python manage.py migrate

makemigrations:
	docker-compose exec server python manage.py makemigrations

createsuperuser:
	docker-compose exec server python manage.py createsuperuser

shell:
	docker-compose exec server python manage.py shell

build-css:
	docker-compose exec server npm run build-css

watch-css:
	docker-compose exec server npm run watch-css

collectstatic:
	docker-compose exec server python manage.py collectstatic --noinput

dev:
	docker compose -f compose.dev.yaml watch
