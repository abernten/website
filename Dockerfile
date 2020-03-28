FROM python:3.8.2-alpine3.11

COPY . /usr/src/app
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add alpine-sdk mariadb-dev

RUN pip install --upgrade pip

RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
RUN pip install gunicorn

RUN chmod +x /usr/src/app/docker-run.sh

EXPOSE 8000

CMD ["./docker-run.sh"]
