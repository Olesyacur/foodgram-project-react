# **FOODGRAM**
[![foodgram-project-react workflow](https://github.com/Olesyacur/foodgram-project-react/actions/workflows/workflow.yml/badge.svg)](https://github.com/Olesyacur/foodgram-project-react/actions/workflows/workflow.yml)
### Продуктовый помощник с базой кулинарных рецептов.
 Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

В данном приложении:

- Публикуем свои рецепты
- Оформляем подписки на других авторов рецептов
- Сохраняем любимые рецепты в избранном
- Формируем список покупок для выбранных рецептов
- Можно выбирать рецепты на основании тегов, таких как: Завтрак, Обед, Ужин.

### Используемые технологии

- [Python 3.7 ](https://www.python.org/downloads/release/python-379/)
- [Django REST framework 3.12](https://www.django-rest-framework.org/community/3.12-announcement/)
- [Simple JWT-аутентификация с реализацией через код подтверждения](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
- [Docker](https://docs.docker.com/engine/reference/builder/#from)
- [Gunicorn](https://docs.gunicorn.org/en/stable/)
- [nginx](https://nginx.org/en/docs/)
- [PostgreSQL](https://postgrespro.ru/docs/postgresql/12/)
- [GIT](https://git-scm.com/docs/git)
- ВМ на Яндекс.Облако

### Установка
Для развертывания проекта используется виртуальная среда Docker и
Docker-compose. Docker "упаковывает" приложение и все его зависимости в
контейнер и может быть перенесен при использовании на месте ОС Linux. Docker-compose это инструмент для запуска многоконтейнерных приложений.

#### Клонируем и разворачиваем репозиторий
```git clone git@github.com:Olesyacur/infra_sp2.git```

#### Устанавливаем соединение с сервером по протоколу ssh:
```ssh username@server_address```
username - имя пользователя, под которым будет выполнено подключение к серверу;
server_address - IP-адрес сервера или доменное имя.

#### Устанавливаем Docker на сервер:
```apt install docker.io```

#### Устанавливаем docker-compose на сервер:
загружаем версию 1.26.0 и сохраняем исполняемый файл в каталоге
/usr/local/bin/docker-compose, в результате чего данное программное
обеспечение будет глобально доступно под именем docker-compose:
```sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose```

задаем правильные разрешения, чтобы сделать команду docker-compose исполняемой:
```sudo chmod +x /usr/local/bin/docker-compose```

#### Редактируем файл infra/nginx.conf на локальном компьютере:
 в строке server_name вписать IP-адрес сервера

#### Копируем файлы docker-compose.yaml и nginx/default.conf из директории infra на сервер:
 ```scp docker-compose.yaml <username>@<host>:/home/<username>/docker-compose.yaml```
```scp nginx <username>@<host>:/home/<username>/nginx```
#### Добавляем переменные окружения в Secrets GitHub для работы с .env:
-DB_ENGINE=django.db.backends.postgresql
-DB_NAME= postgres
-POSTGRES_USER= postgres
-POSTGRES_PASSWORD= 2741001
-DB_HOST= db
-DB_PORT= 5432

#### Добавляем переменные окружения в Secrets GitHub для работы с workflow:
-DOCKER_PASSWORD=<пароль от DockerHub>
-DOCKER_USERNAME=<имя пользователя>

-USER=<username для подключения к серверу>
-HOST=<IP сервера>
-PASSPHRASE=<пароль для сервера, если он установлен>
-SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

-TELEGRAM_TO=<ID чата, в который придет сообщение>
-TELEGRAM_TOKEN=<токен вашего бота>

В workflow четыре задачи:
 1) проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8) и запуск pytest из репозитория yamdb_final;
 2) сборка и доставка докер-образа для контейнера web на Docker Hub;
 3) автоматический деплой проекта на боевой сервер;
 4)отправка уведомления в Telegram о том, что процесс деплоя успешно завершился.

#### Устанавливаем соединение с удаленным сервером:
```
ssh username@server_address
```

#### Запускаем приложение в контейнерах
- Получим список работающих контейнеров:
```sudo docker container ls```
- Выполняем вход в контейнер:
```sudo docker exec -it <id container> bash```
- Выполняем миграции
```python manage.py migrate```
- Создаем суперпользователя
```python manage.py createsuperuser```
- Собираем статику со всего проекта
``` python manage.py collectstatic --no-input```
#### Для заполнения тестовыми данными можно выполнить команду из директории api_yamdb 
```python manage.py loaddata fixtures.json```

Теперь проект доступен по адресу http:/51.250.14.59/admin. Можно войти под
логином и паролем суперпользователя и наполнять базу данных.

#### Другие возможности
Для создания дампа данных из БД
```docker-compose exec web python manage.py dumpdata > dump.json```
Просмотр запущенных контейнеров
```docker stats```
Остановка и удаление контейнеров, томов, образов
```docker-compose down -v```


### Примеры запросов и результат
```
GET http://127.0.0.1:8000/api/recipes/
{
"count": 123,
"next": "http://foodgram.example.org/api/recipes/?page=4",
"previous": "http://foodgram.example.org/api/recipes/?page=2",
"results": [
{
"id": 0,
"tags": [],
"author": {},
"ingredients": [],
"is_favorited": true,
"is_in_shopping_cart": true,
"name": "string",
"image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
"text": "string",
"cooking_time": 1
}
]
}

POST http://127.0.0.1:8000/api/recipes/{id}/favorite/
{
"id": 0,
"name": "string",
"image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
"cooking_time": 1
}

### Автор
Студент Я.Практикум - _Олеся Чурсина_
