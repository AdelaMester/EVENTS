FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

RUN export FLASK_ENV=development

RUN export FLASK_APP=application.py

RUN flask run --host=0.0.0.0