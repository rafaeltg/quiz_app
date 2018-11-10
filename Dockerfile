FROM python:3.6-slim

WORKDIR /code

ADD requirements.txt /code/

RUN apt-get update && \
    apt-get install -y --no-install-recommends gettext

RUN pip install --no-cache-dir pip -U && \
    pip install --no-cache-dir -r requirements.txt -U

ADD . /code/