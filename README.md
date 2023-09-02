# Сервисы Admin Panel + ETL

Панель администратора для онлайн-кинотеатра.
## В проект входит
- GUI для работы с хранилищем
- Перенос данных из SQLite в Postgres
- API, позволяющий получить информацию об фильмах.
- Перенос данных из Postgres в ElasticSearch. 
- Инфраструктура для полнотекстового поиска

## Технологии
- [Python](https://www.python.org/) - is an interpreted high-level general-purpose programming language.
- [Django Framework](https://www.djangoproject.com/) - is a high-level Python Web framework that encourages rapid development and clean, pragmatic design.
- [PostgeSQL](https://www.postgresql.org/) - is an open source object-relational database system that uses and extends the SQL language combined with many features.
- [Docker](https://www.docker.com/) - is a set of platform as a service (PaaS) products that use OS-level virtualization to deliver software in packages (containers).
- [Gunicorn](https://gunicorn.org/) - is a Python WSGI HTTP Server for UNIX.
- [Nginx](https://nginx.org/) - is a web server that can also be used as a reverse proxy, load balancer, mail proxy and HTTP cache.
- [Elasticsearch](https://www.elastic.co/elasticsearch/) - is the distributed, RESTful search and analytics engine at the heart of the Elastic Stack. You can use Elasticsearch to store, search, and manage data.

## Как развернуть проект
- скачать репозиторий, перейти в директорию с ```docker-compose.yml```

- заполнить переменные среды в ```app/config/.env```

- заполнить переменные среды в ```postgres_to_es/.env```

- собрать и запустить докер-сборку

```docker-compose up -d --build```

```docker-compose up```

- перейти в панель администратора http://localhost:8000/admin