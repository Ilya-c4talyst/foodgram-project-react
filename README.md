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
'''
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

SECRET_KEY =''
DEBUG='False'
ALLOWED_HOSTS ='127.0.0.1,localhost,backend'
'''