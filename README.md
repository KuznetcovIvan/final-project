## Система управления и контроля бизнеса
### Веб-сервис на FastAPI для управления командной работой компании. 
---
## Реализовано:
- Управление пользователями, компаниями, отделами
- Приглашение в компанию по инвайт-коду
- Встречи проводимые в компании
- Задачи сотрудникам компании, комментарии к задачам
- Календарь мероприятий (день, месяц, год) для каждого сотрудника
- Кабинет администратора
---
## Установка и запуск
1. Клонировать репозиторий `https://github.com/KuznetcovIvan/final-project.git`
2. Перейти в корневую директорию проекта `cd final-project`
3. Создать файл с переменными окружения (`.env`)
- образец в [`.env.example`](.env.example)
- для автоматической миграции БД и создания суперпользователя указать параметры:
  - `RUN_FIRST_MIGRATION`
  - `FIRST_SUPERUSER_EMAIL`
  - `FIRST_SUPERUSER_PASSWORD` 
### Для запуска через Docker:
4. Находясь в корневой директории приложения, выполнить команду  `docker-compose up`
### Для локального запуска:
4. Установить менеджер пакетов UV `pip install uv`
5. Синхронизировать зависимости `uv sync`
6. Запустить приложение `uv run uvicorn app.main:app`
### Приложение запустится на [http://localhost:8000/](http://localhost:8000/)
### Документация будет доступна на:
- Swagger: [http://localhost:8000/docs/](http://localhost:8000/docs/)
- ReDoc:   [http://localhost:8000/redoc/](http://localhost:8000/redoc/)
---
## Стек приложения
- Python 3.11
- FastAPI
- SQLAlchemy 2.0 + asyncpg
- PostgreSQL
- Alembic (async migrations)
- Uvicorn / Gunicorn
- Starlette Admin
- APScheduler
## Возможные проблемы
1. При занятом 8000 порте, укажите любой свободный в файле [`docker-compose.yml`](docker-compose.yml)

``` bash
gateway:
    build: ./nginx/
    env_file: .env
    ports:
      - 8000:80 <----Тут!
    volumes:
      - ./docs/:/usr/share/nginx/html/api/docs/
    depends_on:
      - backend
```

2. Если в `.env` не указать параметр `RUN_FIRST_MIGRATION` то перед первым запуском приложения потребуется применение миграций:
  - для локального запуска, перед первым запуском приложения, выполните `uv run alembic upgrade head`
  - перед первым запуском в контейнере нужно:
    - также убрать из `.env` параметры `FIRST_SUPERUSER_EMAIL` и `FIRST_SUPERUSER_PASSWORD`
    - запустить контейнер `docker-compose up`
    - выполнить миграции  `docker-compose exec backend alembic upgrade head`
    - остановить контейнер (`Ctrl + C` или `docker-compose stop`)
    - при необходимости прописать в `.env` параметры `FIRST_SUPERUSER_EMAIL` и `FIRST_SUPERUSER_PASSWORD` для создания первого суперпользователя.
    - повторно запустить контейнер `docker-compose up`
### Автор
**Kuznetcov Ivan**  
GitHub: [https://github.com/KuznetcovIvan](https://github.com/KuznetcovIvan)