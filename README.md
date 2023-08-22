# Социальная сеть

Социальная сеть для публикации личных дневников. 



## Оглавление:
- [Технологии](#технологии)
- [Описание работы](#описание-работы)
- [Установка и запуск](#установка-и-запуск)
- [Удаление](#удаление)
- [Автор](#автор)



## Технологии:
<details><summary>Развернуть</summary>

**Языки программирования, библиотеки и модули:**

[![Python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue?logo=python)](https://www.python.org/)
[![Requests](https://img.shields.io/badge/-Requests:_HTTP_for_Humans™-464646?logo=Python)](https://pypi.org/project/requests/)
[![Pillow](https://img.shields.io/badge/-Pillow-464646?logo=Python)](https://pypi.org/project/Pillow/)

[![HTML](https://img.shields.io/badge/-HTML-464646?logo=HTML)](https://html.spec.whatwg.org/multipage/)


**Фреймворк, расширения и библиотеки:**

[![Django](https://img.shields.io/badge/-Django-464646?logo=Django)](https://www.djangoproject.com/)
[![sorl-thumbnail](https://img.shields.io/badge/-sorl--thumbnail-464646?logo=sorl-thumbnail)](https://sorl-thumbnail.readthedocs.io/en/latest/)


**База данных:**

[![SQLite3](https://img.shields.io/badge/-SQLite3-464646?logo=SQLite)](https://www.sqlite.com/version3.html)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?logo=PostgreSQL)](https://www.postgresql.org/)



**Тестирование:**

[![Pytest](https://img.shields.io/badge/-Pytest-464646?logo=Pytest)](https://docs.pytest.org/en/latest/)
[![Pytest-cov](https://img.shields.io/badge/-Pytest--cov-464646?logo=Pytest)](https://pytest-cov.readthedocs.io/en/latest/)
[![Coverage](https://img.shields.io/badge/-Coverage-464646?logo=Python)](https://coverage.readthedocs.io/en/latest/)



[⬆️Оглавление](#оглавление)
</details>



## Описание работы:
- Социальная сеть для публикации личных дневников. Это сайт, на котором можно создать свою страницу.
  - После регистрации пользователь получает свой профайл, то есть получает свою страницу
- Если на нее зайти, то можно посмотреть все записи автора.
  - После публикации каждая запись доступна на странице автора.
- Пользователи могут заходить на чужие страницы, подписываться на авторов и комментировать их записи.
- Автор может выбрать для своей страницы имя и уникальный адрес.
  - Эта часть реализована в момент регистрации. Мы не добавляли возможность изменять свой username: если бы сайт уже был в сети, то при смене имени пользователя старые ссылки на уже опубликованные записи перестали бы работать.
- Есть возможность модерировать записи и блокировать пользователей, если начнут присылать спам.
  - Эту часть мы получили вместе с интерфейсом администратора. Будем банить спамеров через админку.
- Записи можно отправить в сообщество и посмотреть там записи разных авторов.

[⬆️Оглавление](#оглавление)


## Для локального запуска:
1. Клонируйте репозиторий:
```
git clone git@github.com:PavelPrist/hw05_final.git
```
2. Создайте и активируйте виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```
3. Установите зависимости:
```
pip install -r requirements.txt
```
4. В директории yatube выполните команду:
```
python manage.py runserver
```
5. Проект запущен по адресу http://127.0.0.1:8000/

6. Выполните миграции, создайте суперюзера (потребуется ввод персональных данных) и запустите приложение:
```bash
cd yatube && \
python manage.py makemigrations && \
python manage.py migrate && \
python manage.py prepare_load_data && \
python manage.py loaddata dump.json && \
python manage.py createsuperuser && \
python manage.py runserver && cd ..
```


7. Остановить сервер Django можно комбинацией клавиш Ctl-C.
<hr></details>



## Автор:
[Павел Сердюков](https://github.com/PavelPrist/)

[⬆️В начало](#социальная-сеть)