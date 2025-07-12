# Makefile

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
	docker-compose exec server npm run build-css  # Adjust this if you're using Tailwind CLI

collectstatic:
	docker-compose exec server python manage.py collectstatic --noinput
