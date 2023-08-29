setup:
	docker-compose exec web python manage.py makemigrations
	docker-compose exec web python manage.py migrate
	docker-compose exec web python manage.py collectstatic --no-input

admin:
	docker-compose exec web python manage.py createsuperuser

load_data:
	docker-compose exec web bash -c "cd sqlite_to_postgres && python load_data.py"