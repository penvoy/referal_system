FROM python:3.11-alpine
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Сделаем первую миграцию.
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
