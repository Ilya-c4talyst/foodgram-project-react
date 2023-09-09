# Foodgram
Foodgram - продуктовый помощник. Сайт, который поможет вам с поиском любимых/интересных рецептов, а также облегчит вам жизнь при планировке походов за продуктами в магазин.

https://foodgram-store.ddns.net/ - ссылка на сайт.

## Технологии
- Python
- Django
- Rest framework
- Postgresql
- Docker

## Как развернуть проект
Чтобы развернуть проект на сервере, вам необходимо:

Создать файл .env и наполнить его следующими данными(пример)

```plaintext
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
SECRET_KEY =''
DEBUG='False'
ALLOWED_HOSTS ='127.0.0.1,localhost,backend'
```

Перенести файлы из директории infra.

Запустите Docker Compose с этой конфигурацией на своём компьютере.
Выполните миграции.

```plaintext
docker compose -f docker-compose.production.yml up
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

## Загрузка данных из файла с ингредиентами

Для загрузки в базу данных ингредиентов выполните следующую команду

```plaintext
sudo docker compose docker-compose.production.yml exec backend python manage.py ingr_csv
```

## Документация и примеры ответов

При запуске на локальном сервере документацию можно получить по адресу:
http://localhost/api/docs/redoc.html

В этой документации предложены все возможные варианты запросов и примеры ответов на них.

## Контакты
Разработчик(backend) - Савченко Илья

email - c4talyst12@yandex.ru

