FROM python:3.6-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

ADD requirements.txt /code/

RUN apt-get update && \
    apt-get install -y --no-install-recommends gettext

RUN pip install pip -U && \
    pip install --no-cache-dir -r requirements.txt -U

ADD . /code/