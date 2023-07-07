FROM python:3.11.4-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/src/app

COPY requirements.txt ./

COPY ./model/. ./model

RUN pip install --no-cache-dir -r requirements.txt

COPY gptTest.py ./
COPY docker.py ./

CMD [ "python", "./docker.py" ]