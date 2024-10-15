# API для реферальной системы

простой RESTful API сервис для реферальной системы

## Инструкция по запуску

1. Клонируйте репозиторий.
2. Запустите контейнеры с помощью команды 
    ```bash
    docker compose -f "docker-compose.yml" up -d --build 
    ```
3. Чтобы запустить тесты, выполните команду чтобы зайти в контейнер
    ```bash
    docker exec -it server /bin/sh 
    ```
    затем 
    ```python
    python manage.py test 
    ```
4. API доступно по адресу [http://127.0.0.1:8000](http://127.0.0.1:8000)

## API запросы

- **GET /swagger/** - Можно посмотреть все endpoints в Swagger UI 